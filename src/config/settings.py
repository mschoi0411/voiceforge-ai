from __future__ import annotations

from dataclasses import dataclass, field

from src.core.audio_contracts import (
    CANONICAL_CHANNELS,
    CANONICAL_FRAME_MS,
    CANONICAL_FRAME_SAMPLES,
    CANONICAL_SAMPLE_RATE_HZ,
    QueuePolicy,
)


@dataclass(frozen=True)
class RuntimeSettings:
    sample_rate_hz: int = CANONICAL_SAMPLE_RATE_HZ
    channels: int = CANONICAL_CHANNELS
    frame_ms: int = CANONICAL_FRAME_MS
    frame_samples: int = CANONICAL_FRAME_SAMPLES
    provider_order: tuple[str, ...] = (
        "CUDAExecutionProvider",
        "CPUExecutionProvider",
    )
    queue_policy: QueuePolicy = field(default_factory=QueuePolicy)
    ai_transform_p95_ms: int = 55
    sustained_lag_windows: int = 2
    sustained_lag_window_seconds: int = 5

    def validate(self) -> None:
        if self.sample_rate_hz != CANONICAL_SAMPLE_RATE_HZ:
            raise ValueError("sample_rate_hz must match canonical sample rate.")
        if self.channels != CANONICAL_CHANNELS:
            raise ValueError("channels must match canonical mono channel count.")
        if self.frame_ms != CANONICAL_FRAME_MS:
            raise ValueError("frame_ms must match canonical frame duration.")
        if self.frame_samples != CANONICAL_FRAME_SAMPLES:
            raise ValueError("frame_samples must match canonical frame sample count.")
        if not self.provider_order:
            raise ValueError("provider_order must not be empty.")
        if self.provider_order[-1] != "CPUExecutionProvider":
            raise ValueError("provider_order must end with CPUExecutionProvider fallback.")
        self.queue_policy.validate()
        if self.ai_transform_p95_ms <= 0:
            raise ValueError("ai_transform_p95_ms must be positive.")


def build_default_settings() -> RuntimeSettings:
    settings = RuntimeSettings()
    settings.validate()
    return settings
