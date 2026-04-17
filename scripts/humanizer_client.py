#!/usr/bin/env python3
"""Backward-compatible shim for the split Humanizer scripts."""
try:
    from scripts.humanizer_api import (
        DEFAULT_BASE_URL,
        DEFAULT_POLL_INTERVAL,
        DEFAULT_TIMEOUT,
        DETECT_PATH,
        REWRITE_PATH,
        VALID_ZH_MODES,
        HumanizerClient,
        HumanizerError,
    )
    from scripts.humanizer_cli import main
except ModuleNotFoundError:
    from humanizer_api import (  # type: ignore
        DEFAULT_BASE_URL,
        DEFAULT_POLL_INTERVAL,
        DEFAULT_TIMEOUT,
        DETECT_PATH,
        REWRITE_PATH,
        VALID_ZH_MODES,
        HumanizerClient,
        HumanizerError,
    )
    from humanizer_cli import main  # type: ignore

__all__ = [
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_POLL_INTERVAL",
    "REWRITE_PATH",
    "DETECT_PATH",
    "VALID_ZH_MODES",
    "HumanizerClient",
    "HumanizerError",
    "main",
]


if __name__ == "__main__":
    raise SystemExit(main())
