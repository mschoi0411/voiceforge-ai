from __future__ import annotations

from src.runtime import Orchestrator, PipelineMode


def test_rapid_mode_switch_does_not_flap_without_recovery_conditions() -> None:
    orchestrator = Orchestrator()
    orchestrator.set_selected_mode(PipelineMode.AI)
    orchestrator.on_overload(now_ms=0)
    recovered = orchestrator.maybe_recover_ai(
        now_ms=100,
        queue_depth=2,
        preflight_ok=True,
        callback_ok=True,
    )
    assert not recovered
