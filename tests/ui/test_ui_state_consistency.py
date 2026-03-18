from __future__ import annotations

from src.runtime import RuntimeState
from src.ui.main_window import MainWindowViewModel


def test_ui_uses_runtime_state_for_control_enablement() -> None:
    vm = MainWindowViewModel()
    vm.update_runtime_state(RuntimeState.WARMING)
    assert not vm.snapshot().ai_toggle_enabled
    vm.update_runtime_state(RuntimeState.READY)
    assert vm.snapshot().ai_toggle_enabled
