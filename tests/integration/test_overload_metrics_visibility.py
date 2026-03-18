from __future__ import annotations

from src.runtime import Orchestrator


def test_overload_event_increments_metric_counter() -> None:
    orchestrator = Orchestrator()
    orchestrator.on_overload(now_ms=100)
    assert orchestrator.metrics.overload_events == 1
    assert orchestrator.metrics.fallback_events == 1
