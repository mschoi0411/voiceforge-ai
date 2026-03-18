from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class DspPreset:
    name: str
    gain: float
    tone_tilt: float


PRESETS: dict[str, DspPreset] = {
    "robot": DspPreset(name="robot", gain=0.9, tone_tilt=0.15),
    "deep_voice": DspPreset(name="deep_voice", gain=1.05, tone_tilt=-0.1),
    "anime": DspPreset(name="anime", gain=0.95, tone_tilt=0.2),
    "neutral": DspPreset(name="neutral", gain=1.0, tone_tilt=0.0),
}


def apply_preset(samples: np.ndarray, preset_name: str, pitch: float = 0.0, tone: float = 0.0) -> np.ndarray:
    if preset_name not in PRESETS:
        raise ValueError(f"Unknown preset: {preset_name}")
    if pitch < -24.0 or pitch > 24.0:
        raise ValueError("pitch must be in [-24, 24]")
    if tone < -1.0 or tone > 1.0:
        raise ValueError("tone must be in [-1, 1]")

    preset = PRESETS[preset_name]
    working = np.asarray(samples, dtype=np.float32)

    shifted = _cheap_pitch_like_tilt(working, semitones=pitch)
    tonal = _tone_filter(shifted, preset.tone_tilt + tone)
    gained = tonal * preset.gain
    return np.clip(gained, -1.0, 1.0).astype(np.float32)


def _cheap_pitch_like_tilt(samples: np.ndarray, semitones: float) -> np.ndarray:
    # Lightweight, deterministic v1 placeholder: brightness tilt proportional to semitone intent.
    alpha = np.clip(semitones / 48.0, -0.4, 0.4)
    if samples.size < 2:
        return samples
    diff = np.concatenate(([0.0], np.diff(samples)))
    return (samples + alpha * diff).astype(np.float32)


def _tone_filter(samples: np.ndarray, tilt: float) -> np.ndarray:
    if samples.size == 0:
        return samples
    tilt = float(np.clip(tilt, -1.0, 1.0))
    smoothed = np.convolve(samples, np.array([0.25, 0.5, 0.25], dtype=np.float32), mode="same")
    return ((1.0 - max(0.0, -tilt)) * samples + max(0.0, -tilt) * smoothed + max(0.0, tilt) * (samples - smoothed)).astype(np.float32)


def clipping_ratio(samples: np.ndarray) -> float:
    working = np.asarray(samples, dtype=np.float32)
    if working.size == 0:
        return 0.0
    clipped = np.logical_or(working >= 0.999, working <= -0.999)
    return float(clipped.sum() / working.size)


def dc_offset_mean(samples: np.ndarray) -> float:
    working = np.asarray(samples, dtype=np.float32)
    if working.size == 0:
        return 0.0
    return float(np.mean(working))


def loudness_db(samples: np.ndarray) -> float:
    working = np.asarray(samples, dtype=np.float32)
    if working.size == 0:
        return -120.0
    rms = float(np.sqrt(np.mean(np.square(working))))
    if rms <= 1e-9:
        return -120.0
    return float(20.0 * np.log10(rms))
