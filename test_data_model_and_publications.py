from pathlib import Path

from pypdf import PdfReader

from build_publications import build_directory_pdf, build_monthly_pdf
from data_model import validate_authoritative_registry


def test_authoritative_registry_counts_and_claim_links() -> None:
    result = validate_authoritative_registry(Path("."))
    assert result["plant_records"] == 137
    assert result["calendar_entries"] == 359
    assert result["claim_records"] >= 1


def test_three_publication_pdf_set(tmp_path: Path) -> None:
    import shutil
    shutil.copy("errington_calendar_entries.csv", tmp_path)
    shutil.copy("plant_registry.csv", tmp_path)
    shutil.copy("plant_verification_register.csv", tmp_path)
    monthly = build_monthly_pdf(tmp_path)
    directory = build_directory_pdf(tmp_path)
    assert PdfReader(str(monthly)).pages
    assert PdfReader(str(directory)).pages
