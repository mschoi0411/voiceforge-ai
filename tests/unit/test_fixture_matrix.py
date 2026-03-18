from __future__ import annotations

from src.core.fixtures import REQUIRED_FIXTURE_CASES


def test_required_fixture_matrix_contains_contract_cases() -> None:
    expected = {
        "voice_48k_mono",
        "voice_44k1_stereo",
        "silence_heavy_speech",
        "near_clipping_speech",
        "noisy_speech",
        "plosive_heavy_speech",
        "fast_speech",
        "slow_speech",
        "male_range_speech",
        "female_range_speech",
    }
    assert set(REQUIRED_FIXTURE_CASES) == expected
