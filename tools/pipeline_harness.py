from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="VoiceForge AI pipeline harness scaffold")
    parser.add_argument("--mode", default="bypass")
    parser.add_argument("--input")
    parser.add_argument("--json-out")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    print(
        "Pipeline harness scaffold is active. "
        f"mode={args.mode} input={args.input} json_out={args.json_out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
