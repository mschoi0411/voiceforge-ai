from __future__ import annotations

from src.runtime import Orchestrator, RuntimeState


def test_device_loss_transitions_to_safe_state() -> None:
    orchestrator = Orchestrator()
    orchestrator.mark_device_lost()
    assert orchestrator.state == RuntimeState.DEVICE_LOST
