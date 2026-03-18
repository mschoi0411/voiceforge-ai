from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UserDiagnostics:
    mode: str
    input_device: str
    output_device: str
    model_state: str
    avg_latency_ms: float
    dropped_frames: int


@dataclass
class DeveloperDiagnostics:
    queue_depth_peak: int
    provider_used: str
    warmup_ms: int
    resample_count: int
    fallback_history: list[str]
    callback_timing_p95_ms: float


def export_diagnostics(user: UserDiagnostics, dev: DeveloperDiagnostics) -> dict:
    return {
        "user": {
            "mode": user.mode,
            "input_device": user.input_device,
            "output_device": user.output_device,
            "model_state": user.model_state,
            "avg_latency_ms": user.avg_latency_ms,
            "dropped_frames": user.dropped_frames,
        },
        "developer": {
            "queue_depth_peak": dev.queue_depth_peak,
            "provider_used": dev.provider_used,
            "warmup_ms": dev.warmup_ms,
            "resample_count": dev.resample_count,
            "fallback_history": dev.fallback_history,
            "callback_timing_p95_ms": dev.callback_timing_p95_ms,
        },
    }
