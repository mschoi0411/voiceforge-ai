from __future__ import annotations

from src.ui.main_window import MainWindowViewModel


def test_main_window_defaults_to_overlay_hidden() -> None:
    vm = MainWindowViewModel()
    snapshot = vm.snapshot()
    assert not snapshot.overlay_visible
