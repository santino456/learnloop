#!/usr/bin/env python3
"""Validate a LearnLoop course using the project CLI."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from learnloop.cli import main


if __name__ == "__main__":
    course_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    raise SystemExit(main(["validate", course_dir]))
