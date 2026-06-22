#!/usr/bin/env python3
"""Compatibility wrapper for the LearnLoop course server."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from learnloop.cli import main


if __name__ == "__main__":
    raise SystemExit(main(["serve", str(Path(__file__).resolve().parent), *sys.argv[1:]]))
