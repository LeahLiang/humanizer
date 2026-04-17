#!/usr/bin/env python3
"""Humanizer `/api_v2` client — bypass AI detectors (CNKI / Weipu / Turnitin).

Submits a rewrite or detection job, polls until it finishes, prints the result.
Works as a CLI and as an importable module.

Environment variables:
    HUMANIZER_API_KEY        Required. API key from https://ushallpass.ai.
    HUMANIZER_API_BASE_URL   Optional. Defaults to https://leahloveswriting.xyz
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

DEFAULT_BASE_URL = "https://leahloveswriting.xyz"
DEFAULT_TIMEOUT = 180
DEFAULT_POLL_INTERVAL = 2.0

REWRITE_PATH = {
    "zh": "/api_v2/rewrite/chinese/jobs",
    "en": "/api_v2/rewrite/english/jobs",
}
DETECT_PATH = {
    "zh": "/api_v2/detect/chinese/jobs",
    "en": "/api_v2/detect/english/jobs",
}
VALID_ZH_MODES = {"light", "aggressive", "weipu", "weipu_aggressive"}


class HumanizerError(RuntimeError):
    def __init__(self, code: str, message: str, details: Any = None):
        super().__init__(f"[{code}] {message}")
        self.code = code
        self.message = message
        self.details = details


class HumanizerClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
    ):
        self.api_key = api_key or os.environ.get("HUMANIZER_API_KEY")
        if not self.api_key:
            raise HumanizerError(
                "AUTH_ERROR",
                "Missing API key. Set HUMANIZER_API_KEY or pass api_key=.",
            )
        self.base_url = (
            base_url or os.environ.get("HUMANIZER_API_BASE_URL") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.timeout = timeout
        self.poll_interval = poll_interval

    def _request(self, method: str, path: str, body: dict | None = None) -> dict:
        url = f"{self.base_url}{path}"
        data = json.dumps(body).encode("utf-8") if body is not None else None
        headers = {
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }
        if data is not None:
            headers["Content-Type"] = "application/json"
        req = urlrequest.Request(url, data=data, method=method, headers=headers)
        try:
            with urlrequest.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except urlerror.HTTPError as e:
            try:
                payload = json.loads(e.read().decode("utf-8"))
            except Exception:
                raise HumanizerError(
                    "HTTP_ERROR", f"HTTP {e.code}: {e.reason}"
                ) from e
        except urlerror.URLError as e:
            raise HumanizerError("NETWORK_ERROR", str(e.reason)) from e

        if not payload.get("success"):
            err = payload.get("error") or {}
            raise HumanizerError(
                err.get("code", "UNKNOWN"),
                err.get("message", "Unknown error"),
                err.get("details"),
            )
        return payload["data"]

    def _submit(self, path: str, body: dict) -> str:
        data = self._request("POST", path, body)
        task_id = data.get("task_id")
        if not task_id:
            raise HumanizerError("TASK_SUBMIT_FAILED", "No task_id in response", data)
        return task_id

    def _poll(self, status_path: str) -> dict:
        deadline = time.monotonic() + self.timeout
        while True:
            data = self._request("GET", status_path)
            status = data.get("status")
            if status == "completed":
                return data
            if status == "failed":
                raise HumanizerError(
                    "TASK_FAILED", data.get("error") or "Task failed", data
                )
            if time.monotonic() >= deadline:
                raise HumanizerError(
                    "TIMEOUT", f"Task did not finish within {self.timeout}s"
                )
            time.sleep(self.poll_interval)

    def rewrite(self, text: str, lang: str, mode: str = "light") -> dict:
        if lang not in REWRITE_PATH:
            raise ValueError(f"lang must be one of {list(REWRITE_PATH)}")
        body: dict[str, Any] = {"text": text}
        if lang == "zh":
            if mode not in VALID_ZH_MODES:
                raise ValueError(f"mode must be one of {sorted(VALID_ZH_MODES)}")
            body["mode"] = mode
        submit_path = REWRITE_PATH[lang]
        task_id = self._submit(submit_path, body)
        return self._poll(f"{submit_path}/{task_id}")

    def detect(self, text: str, lang: str) -> dict:
        if lang not in DETECT_PATH:
            raise ValueError(f"lang must be one of {list(DETECT_PATH)}")
        submit_path = DETECT_PATH[lang]
        task_id = self._submit(submit_path, {"sentence": text})
        return self._poll(f"{submit_path}/{task_id}")

    def health(self) -> dict:
        return self._request("GET", "/api_v2/health")


def _read_input(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    raise SystemExit("error: provide --text, --file, or pipe text via stdin")


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="humanizer",
        description="Humanizer CLI — bypass AI detectors (CNKI / Weipu / Turnitin). Rewrite + detect.",
    )
    p.add_argument("--base-url", default=None, help="Override API base URL.")
    p.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    p.add_argument("--poll-interval", type=float, default=DEFAULT_POLL_INTERVAL)
    p.add_argument("--json", action="store_true", help="Emit raw JSON result.")

    sub = p.add_subparsers(dest="command", required=True)

    rewrite = sub.add_parser("rewrite", help="Rewrite text to reduce AI signatures.")
    rewrite.add_argument("lang", choices=["zh", "en"])
    rewrite.add_argument(
        "--mode",
        default="light",
        choices=sorted(VALID_ZH_MODES),
        help="Chinese only. English ignores this flag.",
    )
    _add_input_flags(rewrite)

    detect = sub.add_parser("detect", help="Detect whether text is AI-generated.")
    detect.add_argument("lang", choices=["zh", "en"])
    _add_input_flags(detect)

    sub.add_parser("health", help="Call /api_v2/health.")

    return p


def _add_input_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--text", help="Input text (inline).")
    parser.add_argument("--file", help="Read input from this path.")


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
