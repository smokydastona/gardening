from __future__ import annotations

import argparse
import csv
import hashlib
import math
import re
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

from gardening.config import find_repository_root


EXPECTED_COUNTS = {
    "plant_registry.csv": 137,
    "errington_calendar_entries.csv": 359,
}
MONTHS = {
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
}
REQUIRED_INPUTS = (
    "plant_registry.csv",
    "errington_calendar_entries.csv",
    "SOURCE_SHA256SUMS.txt",
    "Errington BC Zone 8a Planting Calendar.pdf",
    "Planting Calander-Crops.png",
    "Planting Calander-Ornamentals.png",
    "cover.png",
    "ERRINGTON_CALENDAR_FULL_TEXT.md",
    "ERRINGTON_ENCYCLOPEDIA_HANDOFF.md",
    "ERRINGTON_COMPLETE_SUPPLEMENT.md",
)
HASHED_SOURCE_FILES = (
    "Errington BC Zone 8a Planting Calendar.pdf",
    "Planting Calander-Crops.png",
    "Planting Calander-Ornamentals.png",
    "plant_registry.csv",
    "errington_calendar_entries.csv",
    "ERRINGTON_CALENDAR_FULL_TEXT.md",
    "claims/CLAIM_SOURCES.csv",
)

RELEASE_PDFS = (
    "Errington_Gardening_Encyclopedia.pdf",
    "Errington_Monthly_Gardening_Guide.pdf",
    "Errington_Illustrated_Plant_Directory.pdf",
    "Errington_Botanical_Illustration_Collection.pdf",
    "Errington_Educational_Figure_Collection.pdf",
)
HANDWRITING_FONTS = frozenset(
    ("IndieFlower-Regular", "ArchitectsDaughter-Regular", "ReenieBeanie")
)
NOTE_LABEL = re.compile(r"^(?:Note|Remember|Check|For later|In the margin):\s+\S")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_source_hashes(base_dir: Path) -> None:
    manifest_path = base_dir / "SOURCE_SHA256SUMS.txt"
    expected: dict[str, str] = {}
    for line_number, line in enumerate(manifest_path.read_text(encoding="utf-8").splitlines(), 1):
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            raise ValueError(f"Invalid source hash manifest line {line_number}")
        digest, filename = match.groups()
        if filename in expected:
            raise ValueError(f"Duplicate source hash entry: {filename}")
        expected[filename] = digest

    if set(expected) != set(HASHED_SOURCE_FILES):
        missing = sorted(set(HASHED_SOURCE_FILES) - set(expected))
        unexpected = sorted(set(expected) - set(HASHED_SOURCE_FILES))
        raise ValueError(
            "Source hash manifest entries do not match the protected source set; "
            f"missing={missing}, unexpected={unexpected}"
        )

    changed = []
    for filename in HASHED_SOURCE_FILES:
        path = base_dir / filename
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected[filename]:
            changed.append(filename)
    if changed:
        raise ValueError("Protected source files changed: " + ", ".join(changed))


