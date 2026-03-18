from __future__ import annotations

from src.runtime import RuntimeState
from src.ui.main_window import MainWindowViewModel


def test_provider_failure_state_disables_ai_toggle_and_shows_reason() -> None:
    vm = MainWindowViewModel()
    vm.update_runtime_state(RuntimeState.DEGRADED_DSP, reason="provider failure")
    snap = vm.snapshot()
    assert not snap.ai_toggle_enabled
    assert "fallback" in snap.status_message.lower()
