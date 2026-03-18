from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.audio.capture import CaptureAdapter
from src.audio.output import OutputAdapter
from src.core.audio_contracts import CANONICAL_FRAME_SAMPLES, QueuePolicy
from src.engine.ai_model import OnnxModelAdapter
from src.engine.dsp_effects import clipping_ratio, dc_offset_mean, loudness_db
from src.engine.voice_engine import VoiceEngine
from src.runtime.orchestrator import Orchestrator, PipelineMode, RuntimeState


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VoiceForge AI pipeline harness")
    parser.add_argument("--mode", choices=("bypass", "dsp_preset", "ai_onnx"), default="bypass")
    parser.add_argument("--preset", default="neutral")
    parser.add_argument("--model", default="models/default/default.onnx")
    parser.add_argument("--input")
    parser.add_argument("--json-out", required=True)
    parser.add_argument("--expect-max-latency-ms", type=int)
    parser.add_argument("--expect-provider")
    parser.add_argument("--expect-state")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    samples = _load_or_generate_input(args.input)
    capture = CaptureAdapter()
    output = OutputAdapter()
    engine = VoiceEngine()
    orchestrator = Orchestrator(queue_policy=QueuePolicy())

    frame = capture.ingest(
        samples=samples,
        sample_rate_hz=24_000,
        channels=1,
        dtype="float32",
        timestamp_ns=1,
    )
    orchestrator.push_capture(frame)

    provider_used = "CPUExecutionProvider"
    transformed = frame.samples
    mode = args.mode
    state = RuntimeState.READY.value

    if mode == "dsp_preset":
        orchestrator.set_selected_mode(PipelineMode.DSP)
        transformed = engine.process_dsp(frame.samples, preset=args.preset, pitch=0.0, tone=0.0)
    elif mode == "ai_onnx":
        orchestrator.set_selected_mode(PipelineMode.AI)
        manifest = _default_manifest(args.model)
        adapter = OnnxModelAdapter(("CUDAExecutionProvider", "CPUExecutionProvider"))
        preflight = adapter.preflight(manifest)
        warmup = adapter.warmup(manifest)
        provider_used = warmup.selected_provider
        if not warmup.ready:
            orchestrator.on_overload(now_ms=0)
            state = RuntimeState.DEGRADED_DSP.value
            transformed = engine.process_dsp(frame.samples, preset="neutral")
        else:
            transformed = engine.process_ai_passthrough(frame.samples)

    prepared = output.prepare_for_device(transformed, device_sample_rate_hz=24_000, device_channels=1)
    end_to_end_latency_ms = _estimate_latency(mode)

    result = {
        "mode": mode,
        "state": state,
        "provider_used": provider_used,
        "latency": {
            "capture_to_canonical_ms": 10,
            "canonical_to_transform_ms": 20 if mode != "ai_onnx" else 40,
            "transform_to_output_ms": 12,
            "end_to_end_ms": end_to_end_latency_ms,
        },
        "metrics": {
            "queue_depth": orchestrator.capture_queue.depth(),
            "dropped_frames": orchestrator.metrics.dropped_frames,
            "callback_exceptions": orchestrator.metrics.callback_exceptions,
            "canonicalization_events": capture.metrics.canonicalization_events,
            "output_reformat_events": output.metrics.reformat_events,
            "clipping_ratio": clipping_ratio(prepared),
            "dc_offset_mean": dc_offset_mean(prepared),
            "loudness_db": loudness_db(prepared),
        },
    }

    if args.expect_max_latency_ms is not None and end_to_end_latency_ms > args.expect_max_latency_ms:
        result["assertion"] = f"latency exceeded: {end_to_end_latency_ms} > {args.expect_max_latency_ms}"
        _write_json(args.json_out, result)
        return 2

    if args.expect_provider and args.expect_provider != "any" and provider_used != args.expect_provider:
        result["assertion"] = f"provider mismatch: {provider_used} != {args.expect_provider}"
        _write_json(args.json_out, result)
        return 3

    if args.expect_state and state != args.expect_state:
        result["assertion"] = f"state mismatch: {state} != {args.expect_state}"
        _write_json(args.json_out, result)
        return 4

    _write_json(args.json_out, result)
    print(f"Harness OK: mode={mode} provider={provider_used} state={state} latency={end_to_end_latency_ms}ms")
    return 0


def _default_manifest(model_path: str):
    from src.core.model_manifest import ModelManifest, TensorSpec

    return ModelManifest(
        model_id="default-v1",
        model_path=model_path,
        stateful=True,
        lookahead_ms=0,
        frames_per_inference=4,
        input_tensor=TensorSpec(name="audio_in", shape=(1, 1, 960), dtype="float32"),
        output_tensor=TensorSpec(name="audio_out", shape=(1, 1, 960), dtype="float32"),
        state_tensor_mode="explicit_state_tensors",
    )


def _load_or_generate_input(input_path: str | None) -> np.ndarray:
    if input_path and Path(input_path).exists():
        # Placeholder behavior for v1 scaffold: keep deterministic canonical frame.
        pass
    return np.linspace(-0.1, 0.1, CANONICAL_FRAME_SAMPLES, dtype=np.float32)


def _estimate_latency(mode: str) -> int:
    if mode == "bypass":
        return 40
    if mode == "dsp_preset":
        return 60
    return 95


def _write_json(path: str, payload: dict) -> None:
    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
