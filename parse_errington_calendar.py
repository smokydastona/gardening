from __future__ import annotations

import csv
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path

from pypdf import PdfReader


MONTH_NAMES = [
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
]

EDIBLE_SECTIONS = [
    "VEGETABLES",
    "HERBS",
    "FRUITS & BERRIES",
    "ROOTS & TUBERS",
    "LEGUMES & GRAINS",
    "PERENNIAL EDIBLES",
]

ORNAMENTAL_SECTIONS = [
    "ANNUAL FLOWERS",
    "HARDY PERENNIALS",
    "BULBS & CORMS",
    "SHRUBS & TREES (Ornamental)",
    "CLIMBING VINES",
    "BC NATIVE PLANTS",
    "CUT FLOWERS",
]

SECTION_HEADINGS = set(EDIBLE_SECTIONS + ORNAMENTAL_SECTIONS)

PAGE_MARKERS = {
    "PAGE A  ·  EDIBLE CROPS": "edibles",
    "PAGE B  ·  FLOWERS & ORNAMENTALS": "ornamentals",
}

HEADER_PREFIXES = (
    "Crop  ",
    "Herb  ",
    "Fruit  ",
    "Plant  ",
    "Indoor Sow",
    "Transplant",
    "Harvest / Action",
    "Bloom / Action",
)

START_TOKENS = (
    "Wk ",
    "Late ",
    "Early ",
    "Mid ",
    "Pot up ",
    "Direct sow ",
    "Divide ",
    "Blooming ",
    "Check ",
    "Nothing ",
    "Fully ",
    "Light ",
    "Order ",
    "Main ",
    "Last ",
    "Harvest ",
    "Sow ",
    "Plant ",
    "Buds ",
    "Crown ",
    "Still ",
    "Too ",
    "Emerging ",
    "Prune ",
    "Bring ",
)

MONTH_RANGE_PATTERN = re.compile(r"^(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[A-Za-z–\- ]*$")

PLANT_SPLIT_PATTERN = re.compile(
    r"\s(?=(Wk\s|Late\s|Early\s|Mid\s|Pot up\s|Direct sow\s|Divide\s|Blooming\s|Check\s|Nothing\s|Fully\s|Light\s|Order\s|Main\s|Last\s|Harvest\s|Sow\s|Plant\s|Buds\s|Crown\s|Still\s|Too\s|Emerging\s|✄|🌾|🌸|🍅|❄|—))"
)


@dataclass
class CalendarEntry:
    month: str
    page_type: str
    section: str
    page_number: int
    plant_text: str
    plant_normalized: str
    row_text: str
    indoor_sow: str
    direct_sow_or_transplant: str
    harvest_bloom_action: str


def normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def normalize_heading(text: str) -> str:
    cleaned = normalize_whitespace(text)
    cleaned = cleaned.replace("LEGUMES & GRAINS", "LEGUMES & GRAINS")
    cleaned = cleaned.replace("LEGUMES  & GRAINS", "LEGUMES & GRAINS")
    return cleaned


