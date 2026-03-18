from __future__ import annotations

from src.runtime import Orchestrator, PipelineMode, RuntimeState


def test_state_machine_happy_path_mode_switch() -> None:
    orchestrator = Orchestrator()
    orchestrator.mark_ready()
    orchestrator.set_selected_mode(PipelineMode.DSP)
    assert orchestrator.mode == PipelineMode.DSP
    orchestrator.set_selected_mode(PipelineMode.BYPASS)
    assert orchestrator.mode == PipelineMode.BYPASS
    assert orchestrator.state == RuntimeState.READY