def validate_inputs(base_dir: Path, check_snapshot: bool = True) -> dict[str, int]:
    missing = [name for name in REQUIRED_INPUTS if not (base_dir / name).is_file()]
    if missing:
        raise ValueError(f"Missing required source inputs: {', '.join(missing)}")
    validate_source_hashes(base_dir)

    registry = read_csv(base_dir / "plant_registry.csv")
    calendar = read_csv(base_dir / "errington_calendar_entries.csv")
    if not registry or not calendar:
        raise ValueError("Plant registry and calendar transcription must not be empty.")

    counts = {
        "plant_registry.csv": len(registry),
        "errington_calendar_entries.csv": len(calendar),
    }
    if check_snapshot:
        changed = [
            f"{name}: expected {expected}, found {counts[name]}"
            for name, expected in EXPECTED_COUNTS.items()
            if counts[name] != expected
        ]
        if changed:
            raise ValueError(
                "Source record count changed without an explicit snapshot update: "
                + "; ".join(changed)
            )

    plant_names = [row.get("display_name", "").strip().casefold() for row in registry]
    duplicates = sorted(name for name, count in Counter(plant_names).items() if name and count > 1)
    if any(not name for name in plant_names):
        raise ValueError("Plant registry contains a blank display_name.")
    if duplicates:
        raise ValueError(f"Duplicate plant display names: {', '.join(duplicates)}")
    stable_ids = [
        "plant-" + re.sub(r"[^A-Za-z0-9]+", "-", row["display_name"]).strip("-").lower()
        for row in registry
    ]
    if "plant_id" in registry[0]:
        mismatched_ids = [
            row["display_name"]
            for row in registry
            if row.get("plant_id", "").strip()
            != "plant-" + re.sub(r"[^A-Za-z0-9]+", "-", row["display_name"]).strip("-").lower()
        ]
        if mismatched_ids:
            raise ValueError(
                "Plant stable IDs do not match display names: "
                + ", ".join(mismatched_ids[:20])
            )
    duplicate_ids = sorted(
        plant_id for plant_id, count in Counter(stable_ids).items() if count > 1
    )
    if duplicate_ids:
        raise ValueError(f"Plant names produce duplicate stable IDs: {', '.join(duplicate_ids)}")

    required_calendar_fields = {
        "month",
        "page_type",
        "section",
        "page_number",
        "plant_text",
        "plant_normalized",
        "row_text",
    }
    missing_fields = required_calendar_fields - set(calendar[0])
    if missing_fields:
        raise ValueError(
            "Calendar transcription is missing required columns: "
            + ", ".join(sorted(missing_fields))
        )
    blank_entries = [
        str(index)
        for index, row in enumerate(calendar, start=2)
        if any(not row.get(field, "").strip() for field in required_calendar_fields)
    ]
    if blank_entries:
        raise ValueError(
            "Calendar transcription has incomplete required values on CSV rows: "
            + ", ".join(blank_entries[:20])
        )

    invalid_months = sorted({row["month"] for row in calendar if row["month"] not in MONTHS})
    if invalid_months:
        raise ValueError(f"Invalid calendar months: {', '.join(invalid_months)}")
    invalid_pages = []
    for index, row in enumerate(calendar, start=2):
        try:
            page_number = int(row["page_number"])
        except ValueError:
            invalid_pages.append(str(index))
            continue
        if page_number < 1:
            invalid_pages.append(str(index))
    if invalid_pages:
        raise ValueError(
            "Calendar transcription has invalid page numbers on CSV rows: "
            + ", ".join(invalid_pages[:20])
        )
    calendar_pdf = PdfReader(str(base_dir / "Errington BC Zone 8a Planting Calendar.pdf"))
    page_count = len(calendar_pdf.pages)
    pages_out_of_range = [
        row["page_number"]
        for row in calendar
        if int(row["page_number"]) > page_count
    ]
    if pages_out_of_range:
        raise ValueError(
            f"Calendar references pages outside the {page_count}-page source PDF: "
            + ", ".join(sorted(set(pages_out_of_range)))
        )
    entry_keys = [
        (
            row["month"],
            row["page_type"],
            row["section"],
            row["plant_normalized"],
            row["row_text"],
        )
        for row in calendar
    ]
    duplicate_entries = [
        key for key, count in Counter(entry_keys).items() if count > 1
    ]
    if duplicate_entries:
        raise ValueError(
            f"Duplicate calendar entry keys found: {len(duplicate_entries)}"
        )

    return {
        "plant_records": len(registry),
        "calendar_entries": len(calendar),
        "calendar_months": len({row["month"] for row in calendar}),
    }


def validate_annotation_theme(reader: PdfReader) -> None:
    notes: list[tuple[int, str, str, tuple[float, ...]]] = []
    for page_index, page in enumerate(reader.pages[1:], start=1):
        fill_color: tuple[float, ...] | None = None
        color_stack: list[tuple[float, ...] | None] = []

        def capture_color(operator, operands, _cm, _tm):
            nonlocal fill_color
            if operator == b"q":
                color_stack.append(fill_color)
            elif operator == b"Q" and color_stack:
                fill_color = color_stack.pop()
            elif operator == b"rg":
                fill_color = tuple(round(float(value), 4) for value in operands)
            elif operator in (b"g", b"k"):
                fill_color = None

        def capture_note(text, _cm, _tm, font, font_size):
            if (
                not NOTE_LABEL.match(text.strip())
                or font is None
                or fill_color is None
                or font_size < 10
            ):
                return
            name = str(font.get("/BaseFont", "")).split("+")[-1]
            descriptor = font.get("/FontDescriptor")
            if name not in HANDWRITING_FONTS or not descriptor:
                return
            descriptor = descriptor.get_object()
            if not any(descriptor.get(key) for key in ("/FontFile", "/FontFile2", "/FontFile3")):
                return
            notes.append((page_index, text.strip(), name, fill_color))

        page.extract_text(visitor_text=capture_note, visitor_operand_before=capture_color)

    required_notes = max(5, math.ceil(len(reader.pages) / 10))
    required_pages = max(3, math.ceil(len(reader.pages) / 20))
    note_pages = {note[0] for note in notes}
    if (
        len(notes) < required_notes
        or len(note_pages) < required_pages
        or len({note[1] for note in notes}) < 5
        or not note_pages
        or min(note_pages) > len(reader.pages) * 0.3
        or max(note_pages) < len(reader.pages) * 0.7
    ):
        raise ValueError("Encyclopedia annotation theme gate: too few or poorly distributed notes.")
    if {note[2] for note in notes} != HANDWRITING_FONTS or len({note[3] for note in notes}) < 3:
        raise ValueError(
            "Encyclopedia annotation theme gate: notes require three embedded handwriting fonts "
            "and three distinct ink colors."
        )