def normalize_plant_name(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", text.upper()).strip("_")


def extract_month(lines: list[str]) -> str | None:
    for line in lines:
        if line in MONTH_NAMES:
            return line
    return None


def extract_page_type(lines: list[str]) -> str | None:
    for line in lines:
        if "PAGE A" in line and "EDIBLE CROPS" in line:
            return "edibles"
        if "PAGE B" in line and "FLOWERS" in line:
            return "ornamentals"
    return None


def extract_frost_note(lines: list[str]) -> str:
    for index, line in enumerate(lines):
        if line.startswith("FROST RISK"):
            note = [line]
            cursor = index + 1
            while cursor < len(lines):
                candidate = lines[cursor]
                if candidate in MONTH_NAMES or candidate in PAGE_MARKERS or candidate in SECTION_HEADINGS:
                    break
                if any(candidate.startswith(prefix) for prefix in HEADER_PREFIXES):
                    break
                note.append(candidate)
                if candidate.endswith("."):
                    break
                cursor += 1
            return normalize_whitespace(" ".join(note))
    return ""


def should_skip_line(line: str) -> bool:
    if not line:
        return True
    if line in MONTH_NAMES or line in PAGE_MARKERS or line in SECTION_HEADINGS:
        return True
    if line.startswith("Errington, BC") or line.startswith("Page "):
        return True
    if line == "❄":
        return True
    if line.startswith("LEGEND:") or line.startswith("🌍") or line.startswith("|"):
        return True
    if "Monthly Tips" in line:
        return True
    if any(line.startswith(prefix) for prefix in HEADER_PREFIXES):
        return True
    if "Indoor Sow🌍" in line and "Direct Sow / 🌿" in line:
        return True
    if line in {"Transplant", "Harvest / Action🌾", "Bloom / Action🌸"}:
        return True
    return False


def looks_like_new_row(line: str, buffer: list[str]) -> bool:
    if not buffer:
        return True
    prior = normalize_whitespace(" ".join(buffer))
    if not ("—" in prior or "Wk " in prior or "Blooming" in prior or "Direct sow" in prior or "Pot up" in prior):
        return False
    if line.startswith(START_TOKENS):
        return False
    if MONTH_RANGE_PATTERN.match(line):
        return False
    if re.match(r"^[a-z]", line):
        return False
    if re.match(r"^[A-Z0-9][A-Za-z0-9(/'’ -].*", line):
        return True
    return False


def join_row_text(parts: list[str]) -> str:
    return normalize_whitespace(" ".join(parts))


def extract_plant_and_remainder(text: str) -> tuple[str, str]:
    split = PLANT_SPLIT_PATTERN.split(text, maxsplit=1)
    if len(split) >= 3:
        plant = split[0].strip()
        remainder = text[len(plant) :].strip()
        return plant, remainder
    if "—" in text:
        plant, remainder = text.split("—", 1)
        return plant.strip(), f"— {remainder.strip()}"
    return text.strip(), ""


def parse_row_columns(row_text: str) -> tuple[str, str, str, str]:
    plant_text, remainder = extract_plant_and_remainder(row_text)
    indoor_sow = ""
    direct_sow_or_transplant = ""
    harvest_bloom_action = ""

    if not remainder:
        return plant_text, indoor_sow, direct_sow_or_transplant, harvest_bloom_action

    if remainder.startswith("—"):
        parts = [part.strip() for part in re.split(r"\s*—\s*", remainder) if part.strip()]
        if len(parts) == 1:
            if row_text.rstrip().endswith("—"):
                direct_sow_or_transplant = parts[0]
            else:
                harvest_bloom_action = parts[0]
        elif len(parts) == 2:
            direct_sow_or_transplant = parts[0]
            harvest_bloom_action = parts[1]
        elif len(parts) >= 3:
            indoor_sow = parts[0]
            direct_sow_or_transplant = parts[1]
            harvest_bloom_action = " — ".join(parts[2:])
    else:
        first_dash = [part.strip() for part in re.split(r"\s*—\s*", remainder) if part.strip()]
        if len(first_dash) == 0:
            indoor_sow = remainder
        elif len(first_dash) == 1:
            indoor_sow = first_dash[0]
        elif len(first_dash) == 2:
            indoor_sow = first_dash[0]
            harvest_bloom_action = first_dash[1]
        else:
            indoor_sow = first_dash[0]
            direct_sow_or_transplant = first_dash[1]
            harvest_bloom_action = " — ".join(first_dash[2:])

    return plant_text, indoor_sow, direct_sow_or_transplant, harvest_bloom_action


def parse_section_rows(lines: list[str]) -> list[str]:
    rows: list[str] = []
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        if buffer:
            rows.append(join_row_text(buffer))
            buffer = []

    for line in lines:
        if should_skip_line(line):
            continue
        if looks_like_new_row(line, buffer):
            flush()
            buffer = [line]
        else:
            buffer.append(line)

    flush()
    return rows


def parse_page(page_number: int, text: str) -> tuple[dict[str, str], list[CalendarEntry]]:
    raw_lines = [normalize_heading(line.strip()) for line in text.splitlines()]
    lines = [line for line in raw_lines if line]
    month = extract_month(lines)
    page_type = extract_page_type(lines)
    frost_note = extract_frost_note(lines)
    metadata = {
        "month": month or "",
        "page_type": page_type or "",
        "page_number": str(page_number),
        "frost_note": frost_note,
    }

    entries: list[CalendarEntry] = []
    current_section: str | None = None
    section_lines: list[str] = []

    def flush_section() -> None:
        nonlocal current_section, section_lines
        if not current_section:
            return
        for row_text in parse_section_rows(section_lines):
            plant_text, indoor_sow, direct_sow_or_transplant, harvest_bloom_action = parse_row_columns(row_text)
            entries.append(
                CalendarEntry(
                    month=metadata["month"],
                    page_type=metadata["page_type"],
                    section=current_section,
                    page_number=page_number,
                    plant_text=plant_text,
                    plant_normalized=normalize_plant_name(plant_text),
                    row_text=row_text,
                    indoor_sow=indoor_sow,
                    direct_sow_or_transplant=direct_sow_or_transplant,
                    harvest_bloom_action=harvest_bloom_action,
                )
            )
        section_lines = []

    for line in lines:
        if line in SECTION_HEADINGS:
            flush_section()
            current_section = line
            continue
        if "Monthly Tips" in line or line.startswith("LEGEND:"):
            flush_section()
            current_section = None
            continue
        if current_section:
            section_lines.append(line)

    flush_section()
    return metadata, entries


def parse_pdf(pdf_path: Path) -> tuple[list[dict[str, str]], list[CalendarEntry]]:
    reader = PdfReader(str(pdf_path))
    page_meta: list[dict[str, str]] = []
    entries: list[CalendarEntry] = []
    current_month = ""
    current_page_type = ""
    for page_index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        metadata, page_entries = parse_page(page_index, text)
        if metadata["month"]:
            current_month = metadata["month"]
        else:
            metadata["month"] = current_month
        if metadata["page_type"]:
            current_page_type = metadata["page_type"]
        else:
            metadata["page_type"] = current_page_type
        if metadata["month"]:
            page_meta.append(metadata)
        for entry in page_entries:
            if not entry.month:
                entry.month = metadata["month"]
            if not entry.page_type:
                entry.page_type = metadata["page_type"]
        entries.extend(page_entries)
    return page_meta, entries


def write_entries_csv(output_path: Path, entries: list[CalendarEntry]) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(asdict(entries[0]).keys()))
        writer.writeheader()
        for entry in entries:
            writer.writerow(asdict(entry))


