#!/usr/bin/env python3
"""Humanizer CLI entrypoint."""
from __future__ import annotations

import argparse
import json
import sys

try:
    from scripts.humanizer_api import (
        DEFAULT_POLL_INTERVAL,
        DEFAULT_TIMEOUT,
        VALID_ZH_MODES,
        HumanizerClient,
        HumanizerError,
    )
except ModuleNotFoundError:
    from humanizer_api import (  # type: ignore
        DEFAULT_POLL_INTERVAL,
        DEFAULT_TIMEOUT,
        VALID_ZH_MODES,
        HumanizerClient,
        HumanizerError,
    )


def _read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("error: provide --text, --file, or pipe text via stdin")


def _add_input_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", help="Input text (inline).")
    parser.add_argument("--file", help="Read input from this path.")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="humanizer",
        description="Humanizer CLI — bypass AI detectors (CNKI / Weipu / Turnitin). Rewrite + detect.",
    )
    p.add_argument("--base-url", default=None, help="Override API base URL.")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL)
    p.add_argument(
        "--json",
        action="store_true",
        help="Emit raw JSON result (can be set before or after subcommand).",
    )

    sub = p.add_subparsers(dest="command", required=True)

    rewrite = sub.add_parser("rewrite", help="Rewrite text to reduce AI signatures.")
    rewrite.add_argument("lang", choices=["zh", "en"])
    rewrite.add_argument(
        "--mode",
        default="light",
        choices=sorted(VALID_ZH_MODES),
        help="Chinese only. English ignores this flag.",
    )
    rewrite.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    _add_input_flags(rewrite)

    detect = sub.add_parser("detect", help="Detect whether text is AI-generated.")
    detect.add_argument("lang", choices=["zh", "en"])
    detect.add_argument("--json", action="store_true", help=argparse.SUPPRESS)
    _add_input_flags(detect)

    sub.add_parser("health", help="Call /api_v2/health.")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    client = HumanizerClient(
        base_url=args.base_url,
        timeout=args.timeout,
        poll_interval=args.poll_interval,
    )

    try:
        if args.command == "health":
            result = client.health()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        text = _read_input(args)
        if not text.strip():
            print("error: input text is empty", file=sys.stderr)
            return 2

        if args.command == "rewrite":
            data = client.rewrite(text, args.lang, mode=args.mode)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                print(data.get("result", ""))
        elif args.command == "detect":
            data = client.detect(text, args.lang)
            if args.json:
                print(json.dumps(data, ensure_ascii=False, indent=2))
            else:
                result = data.get("result", {}) or {}
                analysis = result.get("analysis", {}) or {}
                label = analysis.get("label", "unknown")
                perplexity = analysis.get("perplexity")
                print(f"label: {label}")
                if perplexity is not None:
                    print(f"perplexity: {perplexity}")
        return 0
    except HumanizerError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
