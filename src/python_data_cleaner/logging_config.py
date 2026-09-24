"""Logging setup shared by the command-line interface."""

from __future__ import annotations

import logging


def configure_logging(level: str) -> None:
    """Configure concise console logging at the requested level."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(levelname)s: %(message)s",
        force=True,
    )
