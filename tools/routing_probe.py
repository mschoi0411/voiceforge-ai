from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VoiceForge routing compatibility probe")
    parser.add_argument("--targets", required=True, help="Comma-separated target device names")
    parser.add_argument("--json-out", required=True)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    targets = [x.strip() for x in args.targets.split(",") if x.strip()]

    devices = _list_devices()
    found = []
    missing = []
    for target in targets:
        if any(target.lower() in d.lower() for d in devices):
            found.append(target)
        else:
            missing.append(target)

    payload = {
        "targets": targets,
        "found": found,
        "missing": missing,
        "available_devices": devices,
        "guidance": (
            "Install or enable target virtual audio device if missing. "
            "Application remains usable with local monitoring."
        ),
    }
    out_path = Path(args.json_out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Routing probe complete: found={len(found)} missing={len(missing)}")
    return 0


def _list_devices() -> list[str]:
    try:
        import sounddevice as sd  # type: ignore

        devices = sd.query_devices()
        return [str(dev["name"]) for dev in devices]
    except Exception:
        return []


if __name__ == "__main__":
    raise SystemExit(main())
