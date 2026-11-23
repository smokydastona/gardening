from pathlib import Path

from pypdf import PdfReader
from PIL import Image
import pytest
from reportlab.pdfgen.canvas import Canvas

import build_final_encyclopedia_pdf as encyclopedia
import validate_pipeline
from build_final_encyclopedia_pdf import (
    OUTPUT_MD,
    SOURCE_FILES,
    build_pdf,
    compile_markdown,
    load_plant_illustrations,
    load_sections,
)
from render_publication import render_publication
from validate_pipeline import validate_publication


def test_compiled_encyclopedia_includes_core_handbook(tmp_path: Path) -> None:
    for _title, file_name, _deck in SOURCE_FILES:
        path = tmp_path / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(f"Content from {file_name}.", encoding="utf-8")

    sections = load_sections(tmp_path)
    compiled = compile_markdown(tmp_path, sections)

    assert "# Core Handbook" in compiled
    assert "Content from ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md." in compiled
    assert "# Grower's Handbook" in compiled
    assert "Content from ERRINGTON_GROWER_HANDBOOK.md." in compiled
    assert (tmp_path / OUTPUT_MD).read_text(encoding="utf-8") == compiled


def test_pdf_build_has_paginated_contents_metadata_and_markdown_formatting(
    tmp_path: Path, monkeypatch
) -> None:
    for title, file_name, _deck in SOURCE_FILES:
        path = tmp_path / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f"# {title}\n\nA **bold** claim and *emphasis*.\n\n"
            "- Parent\n  - Nested child\n\nA wrapped\nparagraph.\n\n"
            "First line.\\\nSecond line.\n\n"
            "| First heading | Second heading |\n|---|---|\n| x | y |\n",
            encoding="utf-8",
        )
    Image.new("RGB", (200, 300), "#f6f0e2").save(tmp_path / "cover.png")
    illustration_dir = tmp_path / "plant_illustrations"
    illustration_dir.mkdir()
    (illustration_dir / "illustration_manifest.csv").write_text(
        "plant_id,filename,approval_status\n", encoding="utf-8"
    )

    output = build_pdf(tmp_path)

    reader = PdfReader(str(output))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert len(reader.pages) >= 5
    toc_pages = [page.extract_text() or "" for page in reader.pages if "Contents" in (page.extract_text() or "")]
    assert len(toc_pages) == 1
    assert "Source and Verification Policy" in toc_pages[0]
    assert "Nested child" in extracted
    assert "A bold claim and emphasis." in extracted
    assert "Grower's Handbook" in extracted
    assert "A wrapped paragraph." in extracted
    assert "First line.\nSecond line." in extracted
    assert "First heading" in extracted
    assert "Second heading" in extracted
    assert reader.metadata["/Title"] == "Errington Gardening Encyclopedia"
    assert "Copilot" not in reader.metadata["/Author"]
    assert reader.outline
    result = validate_publication(tmp_path)
    assert result["pdf_pages"] == len(reader.pages)
    page_count, contact_sheets = render_publication(output, tmp_path / "renders")
    assert page_count == len(reader.pages)
    assert contact_sheets
    assert len(list((tmp_path / "renders").rglob("page-*.png"))) == page_count
    first_build = output.read_bytes()
    build_pdf(tmp_path)
    assert output.read_bytes() == first_build

    original_styles = encyclopedia.NOTE_STYLES
    monochrome = tuple(
        (font, encyclopedia.colors.black, size, angle)
        for font, _ink, size, angle in original_styles
    )
    monkeypatch.setattr(encyclopedia, "NOTE_STYLES", monochrome)
    build_pdf(tmp_path)
    with pytest.raises(ValueError, match="three distinct ink colors"):
        validate_publication(tmp_path)

    one_hand = tuple(
        ("IndieFlower", ink, size, angle) for _font, ink, size, angle in original_styles
    )
    monkeypatch.setattr(encyclopedia, "NOTE_STYLES", one_hand)
    build_pdf(tmp_path)
    with pytest.raises(ValueError, match="three embedded handwriting fonts"):
        validate_publication(tmp_path)

    monkeypatch.setattr(encyclopedia.GardenNote, "draw", lambda self: None)
    build_pdf(tmp_path)
    monkeypatch.setattr(validate_pipeline, "RELEASE_PDFS", (output.name,))
    with pytest.raises(ValueError, match="too few or poorly distributed notes"):
        validate_pipeline.validate_publication_set(tmp_path)


