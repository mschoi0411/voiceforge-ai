from __future__ import annotations

import argparse
import importlib
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voiceforge-ai",
        description="Windows-first real-time voice changer (scaffold mode)",
    )
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Run in scaffold/no-audio mode.",
    )
    parser.add_argument(
        "--require-optional",
        metavar="MODULE",
        help="Check optional dependency import and exit with a clear message.",
    )
    return parser


def check_optional_dependency(module_name: str) -> int:
    try:
        importlib.import_module(module_name)
    except ModuleNotFoundError:
        print(
            f"Optional dependency '{module_name}' is not installed. "
            "Install project extras or add the package to your environment.",
            file=sys.stderr,
        )
        return 2
    except Exception as exc:  # pragma: no cover
        print(f"Failed to import optional dependency '{module_name}': {exc}", file=sys.stderr)
        return 3

    print(f"Optional dependency '{module_name}' is available.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.require_optional:
        return check_optional_dependency(args.require_optional)

    if args.no_audio:
        print("VoiceForge AI scaffold mode: no-audio run complete.")
        return 0

    print(
        "VoiceForge AI scaffold initialized. "
        "Audio pipeline is not implemented yet. Use --no-audio for smoke checks."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
