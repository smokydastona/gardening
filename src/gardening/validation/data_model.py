"""Authoritative data-model validation for the Errington publication pipeline."""

from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path

from gardening.config import find_repository_root


VERIFICATION_STATES = {
    "unreviewed",
    "research_required",
    "partially_verified",
    "verified",
    "conflicting_evidence",
    "insufficient_evidence",
    "not_applicable",
}


def stable_plant_id(display_name: str) -> str:
    key = re.sub(r"[^A-Za-z0-9]+", "-", display_name.strip()).strip("-").lower()
    if not key:
        raise ValueError("Plant display name cannot produce a stable plant ID")
    return f"plant-{key}"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_authoritative_registry(base_dir: Path) -> dict[str, int]:
    registry_path = base_dir / "plant_registry.csv"
    rows = read_csv(registry_path)
    if not rows:
        raise ValueError("plant_registry.csv is empty")
    required = {"plant_id", "display_name", "category", "latin_name", "family"}
    missing = required - set(rows[0])
    if missing:
        raise ValueError("plant_registry.csv missing columns: " + ", ".join(sorted(missing)))

    ids = [row["plant_id"].strip() for row in rows]
    names = [row["display_name"].strip() for row in rows]
    duplicate_ids = sorted(value for value, count in Counter(ids).items() if value and count > 1)
    duplicate_names = sorted(value for value, count in Counter(names).items() if value and count > 1)
    if any(not value for value in ids):
        raise ValueError("plant_registry.csv contains a blank plant_id")
    if duplicate_ids:
        raise ValueError("Duplicate plant_id values: " + ", ".join(duplicate_ids))
    if duplicate_names:
        raise ValueError("Duplicate display_name values: " + ", ".join(duplicate_names))

    mismatched = [
        row["plant_id"]
        for row in rows
        if row["plant_id"] != stable_plant_id(row["display_name"])
    ]
    if mismatched:
        raise ValueError("Plant IDs do not match display-name-derived stable IDs: " + ", ".join(mismatched[:20]))

    calendar = read_csv(base_dir / "errington_calendar_entries.csv")
    calendar_required = {"month", "page_type", "section", "page_number", "plant_text", "plant_normalized", "row_text"}
    missing_calendar = calendar_required - set(calendar[0])
    if missing_calendar:
        raise ValueError("Calendar CSV missing columns: " + ", ".join(sorted(missing_calendar)))

    claims = read_csv(base_dir / "claims" / "CLAIM_SOURCES.csv")
    claim_required = {"claim_id", "plant_id", "claim_text", "source_title", "url", "status"}
    missing_claim = claim_required - set(claims[0])
    if missing_claim:
        raise ValueError("CLAIM_SOURCES.csv missing columns: " + ", ".join(sorted(missing_claim)))
    malformed_claims = [
        row.get("claim_id") or f"row {index}"
        for index, row in enumerate(claims, start=2)
        if None in row or any(value is None for value in row.values())
    ]
    if malformed_claims:
        raise ValueError(
            "CLAIM_SOURCES.csv has rows with misaligned columns: "
            + ", ".join(malformed_claims)
        )
    known_ids = set(ids)
    orphan_claims = sorted({row["plant_id"] for row in claims if row["plant_id"] not in known_ids})
    if orphan_claims:
        raise ValueError("Claim source references unknown plant IDs: " + ", ".join(orphan_claims))
    duplicate_claims = sorted(
        value for value, count in Counter(row["claim_id"] for row in claims).items() if value and count > 1
    )
    if duplicate_claims:
        raise ValueError("Duplicate claim_id values: " + ", ".join(duplicate_claims))

    return {
        "plant_records": len(rows),
        "calendar_entries": len(calendar),
        "claim_records": len(claims),
    }


def main() -> None:
    print(validate_authoritative_registry(find_repository_root(__file__)))


if __name__ == "__main__":
    main()
