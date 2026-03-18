from __future__ import annotations

from src.core.model_manifest import ModelManifest, TensorSpec
from src.engine.ai_model import OnnxModelAdapter


def test_provider_falls_back_to_cpu_when_unknown_provider_requested() -> None:
    manifest = ModelManifest(
        model_id="default-v1",
        model_path="models/default/default.onnx",
        stateful=True,
        lookahead_ms=0,
        frames_per_inference=4,
        input_tensor=TensorSpec(name="audio_in", shape=(1, 1, 960), dtype="float32"),
        output_tensor=TensorSpec(name="audio_out", shape=(1, 1, 960), dtype="float32"),
        state_tensor_mode="explicit_state_tensors",
    )
    adapter = OnnxModelAdapter(("UnknownProvider", "CPUExecutionProvider"))
    result = adapter.preflight(manifest)
    assert result.selected_provider == "CPUExecutionProvider"
