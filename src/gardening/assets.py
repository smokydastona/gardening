from __future__ import annotations

import csv
import hashlib
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AssetAudit:
    kind: str
    record_count: int = 0
    checked_files: int = 0
    approved_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def exit_code(self) -> int:
        return int(bool(self.errors))


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _is_sha256(value: str) -> bool:
    return bool(re.fullmatch(r"[a-fA-F0-9]{64}", value.strip()))


def _verify_files(
    manifest_path: Path,
    rows: list[dict[str, str]],
    filename_field: str,
    hash_field: str,
    audit: AssetAudit,
) -> None:
    seen_hashes: Counter[str] = Counter()
    for row in rows:
        filename = row.get(filename_field, "").strip()
        expected = row.get(hash_field, "").strip().lower()
        if not filename or Path(filename).name != filename or "\\" in filename:
            audit.errors.append(f"Invalid asset filename: {filename!r}")
            continue
        if not _is_sha256(expected):
            audit.errors.append(f"{filename}: missing or malformed SHA-256")
            continue
        asset_path = manifest_path.parent / filename
        if not asset_path.is_file():
            audit.errors.append(f"{filename}: asset file is missing")
            continue
        try:
            actual = hashlib.sha256(asset_path.read_bytes()).hexdigest()
        except OSError as error:
            audit.errors.append(f"{filename}: cannot read asset: {error}")
            continue
        if actual != expected:
            audit.errors.append(f"{filename}: checksum mismatch")
            continue
        audit.checked_files += 1
        seen_hashes[actual] += 1
    duplicates = sum(count - 1 for count in seen_hashes.values() if count > 1)
    if duplicates:
        audit.warnings.append(f"{duplicates} repeated image checksum(s)")


def audit_assets(repository: Path, kind: str) -> AssetAudit:
    if kind == "plant":
        manifest_path = repository / (
            "plant_illustrations/concept_candidates/candidate_manifest.csv"
        )
        id_field = "plant_id"
        filename_field = "filename"
        hash_field = "sha256"
    elif kind == "figure":
        manifest_path = repository / "educational_figures/figure_manifest.csv"
        id_field = "figure_id"
        filename_field = "filename"
        hash_field = "sha256"
    else:
        raise ValueError(f"Unknown asset kind: {kind}")

    audit = AssetAudit(kind)
    if not manifest_path.is_file():
        audit.errors.append(f"Manifest is missing: {manifest_path.relative_to(repository)}")
        return audit

    try:
        rows = _read_csv(manifest_path)
    except (OSError, UnicodeError, csv.Error) as error:
        audit.errors.append(f"Cannot read manifest: {error}")
        return audit

    audit.record_count = len(rows)
    if not rows:
        audit.errors.append("Manifest contains no asset records")
        return audit

    identifiers = [row.get(id_field, "").strip() for row in rows]
    if any(not identifier for identifier in identifiers):
        audit.errors.append(f"Manifest contains a blank {id_field}")
    duplicates = sorted(
        identifier
        for identifier, count in Counter(identifiers).items()
        if identifier and count > 1
    )
    if duplicates:
        audit.errors.append(f"Duplicate {id_field}: {', '.join(duplicates)}")

    if kind == "plant":
        registry_path = repository / "plant_registry.csv"
        try:
            registry_ids = {
                row["plant_id"]
                for row in _read_csv(registry_path)
                if row.get("plant_id", "").strip()
            }
        except (OSError, KeyError, UnicodeError, csv.Error) as error:
            audit.errors.append(f"Cannot read plant registry: {error}")
            return audit
        manifest_ids = {identifier for identifier in identifiers if identifier}
        if manifest_ids - registry_ids:
            audit.errors.append(
                "Candidate manifest has unknown plant IDs: "
                + ", ".join(sorted(manifest_ids - registry_ids))
            )
        if registry_ids - manifest_ids:
            audit.errors.append(
                f"{len(registry_ids - manifest_ids)} registry plant(s) have no candidate record"
            )
        approval_path = repository / "plant_illustrations/illustration_asset_manifest.csv"
        try:
            approval_rows = _read_csv(approval_path)
            audit.approved_count = sum(
                row.get("approval_status", "").strip().casefold() == "approved"
                for row in approval_rows
            )
        except (OSError, UnicodeError, csv.Error) as error:
            audit.errors.append(f"Cannot read plant illustration approval manifest: {error}")
    else:
        missing_sources = [
            row.get(id_field, "")
            for row in rows
            if not row.get("source_references", "").strip()
        ]
        if missing_sources:
            audit.errors.append(
                f"{len(missing_sources)} figure(s) lack source references"
            )
        audit.approved_count = sum(
            row.get("approval_status", "").strip().casefold() == "approved"
            for row in rows
        )
        if audit.approved_count < len(rows):
            audit.warnings.append(
                f"{len(rows) - audit.approved_count} figure(s) remain unapproved"
            )

    _verify_files(manifest_path, rows, filename_field, hash_field, audit)
    return audit


def pending_review(repository: Path, plant_id: str | None = None) -> list[dict[str, str]]:
    path = repository / "plant_illustrations/concept_candidates/candidate_manifest.csv"
    rows = _read_csv(path)
    return [
        row
        for row in rows
        if row.get("approval_status", "").strip().casefold() != "approved"
        and (not plant_id or row.get("plant_id", "") == plant_id)
    ]
