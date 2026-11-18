"""Small terminal styling helpers.

The implementation uses plain ANSI escape sequences so there is no extra
dependency. Colour is only emitted when explicitly requested or when the
target stream is an interactive terminal.
"""

import os
import sys
from typing import TextIO

RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"


def color_enabled(mode: str, stream: TextIO) -> bool:
    """Return whether ANSI colour should be used for ``stream``.

    ``mode`` is ``"always"``, ``"never"`` or ``"auto"``. In auto mode the
    ``NO_COLOR`` convention and ``TERM=dumb`` are honoured.
    """
    if mode == "always":
        return True
    if mode == "never":
        return False
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    return bool(getattr(stream, "isatty", lambda: False)())


class Console:
    """Apply a consistent style to CLI output."""

    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def _paint(self, text: str, *codes: str) -> str:
        if not self.enabled:
            return text
        return f"{''.join(codes)}{text}{RESET}"

    def error(self, text: str) -> str:
        """Style a documentation issue."""
        return self._paint(text, RED)

    def heading(self, text: str) -> str:
        """Style a summary or error headline."""
        return self._paint(text, BOLD, YELLOW)

    def success(self, text: str) -> str:
        """Style a success message."""
        return self._paint(text, GREEN)


def for_stream(mode: str, stream: TextIO) -> Console:
    """Build a console for ``stream`` following ``mode``."""
    return Console(color_enabled(mode, stream))


def stdout(mode: str) -> Console:
    """Console bound to the current standard output."""
    return for_stream(mode, sys.stdout)


def stderr(mode: str) -> Console:
    """Console bound to the current standard error."""
    return for_stream(mode, sys.stderr)
