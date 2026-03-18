from __future__ import annotations

from src.core.model_manifest import ModelManifest, TensorSpec


def test_model_manifest_contains_expected_default_tensor_names() -> None:
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
    manifest.validate()
    assert manifest.input_tensor.name == "audio_in"
    assert manifest.output_tensor.name == "audio_out"
