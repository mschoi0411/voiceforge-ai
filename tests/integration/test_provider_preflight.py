from __future__ import annotations

from src.core.model_manifest import ModelManifest, TensorSpec
from src.engine.ai_model import OnnxModelAdapter


def test_provider_preflight_returns_available_and_selected_provider() -> None:
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
    adapter = OnnxModelAdapter(("CUDAExecutionProvider", "CPUExecutionProvider"))
    result = adapter.preflight(manifest)
    assert "CPUExecutionProvider" in result.available_providers
    assert result.selected_provider in result.available_providers
