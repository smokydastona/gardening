"""Compatibility wrapper for the packaged authoritative data model."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gardening.validation.data_model import (
    VERIFICATION_STATES,
    main,
    read_csv,
    stable_plant_id,
    validate_authoritative_registry,
)

__all__ = [
    "VERIFICATION_STATES",
    "read_csv",
    "stable_plant_id",
    "validate_authoritative_registry",
    "main",
]


if __name__ == "__main__":
    main()
