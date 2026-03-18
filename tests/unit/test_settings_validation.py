from __future__ import annotations

import pytest

from src.config.settings import RuntimeSettings, build_default_settings
from src.core.audio_contracts import QueuePolicy


def test_build_default_settings_is_valid() -> None:
    settings = build_default_settings()
    assert settings.provider_order == ("CUDAExecutionProvider", "CPUExecutionProvider")


def test_settings_reject_provider_order_without_cpu_fallback() -> None:
    settings = RuntimeSettings(provider_order=("CUDAExecutionProvider",))
    with pytest.raises(ValueError):
        settings.validate()


def test_settings_reject_non_positive_queue_limit() -> None:
    settings = RuntimeSettings(queue_policy=QueuePolicy(capture_max_frames=0, process_max_frames=3, output_max_frames=3))
    with pytest.raises(ValueError):
        settings.validate()
