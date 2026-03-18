from __future__ import annotations

from src.core.model_manifest import ModelManifest, TensorSpec
from src.engine.ai_model import OnnxModelAdapter


def _manifest() -> ModelManifest:
    return ModelManifest(
        model_id="default-v1",
        model_path="models/default/default.onnx",
        stateful=True,
        lookahead_ms=0,
        frames_per_inference=4,
        input_tensor=TensorSpec(name="audio_in", shape=(1, 1, 960), dtype="float32"),
        output_tensor=TensorSpec(name="audio_out", shape=(1, 1, 960), dtype="float32"),
        state_tensor_mode="explicit_state_tensors",
    )


def test_warmup_transitions_ready() -> None:
    adapter = OnnxModelAdapter(("CUDAExecutionProvider", "CPUExecutionProvider"))
    warmup = adapter.warmup(_manifest())
    assert warmup.ready
    assert adapter.ready
