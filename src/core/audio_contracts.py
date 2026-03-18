from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np

CANONICAL_SAMPLE_RATE_HZ = 24_000
CANONICAL_CHANNELS = 1
CANONICAL_FRAME_MS = 10
CANONICAL_FRAME_SAMPLES = 240
AI_FRAMES_PER_INFERENCE = 4
AI_WINDOW_SAMPLES = CANONICAL_FRAME_SAMPLES * AI_FRAMES_PER_INFERENCE


@dataclass(frozen=True)
class QueuePolicy:
    capture_max_frames: int = 3
    process_max_frames: int = 3
    output_max_frames: int = 3

    def validate(self) -> None:
        for value in (self.capture_max_frames, self.process_max_frames, self.output_max_frames):
            if value <= 0:
                raise ValueError("Queue limits must be positive integers.")


@dataclass(frozen=True)
class AudioFrame:
    samples: np.ndarray
    timestamp_ns: int

    def __post_init__(self) -> None:
        normalized = normalize_canonical_frame(self.samples)
        object.__setattr__(self, "samples", normalized)
        if self.timestamp_ns < 0:
            raise ValueError("timestamp_ns must be non-negative.")


def normalize_canonical_frame(raw_samples: Iterable[float] | np.ndarray) -> np.ndarray:
    samples = np.asarray(raw_samples, dtype=np.float32)
    if samples.ndim != 1:
        raise ValueError("Canonical frame samples must be 1D mono.")
    if samples.shape[0] != CANONICAL_FRAME_SAMPLES:
        raise ValueError(
            f"Canonical frame requires {CANONICAL_FRAME_SAMPLES} samples, got {samples.shape[0]}."
        )
    return samples


def is_canonical_stream(sample_rate_hz: int, channels: int, dtype: str) -> bool:
    return (
        sample_rate_hz == CANONICAL_SAMPLE_RATE_HZ
        and channels == CANONICAL_CHANNELS
        and dtype == "float32"
    )


def requires_canonicalization(sample_rate_hz: int, channels: int, dtype: str) -> bool:
    return not is_canonical_stream(sample_rate_hz=sample_rate_hz, channels=channels, dtype=dtype)
