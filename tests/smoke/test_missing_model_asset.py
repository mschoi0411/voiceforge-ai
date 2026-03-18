from __future__ import annotations

from pathlib import Path


def test_default_model_asset_is_bundled_locally() -> None:
    bundled = Path("models/default/default.onnx")
    assert bundled.exists()
