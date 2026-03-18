from __future__ import annotations

from src.utils.diagnostics import DeveloperDiagnostics, UserDiagnostics, export_diagnostics


def test_metrics_export_contains_user_and_developer_sections() -> None:
    payload = export_diagnostics(
        user=UserDiagnostics(
            mode="dsp",
            input_device="mic",
            output_device="speaker",
            model_state="ready",
            avg_latency_ms=70.0,
            dropped_frames=0,
        ),
        dev=DeveloperDiagnostics(
            queue_depth_peak=2,
            provider_used="CPUExecutionProvider",
            warmup_ms=20,
            resample_count=0,
            fallback_history=["none"],
            callback_timing_p95_ms=10.0,
        ),
    )
    assert set(payload.keys()) == {"user", "developer"}
