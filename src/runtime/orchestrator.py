from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from src.audio.buffer import BoundedFrameQueue
from src.core.audio_contracts import AudioFrame, QueuePolicy


class PipelineMode(str, Enum):
    BYPASS = "bypass"
    DSP = "dsp"
    AI = "ai"


class RuntimeState(str, Enum):
    WARMING = "warming"
    READY = "ready"
    DEGRADED_DSP = "degraded_dsp"
    DEVICE_LOST = "device_lost"
    RECOVERING = "recovering"
    ERROR = "error"


@dataclass
class RuntimeMetrics:
    dropped_frames: int = 0
    overload_events: int = 0
    fallback_events: int = 0
    callback_exceptions: int = 0
    queue_depth_peak: int = 0


@dataclass
class Orchestrator:
    queue_policy: QueuePolicy = field(default_factory=QueuePolicy)
    mode: PipelineMode = PipelineMode.BYPASS
    state: RuntimeState = RuntimeState.READY
    selected_mode: PipelineMode = PipelineMode.BYPASS
    metrics: RuntimeMetrics = field(default_factory=RuntimeMetrics)

    def __post_init__(self) -> None:
        self.queue_policy.validate()
        self.capture_queue = BoundedFrameQueue[AudioFrame](self.queue_policy.capture_max_frames)
        self.process_queue = BoundedFrameQueue[AudioFrame](self.queue_policy.process_max_frames)
        self.output_queue = BoundedFrameQueue[AudioFrame](self.queue_policy.output_max_frames)
        self._cooldown_until_ms = 0

    def set_selected_mode(self, mode: PipelineMode) -> None:
        self.selected_mode = mode
        if mode == PipelineMode.AI and self.state != RuntimeState.READY:
            self.mode = PipelineMode.DSP
        else:
            self.mode = mode

    def push_capture(self, frame: AudioFrame) -> None:
        self.capture_queue.push(frame)
        self.metrics.dropped_frames += self.capture_queue.stats.dropped_frames
        self.metrics.queue_depth_peak = max(self.metrics.queue_depth_peak, self.capture_queue.depth())

    def on_overload(self, now_ms: int) -> None:
        self.metrics.overload_events += 1
        self.metrics.fallback_events += 1
        self.mode = PipelineMode.DSP
        self.state = RuntimeState.DEGRADED_DSP
        self._cooldown_until_ms = now_ms + 10_000

    def maybe_recover_ai(
        self,
        *,
        now_ms: int,
        queue_depth: int,
        preflight_ok: bool,
        callback_ok: bool,
    ) -> bool:
        if self.selected_mode != PipelineMode.AI:
            return False
        if now_ms < self._cooldown_until_ms:
            return False
        if queue_depth > 1 or not preflight_ok or not callback_ok:
            return False
        self.mode = PipelineMode.AI
        self.state = RuntimeState.READY
        return True

    def mark_device_lost(self) -> None:
        self.state = RuntimeState.DEVICE_LOST

    def mark_recovering(self) -> None:
        self.state = RuntimeState.RECOVERING

    def mark_ready(self) -> None:
        self.state = RuntimeState.READY
