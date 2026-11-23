import csv
import hashlib

import pytest
from pypdf import PdfWriter

import build_project_reports
from build_project_reports import (
    action_types_for_entry,
    build_calendar_outputs,
    build_illustration_manifest,
    plant_id,
)
from validate_pipeline import HASHED_SOURCE_FILES, REQUIRED_INPUTS, validate_inputs, validate_source_hashes
from pathlib import Path


def write_source_hashes(base_dir):
    lines = []
    for filename in HASHED_SOURCE_FILES:
        digest = hashlib.sha256((base_dir / filename).read_bytes()).hexdigest()
        lines.append(f"{digest}  {filename}")
    (base_dir / "SOURCE_SHA256SUMS.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_stable_plant_ids_are_normalized() -> None:
    assert plant_id("Clematis Group 3") == "plant-clematis-group-3"


def test_calendar_action_classifier_uses_transcribed_row_and_separates_observations() -> None:
    peas = action_types_for_entry(
        {
            "row_text": "Peas — Wk 3–4 (cold-tolerant) direct sow",
            "direct_sow_or_transplant": "",
            "harvest_bloom_action": "",
        }
    )
    icon_marked_sowing = action_types_for_entry(
        {
            "row_text": "Peas — Wk 3–4 (cold-tolerant) 🌿",
            "direct_sow_or_transplant": "Wk 3–4 (cold-tolerant) 🌿",
            "harvest_bloom_action": "",
        }
    )
    dormant = action_types_for_entry(
        {
            "row_text": "Rhubarb — Fully dormant",
            "direct_sow_or_transplant": "",
            "harvest_bloom_action": "",
        }
    )

    assert peas == ["direct-sowing"]
    assert icon_marked_sowing == ["direct-sowing"]
    assert dormant == ["seasonal-observation"]


def test_illustration_rebuild_preserves_review_data_and_rejects_record_loss(tmp_path, monkeypatch):
    monkeypatch.setattr(build_project_reports, "BASE_DIR", tmp_path)
    (tmp_path / "plant_illustrations").mkdir()
    registry = [{"display_name": "Iris", "latin_name": "Iris germanica"}]
    build_illustration_manifest(registry)
    manifest = tmp_path / "plant_illustrations" / "illustration_manifest.csv"
    with manifest.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows[0].update(
        filename="IRIS.png",
        image_source="original",
        creator="Artist",
        license="CC0",
        review_status="reviewed",
        approval_status="approved",
        reviewer_notes="Compared against cited specimens",
    )
    with manifest.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=build_project_reports.ILLUSTRATION_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    build_illustration_manifest(registry + [{"display_name": "Rose"}])
    with manifest.open(encoding="utf-8", newline="") as handle:
        result = list(csv.DictReader(handle))
    assert result[0] == rows[0]
    assert result[1]["approval_status"] == "not-approved"
    before = manifest.read_bytes()
    with pytest.raises(ValueError, match="absent from registry"):
        build_illustration_manifest(registry)
    assert manifest.read_bytes() == before


def test_calendar_build_preserves_grouped_transcriptions_without_plant_assignment(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(build_project_reports, "BASE_DIR", tmp_path)
    entries = [
        {
            "month": "MARCH",
            "page_type": "edibles",
            "section": "VEGETABLES",
            "page_number": "4",
            "plant_text": "Arugula",
            "row_text": "Arugula — Direct sow",
            "indoor_sow": "",
            "direct_sow_or_transplant": "Direct sow",
            "harvest_bloom_action": "",
        },
        {
            "month": "MARCH",
            "page_type": "edibles",
            "section": "VEGETABLES",
            "page_number": "4",
            "plant_text": "Radish / Arugula",
            "row_text": "Radish / Arugula — Direct sow",
            "indoor_sow": "",
            "direct_sow_or_transplant": "Direct sow",
            "harvest_bloom_action": "",
        },
    ]
    registry = [{"display_name": "Arugula"}]

    build_calendar_outputs(entries, registry)

    with (tmp_path / "calendar_actions.csv").open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    with (tmp_path / "calendar_review.csv").open(encoding="utf-8", newline="") as handle:
        review_rows = list(csv.DictReader(handle))
    assert rows[0]["plant_id"] == "plant-arugula"
    assert rows[0]["action_types"] == "direct-sowing"
    assert rows[0]["verification_status"] == "pending-verification"
    assert rows[0]["interpretation_status"] == "source-transcription; not a recommendation"
    assert rows[1]["plant_id"] == ""
    assert rows[1]["grouped_plant_text"] == "true"
    assert len(review_rows) == len(entries)
    assert "individual timing not established" in review_rows[1]["review_reasons"]


def test_source_count_guard_detects_record_loss(tmp_path) -> None:
    for name in REQUIRED_INPUTS:
        if name.endswith(".pdf"):
            continue
        (tmp_path / name).write_bytes(b"source")
    writer = PdfWriter()
    for _ in range(5):
        writer.add_blank_page(width=100, height=100)
    with (tmp_path / "Errington BC Zone 8a Planting Calendar.pdf").open("wb") as handle:
        writer.write(handle)
    (tmp_path / "plant_registry.csv").write_text(
        "display_name\nArugula\n", encoding="utf-8"
    )
    (tmp_path / "errington_calendar_entries.csv").write_text(
        "month,page_type,section,page_number,plant_text,plant_normalized,row_text\n"
        "MARCH,edibles,VEGETABLES,4,Arugula,ARUGULA,Arugula\n",
        encoding="utf-8",
    )
    write_source_hashes(tmp_path)

    counts = validate_inputs(tmp_path, check_snapshot=False)

    assert counts == {
        "plant_records": 1,
        "calendar_entries": 1,
        "calendar_months": 1,
    }
    with pytest.raises(ValueError, match="record count changed"):
        validate_inputs(tmp_path)


def test_source_validation_rejects_bad_calendar_month(tmp_path) -> None:
    for name in REQUIRED_INPUTS:
        if name.endswith(".pdf"):
            continue
        (tmp_path / name).write_bytes(b"source")
    writer = PdfWriter()
    for _ in range(5):
        writer.add_blank_page(width=100, height=100)
    with (tmp_path / "Errington BC Zone 8a Planting Calendar.pdf").open("wb") as handle:
        writer.write(handle)
    (tmp_path / "plant_registry.csv").write_text(
        "display_name\nArugula\n", encoding="utf-8"
    )
    (tmp_path / "errington_calendar_entries.csv").write_text(
        "month,page_type,section,page_number,plant_text,plant_normalized,row_text\n"
        "FROSTMONTH,edibles,VEGETABLES,4,Arugula,ARUGULA,Arugula\n",
        encoding="utf-8",
    )
    write_source_hashes(tmp_path)

    with pytest.raises(ValueError, match="Invalid calendar months"):
        validate_inputs(tmp_path, check_snapshot=False)


def test_source_hash_guard_detects_changed_original(tmp_path) -> None:
    for filename in HASHED_SOURCE_FILES:
        (tmp_path / filename).write_bytes(filename.encode("utf-8"))
    write_source_hashes(tmp_path)

    validate_source_hashes(tmp_path)
    (tmp_path / "plant_registry.csv").write_text("changed", encoding="utf-8")

    with pytest.raises(ValueError, match="Protected source files changed"):
        validate_source_hashes(tmp_path)


def test_generated_asset_counts_cover_registry_and_figure_library() -> None:
    candidate_dir = Path("plant_illustrations/concept_candidates")
    candidates = list(candidate_dir.glob("*.png"))
    manifests = list(candidate_dir.glob("*.json"))
    figures = list(Path("educational_figures").glob("FIG-*.png"))
    with Path("plant_registry.csv").open(encoding="utf-8-sig", newline="") as handle:
        registry_count = sum(1 for _ in csv.DictReader(handle))
    assert len(candidates) == registry_count == 137
    assert len(manifests) == registry_count
    assert len(figures) == 36


def test_reenie_beanie_font_is_bundled() -> None:
    font = Path("fonts/ReenieBeanie.ttf")
    license_file = Path("fonts/OFL-ReenieBeanie.txt")
    assert font.is_file()
    assert font.stat().st_size > 100000
    assert "SIL OPEN FONT LICENSE" in license_file.read_text(encoding="utf-8")
