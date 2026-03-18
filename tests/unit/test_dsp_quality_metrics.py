from __future__ import annotations

import numpy as np

from src.engine.dsp_effects import clipping_ratio, dc_offset_mean, loudness_db


def test_quality_metrics_return_finite_values() -> None:
    samples = np.linspace(-0.2, 0.2, 240, dtype=np.float32)
    assert 0.0 <= clipping_ratio(samples) <= 1.0
    assert abs(dc_offset_mean(samples)) < 0.01
    assert loudness_db(samples) < 0.0
