from __future__ import annotations

from src.core.audio_contracts import requires_canonicalization


def test_resample_policy_marks_44k1_stereo_as_non_canonical() -> None:
    assert requires_canonicalization(sample_rate_hz=44_100, channels=2, dtype="float32")


def test_resample_policy_marks_24k_mono_float32_as_canonical() -> None:
    assert not requires_canonicalization(sample_rate_hz=24_000, channels=1, dtype="float32")
