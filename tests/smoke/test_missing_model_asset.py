from __future__ import annotations

from pathlib import Path


def test_missing_model_asset_path_is_detectable() -> None:
    missing = Path("models/default/default.onnx")
    assert not missing.exists()
