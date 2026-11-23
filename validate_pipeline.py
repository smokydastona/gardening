"""Compatibility wrapper for the packaged validation pipeline."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gardening.validation.pipeline import *
from gardening.validation.pipeline import main


if __name__ == "__main__":
    main()
