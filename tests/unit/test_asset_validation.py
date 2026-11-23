from __future__ import annotations

import csv
import hashlib
from pathlib import Path

from gardening.assets import audit_assets


def _write_csv(path: Path, fields: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def test_plant_candidate_audit_checks_registry_ids_and_file_hashes(tmp_path: Path) -> None:
    asset_dir = tmp_path / "plant_illustrations" / "concept_candidates"
    asset_dir.mkdir(parents=True)
    image = asset_dir / "leaf.png"
    image.write_bytes(b"candidate image")
    digest = hashlib.sha256(image.read_bytes()).hexdigest()
    _write_csv(
        tmp_path / "plant_registry.csv",
        ["plant_id"],
        [{"plant_id": "plant-example"}],
    )
    _write_csv(
        asset_dir / "candidate_manifest.csv",
        ["plant_id", "filename", "sha256"],
        [{"plant_id": "plant-example", "filename": image.name, "sha256": digest}],
    )
    _write_csv(
        tmp_path / "plant_illustrations" / "illustration_asset_manifest.csv",
        ["plant_id", "approval_status"],
        [{"plant_id": "plant-example", "approval_status": "not-approved"}],
    )

    result = audit_assets(tmp_path, "plant")

    assert result.errors == []
    assert result.record_count == 1
    assert result.checked_files == 1
    assert result.approved_count == 0


def test_figure_audit_fails_missing_sources_and_checksum_mismatch(tmp_path: Path) -> None:
    figure_dir = tmp_path / "educational_figures"
    figure_dir.mkdir()
    image = figure_dir / "figure.png"
    image.write_bytes(b"figure")
    _write_csv(
        figure_dir / "figure_manifest.csv",
        ["figure_id", "filename", "sha256", "source_references", "approval_status"],
        [
            {
                "figure_id": "FIG-001",
                "filename": image.name,
                "sha256": "0" * 64,
                "source_references": "",
                "approval_status": "CONCEPT_PENDING_REVIEW",
            }
        ],
    )

    result = audit_assets(tmp_path, "figure")

    assert result.exit_code == 1
    assert any("lack source references" in error for error in result.errors)
    assert any("checksum mismatch" in error for error in result.errors)
