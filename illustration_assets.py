"""Compatibility wrapper for the packaged illustration publication gate."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from gardening.illustrations.publication_gate import (
    EXTENSIONS,
    ORGANS,
    REVIEW_FIELDS,
    approved_assets,
    keyify,
    publication_problem,
    sha256_file,
    sha256_json,
)

__all__ = [
    "EXTENSIONS",
    "ORGANS",
    "REVIEW_FIELDS",
    "approved_assets",
    "keyify",
    "publication_problem",
    "sha256_file",
    "sha256_json",
]
