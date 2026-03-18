from __future__ import annotations

from src.utils.diagnostics import DeveloperDiagnostics, UserDiagnostics, export_diagnostics


def test_diagnostics_split_user_and_developer_audiences() -> None:
    payload = export_diagnostics(
        UserDiagnostics("ai", "mic", "speaker", "ready", 80.0, 1),
        DeveloperDiagnostics(3, "CPUExecutionProvider", 30, 2, ["fallback:dsp"], 18.0),
    )
    assert "provider_used" not in payload["user"]
    assert "provider_used" in payload["developer"]
