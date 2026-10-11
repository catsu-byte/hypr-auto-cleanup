#!/usr/bin/env python3
"""Compatibility launcher for the Linux implementation."""

from pathlib import Path
import runpy

runpy.run_path(
    str(Path(__file__).resolve().parent / "linux" / "auto_cleanup.py"),
    run_name="__main__",
)
