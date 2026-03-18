from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.core.audio_contracts import (
    AudioFrame,
    CANONICAL_FRAME_SAMPLES,
    CANONICAL_SAMPLE_RATE_HZ,
    is_canonical_stream,
    normalize_canonical_frame,
)


@dataclass
class CaptureMetrics:
    canonicalization_events: int = 0
    callback_exceptions: int = 0


class CaptureAdapter:
    def __init__(self) -> None:
        self.metrics = CaptureMetrics()

    def canonicalize(
        self,
        samples: np.ndarray,
        sample_rate_hz: int,
        channels: int,
        dtype: str,
    ) -> np.ndarray:
        if is_canonical_stream(sample_rate_hz, channels, dtype):
            return normalize_canonical_frame(samples)

        self.metrics.canonicalization_events += 1
        working = np.asarray(samples, dtype=np.float32)

        if working.ndim == 2:
            working = working.mean(axis=1)
        elif working.ndim != 1:
            raise ValueError("Unsupported input sample shape.")

        if sample_rate_hz != CANONICAL_SAMPLE_RATE_HZ:
            working = _linear_resample(working, sample_rate_hz, CANONICAL_SAMPLE_RATE_HZ)

        if working.shape[0] < CANONICAL_FRAME_SAMPLES:
            working = np.pad(working, (0, CANONICAL_FRAME_SAMPLES - working.shape[0]))
        elif working.shape[0] > CANONICAL_FRAME_SAMPLES:
            working = working[:CANONICAL_FRAME_SAMPLES]

        return normalize_canonical_frame(working)

    def ingest(
        self,
        samples: np.ndarray,
        sample_rate_hz: int,
        channels: int,
        dtype: str,
        timestamp_ns: int,
    ) -> AudioFrame:
        canonical = self.canonicalize(samples, sample_rate_hz, channels, dtype)
        return AudioFrame(samples=canonical, timestamp_ns=timestamp_ns)


def _linear_resample(samples: np.ndarray, from_hz: int, to_hz: int) -> np.ndarray:
    if from_hz <= 0 or to_hz <= 0:
        raise ValueError("Sample rates must be positive.")
    if from_hz == to_hz:
        return samples.astype(np.float32, copy=False)

    source_len = samples.shape[0]
    target_len = max(1, int(round(source_len * (to_hz / from_hz))))
    source_idx = np.linspace(0.0, 1.0, source_len, endpoint=True)
    target_idx = np.linspace(0.0, 1.0, target_len, endpoint=True)
    resampled = np.interp(target_idx, source_idx, samples)
    return resampled.astype(np.float32)
