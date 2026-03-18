from __future__ import annotations

import pytest

from src.core.model_manifest import manifest_from_dict


def _valid_manifest() -> dict[str, object]:
    return {
        "model_id": "default-v1",
        "model_path": "models/default/default.onnx",
        "stateful": True,
        "lookahead_ms": 0,
        "frames_per_inference": 4,
        "input_tensor": {
            "name": "audio_in",
            "shape": [1, 1, 960],
            "dtype": "float32",
        },
        "output_tensor": {
            "name": "audio_out",
            "shape": [1, 1, 960],
            "dtype": "float32",
        },
        "state_tensor_mode": "explicit_state_tensors",
    }


def test_manifest_accepts_v1_contract_shape() -> None:
    manifest = manifest_from_dict(_valid_manifest())
    assert manifest.frames_per_inference == 4


def test_manifest_rejects_positive_lookahead() -> None:
    raw = _valid_manifest()
    raw["lookahead_ms"] = 20
    with pytest.raises(ValueError):
        manifest_from_dict(raw)


def test_manifest_rejects_wrong_tensor_shape() -> None:
    raw = _valid_manifest()
    raw["input_tensor"] = {"name": "audio_in", "shape": [1, 1, 480], "dtype": "float32"}
    with pytest.raises(ValueError):
        manifest_from_dict(raw)


def test_manifest_rejects_non_stateful_mode() -> None:
    raw = _valid_manifest()
    raw["stateful"] = False
    with pytest.raises(ValueError):
        manifest_from_dict(raw)
