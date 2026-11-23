"""Compatibility wrapper for the packaged registry normalizer."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gardening.normalization.registry import *
from gardening.normalization.registry import main


if __name__ == "__main__":
    main()
