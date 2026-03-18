from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def test_routing_probe_reports_guidance_when_targets_missing(tmp_path: Path) -> None:
    out = tmp_path / "routing.json"
    cmd = [
        sys.executable,
        "tools/routing_probe.py",
        "--targets",
        "DefinitelyMissingDevice",
        "--json-out",
        str(out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    assert result.returncode == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["missing"] == ["DefinitelyMissingDevice"]
    assert "guidance" in payload
