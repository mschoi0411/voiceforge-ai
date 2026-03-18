from __future__ import annotations

from src.ui.main_window import MainWindowViewModel


def test_hotkey_toggle_changes_only_overlay_visibility() -> None:
    vm = MainWindowViewModel()
    before = vm.snapshot()
    vm.toggle_overlay_visibility()
    after = vm.snapshot()
    assert before.mode == after.mode
    assert after.overlay_visible is True
