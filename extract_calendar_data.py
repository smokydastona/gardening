"""Compatibility wrapper for the packaged calendar-chart OCR tool."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gardening.ingestion.calendar_ocr import *
from gardening.ingestion.calendar_ocr import main


if __name__ == "__main__":
    main()
