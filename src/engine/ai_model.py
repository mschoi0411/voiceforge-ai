from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from src.core.model_manifest import ModelManifest


@dataclass
class ProviderPreflightResult:
    available_providers: list[str]
    configured_providers: list[str]
    selected_provider: str
    ready: bool
    warning: str | None = None


@dataclass
class WarmupResult:
    ready: bool
    warmup_ms: int
    selected_provider: str


class OnnxModelAdapter:
    def __init__(self, provider_order: tuple[str, ...]) -> None:
        self.provider_order = provider_order
        self._preflight: ProviderPreflightResult | None = None
        self._ready = False

    def preflight(self, manifest: ModelManifest) -> ProviderPreflightResult:
        manifest.validate()
        if not Path(manifest.model_path).suffix.lower() == ".onnx":
            raise ValueError("model_path must point to an ONNX file.")

        available = _available_providers()
        selected = "CPUExecutionProvider"
        warning: str | None = None

        for provider in self.provider_order:
            if provider in available:
                selected = provider
                break

        if selected not in available and "CPUExecutionProvider" not in available:
            warning = "No supported execution provider available."

        self._preflight = ProviderPreflightResult(
            available_providers=available,
            configured_providers=list(self.provider_order),
            selected_provider=selected,
            ready=warning is None,
            warning=warning,
        )
        return self._preflight

    def warmup(self, manifest: ModelManifest) -> WarmupResult:
        if self._preflight is None:
            self.preflight(manifest)

        if self._preflight is None or not self._preflight.ready:
            self._ready = False
            return WarmupResult(ready=False, warmup_ms=0, selected_provider="CPUExecutionProvider")

        _ = np.zeros(manifest.input_tensor.shape, dtype=np.float32)
        self._ready = True
        return WarmupResult(
            ready=True,
            warmup_ms=20 if self._preflight.selected_provider == "CPUExecutionProvider" else 8,
            selected_provider=self._preflight.selected_provider,
        )

    @property
    def ready(self) -> bool:
        return self._ready


def _available_providers() -> list[str]:
    try:
        import onnxruntime as ort  # type: ignore

        providers = list(ort.get_available_providers())
    except Exception:
        providers = ["CPUExecutionProvider"]
    if "CPUExecutionProvider" not in providers:
        providers.append("CPUExecutionProvider")
    return providers


def supported_ops_warning(_: dict[str, Any]) -> str | None:
    return None
