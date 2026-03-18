from __future__ import annotations

import subprocess
import sys


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, "-m", "src.main", *args]
    return subprocess.run(command, capture_output=True, text=True, check=False)


def test_cli_help_exits_zero() -> None:
    result = _run("--help")
    assert result.returncode == 0
    assert "voiceforge-ai" in result.stdout


def test_cli_no_audio_exits_zero() -> None:
    result = _run("--no-audio")
    assert result.returncode == 0
    assert "no-audio" in result.stdout


def test_cli_missing_optional_dependency_is_clear() -> None:
    result = _run("--no-audio", "--require-optional", "missing_dep")
    assert result.returncode != 0
    assert "Optional dependency 'missing_dep' is not installed." in result.stderr
