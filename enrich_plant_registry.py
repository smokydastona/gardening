from __future__ import annotations

import csv
import re
from pathlib import Path


DESCRIPTOR_WORDS = {
    "EARLY",
    "LATE",
    "MAIN",
    "WINTER",
    "SUMMER",
    "SPRING",
    "FALL",
    "FORCED",
    "STORED",
    "BARE",
    "ROOT",
    "ROOTS",
    "NEW",
    "HARDY",
    "ORNAMENTAL",
    "PROTECTED",
    "OVERWINTERING",
    "OVERWINTERED",
}


def normalize(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", text.upper()).strip("_")


def alias_variants(value: str) -> set[str]:
    variants = set()
    if not value:
        return variants
    variants.add(value)
    if value.endswith("S"):
        variants.add(value[:-1])
    else:
        variants.add(f"{value}S")
    if value.endswith("IES"):
        variants.add(f"{value[:-3]}Y")
    if value.endswith("Y"):
        variants.add(f"{value[:-1]}IES")
    return {item for item in variants if item}


def clean_alias_part(part: str) -> str:
    part = re.sub(r"\([^)]*\)", "", part)
    part = part.replace("&", " ")
    words = [word for word in re.split(r"\s+", part.upper()) if word]
    while words and words[0] in DESCRIPTOR_WORDS:
        words.pop(0)
    return normalize(" ".join(words))


def entry_aliases(plant_text: str) -> set[str]:
    raw_parts = re.split(r"/|,", plant_text)
    aliases = {normalize(plant_text)}
    for part in raw_parts:
        cleaned = clean_alias_part(part)
        if cleaned:
            aliases.update(alias_variants(cleaned))
    return aliases


def registry_aliases(row: dict[str, str]) -> set[str]:
    aliases: set[str] = set()
    for key in ("display_name", "source_name", "normalized_name"):
        value = row.get(key, "").strip()
        if value:
            aliases.update(alias_variants(normalize(value)))
    return aliases


def load_calendar_entries(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_registry_row(fieldnames: list[str], row: list[str]) -> list[str]:
    if len(row) == len(fieldnames):
        return row

    maintenance_index = fieldnames.index("maintenance_notes")
    expected_tail_length = len(fieldnames) - maintenance_index
    current_tail_length = len(row) - maintenance_index

    if current_tail_length == expected_tail_length - 2:
        row = row[:maintenance_index] + ["", ""] + row[maintenance_index:]

    if len(row) < len(fieldnames):
        row = row + [""] * (len(fieldnames) - len(row))
    elif len(row) > len(fieldnames):
        row = row[: len(fieldnames)]

    return row


def load_registry_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            fieldnames = next(reader)
        except StopIteration as error:
            raise RuntimeError("Plant registry is empty.") from error

        rows: list[dict[str, str]] = []
        for raw_row in reader:
            normalized_row = normalize_registry_row(fieldnames, raw_row)
            rows.append(dict(zip(fieldnames, normalized_row, strict=True)))
    return rows


def enrich_registry(base_dir: Path) -> list[dict[str, str]]:
    registry_path = base_dir / "plant_registry.csv"
    entries_path = base_dir / "errington_calendar_entries.csv"
    registry_rows = load_registry_rows(registry_path)
    entries = load_calendar_entries(entries_path)
    entry_lookup = [(entry, entry_aliases(entry["plant_text"])) for entry in entries]

    enriched_rows: list[dict[str, str]] = []
    for row in registry_rows:
        aliases = registry_aliases(row)
        matched_entries: list[dict[str, str]] = []
        for entry, entry_alias_set in entry_lookup:
            if aliases & entry_alias_set:
                matched_entries.append(entry)

        months = []
        actions = []
        sections = []
        page_types = []
        for entry in matched_entries:
            if entry["month"] and entry["month"] not in months:
                months.append(entry["month"])
            action = f"{entry['month']}: {entry['row_text']}"
            if action not in actions:
                actions.append(action)
            if entry["section"] and entry["section"] not in sections:
                sections.append(entry["section"])
            if entry["page_type"] and entry["page_type"] not in page_types:
                page_types.append(entry["page_type"])

        enriched = dict(row)
        enriched["calendar_match_count"] = str(len(matched_entries))
        enriched["calendar_months"] = "; ".join(months)
        enriched["calendar_sections"] = "; ".join(sections)
        enriched["calendar_page_types"] = "; ".join(page_types)
        enriched["calendar_actions"] = " || ".join(actions)
        enriched["calendar_match_status"] = "matched" if matched_entries else "unmatched"
        enriched_rows.append(enriched)

    return enriched_rows


def write_enriched_registry(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError("No registry rows available to write.")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    registry_rows = load_registry_rows(base_dir / "plant_registry.csv")
    write_enriched_registry(base_dir / "plant_registry.csv", registry_rows)
    rows = enrich_registry(base_dir)
    write_enriched_registry(base_dir / "plant_registry_enriched.csv", rows)


if __name__ == "__main__":
    main()