from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_bypass_pipeline_harness(tmp_path: Path) -> None:
    out = tmp_path / "bypass.json"
    cmd = [
        sys.executable,
        "tools/pipeline_harness.py",
        "--mode",
        "bypass",
        "--input",
        "tests/fixtures/voice_48k_mono.wav",
        "--expect-max-latency-ms",
        "80",
        "--json-out",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["latency"]["end_to_end_ms"] <= 80