def write_entries_json(output_path: Path, page_meta: list[dict[str, str]], entries: list[CalendarEntry]) -> None:
    payload = {
        "page_meta": page_meta,
        "entries": [asdict(entry) for entry in entries],
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def aggregate_entries(entries: list[CalendarEntry]) -> list[dict[str, str]]:
    aggregated: dict[str, dict[str, str]] = {}
    for entry in entries:
        bucket = aggregated.setdefault(
            entry.plant_normalized,
            {
                "plant_normalized": entry.plant_normalized,
                "plant_text": entry.plant_text,
                "page_type": entry.page_type,
                "section": entry.section,
                "months": "",
                "entry_count": "0",
                "actions": "",
            },
        )
        month_list = [part for part in bucket["months"].split("; ") if part]
        if entry.month and entry.month not in month_list:
            month_list.append(entry.month)
            bucket["months"] = "; ".join(month_list)
        actions = [part for part in bucket["actions"].split(" || ") if part]
        action_text = f"{entry.month}: {entry.row_text}"
        if action_text not in actions:
            actions.append(action_text)
            bucket["actions"] = " || ".join(actions)
        bucket["entry_count"] = str(int(bucket["entry_count"]) + 1)
    return sorted(aggregated.values(), key=lambda current: current["plant_text"])


def write_aggregate_csv(output_path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        return
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    pdf_path = base_dir / "Errington BC Zone 8a Planting Calendar.pdf"
    page_meta, entries = parse_pdf(pdf_path)
    if not entries:
        raise RuntimeError("No calendar entries were parsed from the Errington PDF.")
    write_entries_csv(base_dir / "errington_calendar_entries.csv", entries)
    write_entries_json(base_dir / "errington_calendar_entries.json", page_meta, entries)
    write_aggregate_csv(base_dir / "errington_calendar_plant_summary.csv", aggregate_entries(entries))


if __name__ == "__main__":
    main()