def test_illustration_loader_ignores_unapproved_and_fails_for_missing_approved(tmp_path: Path) -> None:
    directory = tmp_path / "plant_illustrations"
    directory.mkdir()
    manifest = directory / "illustration_manifest.csv"
    manifest.write_text(
        "plant_id,filename,approval_status\n"
        "plant-arugula,ARUGULA.png,pending\n",
        encoding="utf-8",
    )
    assert load_plant_illustrations(tmp_path) == {}

    manifest.write_text(
        "plant_id,filename,approval_status\n"
        "plant-arugula,ARUGULA.png,approved\n",
        encoding="utf-8",
    )
    with pytest.raises(FileNotFoundError, match="ARUGULA.png"):
        load_plant_illustrations(tmp_path)


def test_theme_gate_rejects_notes_confined_to_one_end(tmp_path: Path) -> None:
    encyclopedia.register_fonts()
    pdf = tmp_path / "concentrated-notes.pdf"
    canvas = Canvas(str(pdf))
    for page in range(10):
        if 1 <= page <= 3:
            for item in range(2):
                note = encyclopedia.GardenNote(f"Observation {page}-{item}.", page + item)
                note.wrap(350, 500)
                note.drawOn(canvas, 30, 500 - item * 60)
        canvas.showPage()
    canvas.save()

    with pytest.raises(ValueError, match="poorly distributed notes"):
        validate_pipeline.validate_annotation_theme(PdfReader(str(pdf)))


def test_unapproved_markdown_artwork_is_withheld_from_encyclopedia(tmp_path: Path) -> None:
    for title, file_name, _deck in SOURCE_FILES:
        path = tmp_path / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f"# {title}\n\nText.\n"
        if title == "Plant Field Index and Learning Aids":
            content += "\n**Concept plate:** ![Concept plate](artwork.png)\n"
        path.write_text(content, encoding="utf-8")
    Image.new("RGB", (200, 300), "#f6f0e2").save(tmp_path / "cover.png")
    Image.new("RGB", (80, 120), "#51664e").save(tmp_path / "artwork.png")
    (tmp_path / "plant_illustrations").mkdir()
    (tmp_path / "plant_illustrations" / "illustration_manifest.csv").write_text(
        "plant_id,filename,approval_status\n", encoding="utf-8"
    )

    output = build_pdf(tmp_path)
    reader = PdfReader(str(output))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)

    assert sum(len(page.images) for page in reader.pages) == 1
    assert "Artwork withheld pending independent botanical and rights review." in extracted


def test_missing_markdown_artwork_fails_pdf_build(tmp_path: Path) -> None:
    for title, file_name, _deck in SOURCE_FILES:
        path = tmp_path / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        content = f"# {title}\n\nText.\n"
        if title == "Plant Field Index and Learning Aids":
            content += "\n![Missing plate](missing.png)\n"
        path.write_text(content, encoding="utf-8")
    Image.new("RGB", (200, 300), "#f6f0e2").save(tmp_path / "cover.png")
    (tmp_path / "plant_illustrations").mkdir()
    (tmp_path / "plant_illustrations" / "illustration_manifest.csv").write_text(
        "plant_id,filename,approval_status\n", encoding="utf-8"
    )

    with pytest.raises(FileNotFoundError, match="Markdown image is missing"):
        build_pdf(tmp_path)
