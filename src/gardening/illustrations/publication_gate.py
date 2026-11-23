"""Shared publication checks for botanical illustration assets."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ORGANS = ("growth_habit", "leaves", "stems", "flowers", "fruit_and_seed", "roots")
REVIEW_FIELDS = (*ORGANS, "style")
EXTENSIONS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp"}


def keyify(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: Any) -> str:
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def publication_problem(image: Path) -> str | None:
    """Return a reason an asset is not eligible, or None for a valid sign-off."""
    sidecar = image.with_suffix(".json")
    try:
        metadata = json.loads(sidecar.read_text(encoding="utf-8"))
        if not isinstance(metadata, dict):
            return "invalid metadata"
        review = metadata.get("review")
        evidence = metadata.get("evidence")
        if not isinstance(review, dict) or not isinstance(evidence, dict):
            return "missing review or evidence"
        checks = review.get("checklist")
        if not isinstance(checks, dict):
            return "missing review checklist"
        if metadata.get("schema_version") != 1 or metadata.get("status") != "human-reviewed-approved":
            return "not approved"
        if metadata.get("asset_id") != keyify(image.stem) or metadata.get("file") != image.name:
            return "image identity mismatch"
        if evidence.get("plant_key") != metadata.get("asset_id"):
            return "evidence plant identity mismatch"
        if metadata.get("image_sha256") != sha256_file(image):
            return "image changed after review"
        if metadata.get("evidence_sha256") != sha256_json(evidence):
            return "evidence changed after review"
        if evidence.get("taxon_verified") is not True:
            return "taxon not verified"
        if not all(isinstance(review.get(k), str) and review[k].strip() for k in ("reviewer", "reviewed_at_utc", "notes")):
            return "incomplete reviewer sign-off"
        if checks.get("style") != "pass":
            return "style not approved"
        if any(checks.get(k) not in ("pass", "not-depicted") for k in ORGANS):
            return "incomplete botanical checklist"
        if checks.get("growth_habit") != "pass" or checks.get("leaves") != "pass":
            return "growth habit and leaves must be reviewed"
    except (OSError, ValueError, TypeError) as exc:
        return f"unreadable approval metadata: {exc}"
    return None


def approved_assets(directory: Path) -> dict[str, Path]:
    if not directory.exists():
        return {}
    assets: dict[str, Path] = {}
    for path in sorted(directory.iterdir()):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        reason = publication_problem(path)
        if reason:
            print(f"Skipping unapproved illustration {path.name}: {reason}", file=sys.stderr)
            continue
        key = keyify(path.stem)
        if key in assets:
            raise ValueError(f"Multiple approved illustrations resolve to {key}")
        assets[key] = path
    return assets
