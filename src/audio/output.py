from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.core.audio_contracts import CANONICAL_SAMPLE_RATE_HZ


@dataclass
class OutputMetrics:
    reformat_events: int = 0


class OutputAdapter:
    def __init__(self) -> None:
        self.metrics = OutputMetrics()

    def prepare_for_device(
        self,
        samples: np.ndarray,
        device_sample_rate_hz: int,
        device_channels: int,
    ) -> np.ndarray:
        working = np.asarray(samples, dtype=np.float32)

        if device_sample_rate_hz != CANONICAL_SAMPLE_RATE_HZ:
            self.metrics.reformat_events += 1
            working = _linear_resample(working, CANONICAL_SAMPLE_RATE_HZ, device_sample_rate_hz)

        if device_channels == 2:
            self.metrics.reformat_events += 1
            working = np.repeat(working[:, None], 2, axis=1)
        elif device_channels != 1:
            raise ValueError("Only mono or stereo output is supported.")

        return working.astype(np.float32)


def _linear_resample(samples: np.ndarray, from_hz: int, to_hz: int) -> np.ndarray:
    if from_hz == to_hz:
        return samples.astype(np.float32, copy=False)
    source_len = samples.shape[0]
    target_len = max(1, int(round(source_len * (to_hz / from_hz))))
    source_idx = np.linspace(0.0, 1.0, source_len, endpoint=True)
    target_idx = np.linspace(0.0, 1.0, target_len, endpoint=True)
    resampled = np.interp(target_idx, source_idx, samples)
    return resampled.astype(np.float32)
