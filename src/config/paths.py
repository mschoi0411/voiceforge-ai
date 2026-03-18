from __future__ import annotations

import os
from pathlib import Path


def resolve_runtime_paths(app_name: str = "VoiceForgeAI") -> dict[str, Path]:
    appdata = Path(os.getenv("APPDATA", Path.home() / "AppData" / "Roaming")) / app_name
    local = Path(os.getenv("LOCALAPPDATA", Path.home() / "AppData" / "Local")) / app_name
    return {
        "install_models": Path("models/default"),
        "user_models": local / "models",
        "settings": appdata / "settings",
        "cache": local / "cache",
        "evidence": local / "evidence",
    }
