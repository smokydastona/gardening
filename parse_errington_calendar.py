"""Compatibility wrapper for the packaged calendar parser."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gardening.parsing.calendar import *
from gardening.parsing.calendar import main


if __name__ == "__main__":
    main()
