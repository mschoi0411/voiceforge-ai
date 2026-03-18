"""Shared core contracts and settings."""

from src.core.audio_contracts import (
    AI_FRAMES_PER_INFERENCE,
    AI_WINDOW_SAMPLES,
    CANONICAL_CHANNELS,
    CANONICAL_FRAME_MS,
    CANONICAL_FRAME_SAMPLES,
    CANONICAL_SAMPLE_RATE_HZ,
    AudioFrame,
    QueuePolicy,
    is_canonical_stream,
    normalize_canonical_frame,
    requires_canonicalization,
)
from src.core.model_manifest import ModelManifest, TensorSpec, manifest_from_dict

__all__ = [
    "AI_FRAMES_PER_INFERENCE",
    "AI_WINDOW_SAMPLES",
    "CANONICAL_CHANNELS",
    "CANONICAL_FRAME_MS",
    "CANONICAL_FRAME_SAMPLES",
    "CANONICAL_SAMPLE_RATE_HZ",
    "AudioFrame",
    "QueuePolicy",
    "ModelManifest",
    "TensorSpec",
    "is_canonical_stream",
    "manifest_from_dict",
    "normalize_canonical_frame",
    "requires_canonicalization",
]
