from __future__ import annotations

import subprocess
import sys


def test_packaged_launch_equivalent_cli_mode() -> None:
    result = subprocess.run(
        [sys.executable, "-m", "src.main", "--no-audio"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
