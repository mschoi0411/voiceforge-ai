from __future__ import annotations

from src.config.paths import resolve_runtime_paths


def test_standard_paths_keep_writable_data_outside_install_dir() -> None:
    paths = resolve_runtime_paths()
    assert str(paths["install_models"]).startswith("models")
    assert "AppData" in str(paths["user_models"]) or "home" in str(paths["user_models"]).lower()
    assert "AppData" in str(paths["settings"]) or "home" in str(paths["settings"]).lower()
