from __future__ import annotations

import numpy as np

from src.core.audio_contracts import AudioFrame, CANONICAL_FRAME_SAMPLES
from src.runtime import Orchestrator, PipelineMode, RuntimeState


def test_overload_falls_back_to_dsp_and_marks_degraded() -> None:
    orchestrator = Orchestrator()
    for idx in range(10):
        frame = AudioFrame(samples=np.zeros(CANONICAL_FRAME_SAMPLES, dtype=np.float32), timestamp_ns=idx)
        orchestrator.push_capture(frame)
    orchestrator.on_overload(now_ms=10)
    assert orchestrator.mode == PipelineMode.DSP
    assert orchestrator.state == RuntimeState.DEGRADED_DSP
    assert orchestrator.metrics.overload_events == 1
