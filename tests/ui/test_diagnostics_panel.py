from __future__ import annotations

from src.utils.diagnostics import DeveloperDiagnostics, UserDiagnostics, export_diagnostics


def test_diagnostics_payload_contains_summary_fields() -> None:
    payload = export_diagnostics(
        UserDiagnostics("dsp", "mic", "speaker", "ready", 42.0, 0),
        DeveloperDiagnostics(2, "CPUExecutionProvider", 20, 0, [], 11.0),
    )
    assert "avg_latency_ms" in payload["user"]
    assert "queue_depth_peak" in payload["developer"]
