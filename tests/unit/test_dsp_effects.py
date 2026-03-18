from __future__ import annotations

import numpy as np

from src.engine.dsp_effects import apply_preset


def test_apply_preset_returns_float32_same_shape() -> None:
    samples = np.linspace(-0.2, 0.2, 240, dtype=np.float32)
    out = apply_preset(samples, preset_name="deep_voice")
    assert out.dtype == np.float32
    assert out.shape == samples.shape
