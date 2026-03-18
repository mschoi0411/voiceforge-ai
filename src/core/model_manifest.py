from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.audio_contracts import AI_FRAMES_PER_INFERENCE, AI_WINDOW_SAMPLES


@dataclass(frozen=True)
class TensorSpec:
    name: str
    shape: tuple[int, ...]
    dtype: str


@dataclass(frozen=True)
class ModelManifest:
    model_id: str
    model_path: str
    stateful: bool
    lookahead_ms: int
    frames_per_inference: int
    input_tensor: TensorSpec
    output_tensor: TensorSpec
    state_tensor_mode: str

    def validate(self) -> None:
        if not self.model_id.strip():
            raise ValueError("model_id is required.")
        if not self.model_path.strip():
            raise ValueError("model_path is required.")
        if not self.stateful:
            raise ValueError("v1 contract requires a stateful model manifest.")
        if self.lookahead_ms != 0:
            raise ValueError("v1 contract requires zero positive lookahead.")
        if self.frames_per_inference != AI_FRAMES_PER_INFERENCE:
            raise ValueError(
                f"frames_per_inference must be {AI_FRAMES_PER_INFERENCE} for v1."
            )

        expected_shape = (1, 1, AI_WINDOW_SAMPLES)
        if self.input_tensor.shape != expected_shape:
            raise ValueError(f"input_tensor.shape must be {expected_shape}.")
        if self.output_tensor.shape != expected_shape:
            raise ValueError(f"output_tensor.shape must be {expected_shape}.")
        if self.input_tensor.dtype != "float32" or self.output_tensor.dtype != "float32":
            raise ValueError("input/output tensor dtype must be float32.")

        allowed_modes = {"explicit_state_tensors", "rolling_history"}
        if self.state_tensor_mode not in allowed_modes:
            raise ValueError(
                "state_tensor_mode must be one of: explicit_state_tensors, rolling_history."
            )


def manifest_from_dict(raw: dict[str, Any]) -> ModelManifest:
    input_tensor = TensorSpec(
        name=str(raw["input_tensor"]["name"]),
        shape=tuple(int(v) for v in raw["input_tensor"]["shape"]),
        dtype=str(raw["input_tensor"]["dtype"]),
    )
    output_tensor = TensorSpec(
        name=str(raw["output_tensor"]["name"]),
        shape=tuple(int(v) for v in raw["output_tensor"]["shape"]),
        dtype=str(raw["output_tensor"]["dtype"]),
    )
    manifest = ModelManifest(
        model_id=str(raw["model_id"]),
        model_path=str(raw["model_path"]),
        stateful=bool(raw["stateful"]),
        lookahead_ms=int(raw["lookahead_ms"]),
        frames_per_inference=int(raw["frames_per_inference"]),
        input_tensor=input_tensor,
        output_tensor=output_tensor,
        state_tensor_mode=str(raw["state_tensor_mode"]),
    )
    manifest.validate()
    return manifest
