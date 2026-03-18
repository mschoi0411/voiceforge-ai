from __future__ import annotations

import numpy as np
import pytest

from src.engine.dsp_effects import apply_preset


def test_pitch_bounds_are_enforced() -> None:
    samples = np.zeros(240, dtype=np.float32)
    with pytest.raises(ValueError):
        apply_preset(samples, preset_name="robot", pitch=100.0)


def test_tone_bounds_are_enforced() -> None:
    samples = np.zeros(240, dtype=np.float32)
    with pytest.raises(ValueError):
        apply_preset(samples, preset_name="robot", tone=2.0)