def validate_publication(base_dir: Path) -> dict[str, int | str]:
    pdf_path = base_dir / "Errington_Gardening_Encyclopedia.pdf"
    if not pdf_path.is_file():
        raise ValueError(f"Expected publication PDF was not generated: {pdf_path.name}")

    reader = PdfReader(str(pdf_path), strict=True)
    if not reader.pages:
        raise ValueError("Publication PDF has no pages.")
    metadata = reader.metadata or {}
    if metadata.get("/Title") != "Errington Gardening Encyclopedia":
        raise ValueError("Publication PDF title metadata is missing or incorrect.")
    author = str(metadata.get("/Author", ""))
    if not author or "copilot" in author.casefold():
        raise ValueError("Publication PDF must have intentional non-Copilot author metadata.")
    if not reader.pages[0].images:
        raise ValueError("Publication cover image is not embedded in the PDF.")

    page_text = [page.extract_text() or "" for page in reader.pages]
    extracted_text = "\n".join(page_text)
    for required in ("Contents", "Source and verification policy", "Errington"):
        if required.casefold() not in extracted_text.casefold():
            raise ValueError(f"Publication PDF is missing required text: {required}")
    if any(not text.strip() for text in page_text[1:]):
        raise ValueError("Publication PDF contains an empty interior page.")

    def check_outline(items: list) -> int:
        destination_count = 0
        for item in items:
            if isinstance(item, list):
                destination_count += check_outline(item)
                continue
            page_number = reader.get_destination_page_number(item)
            if page_number < 0:
                raise ValueError(f"Invalid table-of-contents destination: {item.title}")
            destination_count += 1
        return destination_count

    outline_entries = check_outline(reader.outline)
    if not outline_entries:
        raise ValueError("Publication PDF has no navigable table-of-contents entries.")

    toc_pages = [
        page for page, text in zip(reader.pages, page_text) if "Contents" in text
    ]
    if len(toc_pages) != 1:
        raise ValueError(
            f"Expected a single table-of-contents page, found {len(toc_pages)}."
        )
    toc_links = []
    for reference in toc_pages[0].get("/Annots", []):
        annotation = reference.get_object()
        destination = annotation.get("/Dest")
        if destination:
            if not isinstance(destination, (list, tuple)) or not destination:
                raise ValueError("Table-of-contents link has an invalid destination.")
            if reader.get_page_number(destination[0]) < 0:
                raise ValueError("Table-of-contents link points to an invalid page.")
            toc_links.append(destination)
    if len(toc_links) < outline_entries:
        raise ValueError(
            "Publication PDF is missing internal links for its table-of-contents entries."
        )

    embedded_font = False
    for page in reader.pages[1:]:
        resources = page.get("/Resources")
        font_resources = resources.get("/Font", {}) if resources else {}
        for reference in font_resources.values():
            font = reference.get_object()
            descriptor = font.get("/FontDescriptor")
            descendants = font.get("/DescendantFonts", [])
            if descriptor is None and descendants:
                descriptor = descendants[0].get_object().get("/FontDescriptor")
            if descriptor and any(
                descriptor.get(key)
                for key in ("/FontFile", "/FontFile2", "/FontFile3")
            ):
                embedded_font = True
                break
        if embedded_font:
            break
    if not embedded_font:
        raise ValueError("Publication PDF has no embedded fonts.")
    validate_annotation_theme(reader)
    return {
        "pdf_pages": len(reader.pages),
        "pdf_bytes": pdf_path.stat().st_size,
        "metadata_author": author,
    }


def validate_publication_set(base_dir: Path) -> dict[str, dict[str, int | str]]:
    results: dict[str, dict[str, int | str]] = {}
    for filename in RELEASE_PDFS:
        if filename == "Errington_Gardening_Encyclopedia.pdf":
            results[filename] = validate_publication(base_dir)
            continue
        path = base_dir / filename
        if not path.is_file():
            raise ValueError(f"Missing publication: {filename}")
        reader = PdfReader(str(path), strict=True)
        if not reader.pages:
            raise ValueError(f"Publication PDF has no pages: {filename}")
        if any(not (page.extract_text() or "").strip() for page in reader.pages[1:]):
            raise ValueError(f"Publication PDF contains an empty page: {filename}")
        metadata = reader.metadata or {}
        author = str(metadata.get("/Author", ""))
        if not author or "copilot" in author.casefold():
            raise ValueError(f"Publication PDF has invalid author metadata: {filename}")
        results[filename] = {
            "pdf_pages": len(reader.pages),
            "pdf_bytes": path.stat().st_size,
            "metadata_author": author,
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate encyclopedia source data and outputs.")
    parser.add_argument("--publication", action="store_true", help="Validate the generated PDF.")
    parser.add_argument(
        "--no-count-snapshot",
        action="store_true",
        help="Skip baseline record-count checks (for an intentional source update).",
    )
    args = parser.parse_args()
    base_dir = find_repository_root(__file__)
    counts = validate_inputs(base_dir, check_snapshot=not args.no_count_snapshot)
    print(
        "Source validation passed: "
        f"{counts['plant_records']} plants, {counts['calendar_entries']} calendar entries, "
        f"{counts['calendar_months']} months."
    )
    if args.publication:
        results = validate_publication_set(base_dir)
        for filename, result in results.items():
            print(
                f"{filename}: {result['pdf_pages']} pages, "
                f"{result['pdf_bytes']} bytes; author={result['metadata_author']}."
            )


if __name__ == "__main__":
    main()
