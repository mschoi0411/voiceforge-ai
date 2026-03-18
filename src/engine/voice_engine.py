from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from src.engine.ai_model import OnnxModelAdapter
from src.engine.dsp_effects import apply_preset


@dataclass
class VoiceEngineConfig:
    provider_order: tuple[str, ...] = ("CUDAExecutionProvider", "CPUExecutionProvider")


class VoiceEngine:
    def __init__(self, config: VoiceEngineConfig | None = None) -> None:
        self.config = config or VoiceEngineConfig()
        self.ai = OnnxModelAdapter(self.config.provider_order)

    def process_dsp(self, samples: np.ndarray, preset: str, pitch: float = 0.0, tone: float = 0.0) -> np.ndarray:
        return apply_preset(samples=samples, preset_name=preset, pitch=pitch, tone=tone)

    def process_ai_passthrough(self, samples: np.ndarray) -> np.ndarray:
        # v1 baseline: adapter preflight/warmup lifecycle is real, transform kernel remains pass-through.
        return np.asarray(samples, dtype=np.float32)
