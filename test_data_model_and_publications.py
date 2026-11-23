import json
import shutil
from pathlib import Path

from pypdf import PdfReader
from PIL import Image

from build_publications import (
    build_botanical_collection_pdf,
    build_directory_pdf,
    build_figure_collection_pdf,
    build_monthly_pdf,
)
from data_model import validate_authoritative_registry
from illustration_assets import ORGANS, keyify, sha256_file, sha256_json


def test_authoritative_registry_counts_and_claim_links() -> None:
    result = validate_authoritative_registry(Path("."))
    assert result["plant_records"] == 137
    assert result["calendar_entries"] == 359
    assert result["claim_records"] >= 1


def test_three_publication_pdf_set(tmp_path: Path) -> None:
    shutil.copy("errington_calendar_entries.csv", tmp_path)
    shutil.copy("calendar_actions.csv", tmp_path)
    shutil.copy("plant_registry.csv", tmp_path)
    shutil.copy("plant_verification_register.csv", tmp_path)
    (tmp_path / "plant_illustrations").mkdir()
    shutil.copy(
        "plant_illustrations/illustration_manifest.csv",
        tmp_path / "plant_illustrations",
    )
    monthly = build_monthly_pdf(tmp_path)
    directory = build_directory_pdf(tmp_path)
    monthly_reader = PdfReader(str(monthly))
    monthly_text = "\n".join(page.extract_text() or "" for page in monthly_reader.pages)
    assert "Wk 3–4 (cold-tolerant)" in monthly_text
    assert "Direct sowing" in monthly_text
    reader = PdfReader(str(directory))
    assert reader.pages
    assert reader.metadata["/Title"] == "Errington Plant Directory — Concept Candidates"
    assert "0 of 137 records have approved illustrations" in reader.pages[0].extract_text()


def test_approved_illustration_is_embedded_in_directory(tmp_path: Path) -> None:
    (tmp_path / "plant_registry.csv").write_text(
        "plant_id,display_name,latin_name,family\n"
        "plant-iris,Iris,Iris germanica,Iridaceae\n",
        encoding="utf-8",
    )
    (tmp_path / "plant_verification_register.csv").write_text(
        "plant_id,taxonomy_status,cultivar_status,illustration_status\n"
        "plant-iris,pending-verification,pending-verification,illustration-approved\n",
        encoding="utf-8",
    )
    illustrations = tmp_path / "plant_illustrations"
    illustrations.mkdir()
    (illustrations / "illustration_manifest.csv").write_text(
        "plant_id,filename,approval_status\nplant-iris,IRIS.png,approved\n",
        encoding="utf-8",
    )
    image_path = illustrations / "IRIS.png"
    Image.new("RGB", (200, 300), "white").save(image_path)
    evidence = {"plant_key": keyify("Iris"), "taxon_verified": True}
    checklist = {field: "pass" for field in ORGANS}
    checklist["style"] = "pass"
    metadata = {
        "schema_version": 1,
        "asset_id": keyify("Iris"),
        "file": image_path.name,
        "status": "human-reviewed-approved",
        "image_sha256": sha256_file(image_path),
        "evidence": evidence,
        "evidence_sha256": sha256_json(evidence),
        "review": {
            "reviewer": "Reviewer",
            "reviewed_at_utc": "2026-01-01T00:00:00Z",
            "notes": "Compared the candidate with cited references.",
            "checklist": checklist,
        },
    }
    image_path.with_suffix(".json").write_text(json.dumps(metadata), encoding="utf-8")

    directory = build_directory_pdf(tmp_path)
    reader = PdfReader(str(directory))
    assert reader.metadata["/Title"] == "Errington Illustrated Plant Directory"
    assert any(page.images for page in reader.pages)


def test_generated_collection_pdfs_exist(tmp_path: Path) -> None:
    shutil.copy("plant_registry.csv", tmp_path)
    shutil.copy("plant_verification_register.csv", tmp_path)
    shutil.copy("errington_calendar_entries.csv", tmp_path)
    (tmp_path / "plant_illustrations").mkdir()
    shutil.copy(
        "plant_illustrations/illustration_manifest.csv",
        tmp_path / "plant_illustrations",
    )
    shutil.copytree(
        "plant_illustrations/concept_candidates",
        tmp_path / "plant_illustrations" / "concept_candidates",
    )
    shutil.copytree(
        "educational_figures",
        tmp_path / "educational_figures",
    )
    botanical = build_botanical_collection_pdf(tmp_path)
    figures = build_figure_collection_pdf(tmp_path)
    assert len(PdfReader(str(botanical)).pages) >= 138
    assert len(PdfReader(str(figures)).pages) == 37
