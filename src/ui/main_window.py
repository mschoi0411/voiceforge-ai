from __future__ import annotations

from dataclasses import dataclass

from src.runtime import PipelineMode, RuntimeState


@dataclass
class UiState:
    mode: PipelineMode
    runtime_state: RuntimeState
    overlay_visible: bool
    ai_toggle_enabled: bool
    status_message: str


class MainWindowViewModel:
    def __init__(self) -> None:
        self._overlay_visible = False
        self._mode = PipelineMode.BYPASS
        self._runtime_state = RuntimeState.WARMING
        self._last_reason = "warming"

    def toggle_overlay_visibility(self) -> None:
        self._overlay_visible = not self._overlay_visible

    def set_mode(self, mode: PipelineMode) -> None:
        self._mode = mode

    def update_runtime_state(self, state: RuntimeState, reason: str = "") -> None:
        self._runtime_state = state
        if reason:
            self._last_reason = reason

    def snapshot(self) -> UiState:
        ai_toggle_enabled = self._runtime_state == RuntimeState.READY
        status_message = self._status_message()
        return UiState(
            mode=self._mode,
            runtime_state=self._runtime_state,
            overlay_visible=self._overlay_visible,
            ai_toggle_enabled=ai_toggle_enabled,
            status_message=status_message,
        )

    def _status_message(self) -> str:
        state = self._runtime_state
        if state == RuntimeState.WARMING:
            return "AI warming up"
        if state == RuntimeState.DEGRADED_DSP:
            return f"Using DSP fallback: {self._last_reason}"
        if state == RuntimeState.DEVICE_LOST:
            return "Audio device lost"
        if state == RuntimeState.RECOVERING:
            return "Recovering audio pipeline"
        if state == RuntimeState.ERROR:
            return "Runtime error"
        return "Ready"
