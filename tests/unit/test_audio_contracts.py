from __future__ import annotations

import numpy as np
import pytest

from src.core.audio_contracts import (
    CANONICAL_FRAME_SAMPLES,
    CANONICAL_SAMPLE_RATE_HZ,
    AudioFrame,
    QueuePolicy,
    is_canonical_stream,
    normalize_canonical_frame,
)


def test_normalize_canonical_frame_accepts_expected_shape() -> None:
    frame = normalize_canonical_frame(np.zeros(CANONICAL_FRAME_SAMPLES, dtype=np.float32))
    assert frame.dtype == np.float32
    assert frame.shape == (CANONICAL_FRAME_SAMPLES,)


def test_normalize_canonical_frame_rejects_wrong_shape() -> None:
    with pytest.raises(ValueError):
        normalize_canonical_frame(np.zeros((2, CANONICAL_FRAME_SAMPLES), dtype=np.float32))


def test_audio_frame_validates_timestamp_and_shape() -> None:
    frame = AudioFrame(
        samples=np.zeros(CANONICAL_FRAME_SAMPLES, dtype=np.float32),
        timestamp_ns=123,
    )
    assert frame.timestamp_ns == 123


def test_queue_policy_defaults_are_v1_contract_values() -> None:
    policy = QueuePolicy()
    policy.validate()
    assert policy.capture_max_frames == 3
    assert policy.process_max_frames == 3
    assert policy.output_max_frames == 3


def test_is_canonical_stream_true_for_contract_values() -> None:
    assert is_canonical_stream(CANONICAL_SAMPLE_RATE_HZ, 1, "float32")
