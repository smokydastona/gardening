from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MONTHS = (
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
)
ACTION_ORDER = (
    "indoor-sowing",
    "direct-sowing",
    "transplanting",
    "succession-sowing",
    "harvesting",
    "flowering",
    "pruning",
    "dividing",
    "propagation",
    "seasonal-maintenance",
    "unclassified",
)
CALENDAR_SOURCE_ID = "ERRINGTON-CALENDAR-PDF"
CALENDAR_SOURCE_PATH = "Errington BC Zone 8a Planting Calendar.pdf"
CALENDAR_ACTION_COLUMNS = (
    "source_id",
    "source_path",
    "source_title",
    "source_author",
    "publication_date",
    "access_date",
    "page_number",
    "month",
    "page_type",
    "section",
    "plant_text",
    "plant_id",
    "source_transcription",
    "evidence_type",
    "action_types",
    "classification_method",
    "editorial_interpretation",
    "confidence",
    "verification_status",
    "interpretation_status",
    "grouped_plant_text",
)
CALENDAR_REVIEW_COLUMNS = (
    "source_id",
    "source_path",
    "page_number",
    "month",
    "page_type",
    "section",
    "plant_text",
    "source_transcription",
    "review_reasons",
)
PLANT_REGISTER_COLUMNS = (
    "plant_id",
    "common_name",
    "botanical_name_as_recorded",
    "family_as_recorded",
    "source_id",
    "source_path",
    "source_title",
    "source_author",
    "publication_date",
    "access_date",
    "page_or_section",
    "evidence_type",
    "relevant_transcription",
    "editorial_interpretation",
    "confidence",
    "source_status",
    "taxonomy_status",
    "cultivar_status",
    "profile_status",
    "timing_status",
    "illustration_status",
)
ILLUSTRATION_COLUMNS = (
    "plant_id",
    "filename",
    "common_name",
    "botanical_name_as_recorded",
    "image_source",
    "creator",
    "license",
    "generation_status",
    "review_status",
    "approval_status",
    "reviewer_notes",
)


def read_csv(filename: str) -> list[dict[str, str]]:
    with (BASE_DIR / filename).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(filename: str, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with (BASE_DIR / filename).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def normalize_key(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", text.upper()).strip("_")


def plant_id(name: str) -> str:
    return f"plant-{normalize_key(name).lower().replace('_', '-')}"


def action_types_for_entry(entry: dict[str, str]) -> list[str]:
    found: set[str] = set()
    indoor_text = entry.get("indoor_sow", "").strip()
    direct_text = entry.get("direct_sow_or_transplant", "").strip().casefold()
    action_text = entry.get("harvest_bloom_action", "").strip().casefold()
    checks = (
        ("succession-sowing", r"\bsuccession\b"),
        ("direct-sowing", r"\bdirect sow\b|\bsow outdoors?\b"),
        ("transplanting", r"\btransplant(?:ing)?\b|\bplant out\b"),
        ("harvesting", r"\bharvest(?:ing)?\b|\bpick(?:ing)?\b"),
        ("flowering", r"\bbloom(?:ing)?\b|\bflower(?:ing)?\b"),
        ("pruning", r"\bprun(?:e|ing)\b|\bdeadhead(?:ing)?\b"),
        ("dividing", r"\bdivid(?:e|ing)\b"),
        ("propagation", r"\bpropagat(?:e|ion|ing)\b|\bcuttings?\b|\blayering\b"),
    )
    if indoor_text:
        found.add("indoor-sowing")
    for action, pattern in checks:
        if re.search(pattern, direct_text):
            found.add(action)
        if re.search(pattern, action_text):
            found.add(action)
    if direct_text and not any(re.search(pattern, direct_text) for _action, pattern in checks):
        found.add("unclassified")
    if action_text and not any(re.search(pattern, action_text) for _action, pattern in checks):
        if re.search(
            r"\b(mulch|water|weed|support|feed|protect|check|plan|order|"
            r"clean|remove|leave|allow|store|cover|stake|cut back)\w*\b",
            action_text,
        ):
            found.add("seasonal-maintenance")
        else:
            found.add("unclassified")
    if not found:
        found.add("unclassified")
    return [action for action in ACTION_ORDER if action in found]


def build_calendar_outputs(entries: list[dict[str, str]], registry: list[dict[str, str]]) -> None:
    names = {normalize_key(row["display_name"]): row for row in registry}
    action_rows: list[dict[str, str]] = []
    review_rows: list[dict[str, str]] = []
    for entry in entries:
        grouped = "/" in entry["plant_text"] or "," in entry["plant_text"]
        registry_row = names.get(normalize_key(entry["plant_text"]))
        actions = action_types_for_entry(entry)
        action_rows.append(
            {
                "source_id": CALENDAR_SOURCE_ID,
                "source_path": CALENDAR_SOURCE_PATH,
                "source_title": "Errington BC Zone 8a Planting Calendar",
                "source_author": "Not identified in PDF metadata",
                "publication_date": "Unknown; PDF metadata creation date 2026-06-28",
                "access_date": "2026-11-22",
                "page_number": entry["page_number"],
                "month": entry["month"],
                "page_type": entry["page_type"],
                "section": entry["section"],
                "plant_text": entry["plant_text"],
                "plant_id": plant_id(registry_row["display_name"]) if registry_row else "",
                "source_transcription": entry["row_text"],
                "evidence_type": "source transcription",
                "action_types": "; ".join(actions) if actions else "unclassified",
                "classification_method": "mechanical keyword classification; not editorially reviewed",
                "editorial_interpretation": "Mechanical action label only; not a recommendation.",
                "confidence": "unassessed",
                "verification_status": "pending-verification",
                "interpretation_status": "source-transcription; not a recommendation",
                "grouped_plant_text": "true" if grouped else "false",
            }
        )

        reasons = ["source transcription and timing not independently reviewed"]
        if grouped:
            reasons.append("grouped plant names; individual timing not established")
        if not registry_row:
            reasons.append("no exact single-plant registry match")
        if not actions:
            reasons.append("action type unresolved")
        if not entry.get("section"):
            reasons.append("section missing")
        if reasons:
            review_rows.append(
                {
                    "source_id": CALENDAR_SOURCE_ID,
                    "source_path": CALENDAR_SOURCE_PATH,
                    "page_number": entry["page_number"],
                    "month": entry["month"],
                    "page_type": entry["page_type"],
                    "section": entry["section"],
                    "plant_text": entry["plant_text"],
                    "source_transcription": entry["row_text"],
                    "review_reasons": "; ".join(reasons),
                }
            )

    write_csv("calendar_actions.csv", CALENDAR_ACTION_COLUMNS, action_rows)
    write_csv("calendar_review.csv", CALENDAR_REVIEW_COLUMNS, review_rows)


def build_plant_register(
    registry: list[dict[str, str]],
    calendar: list[dict[str, str]],
    approved_plant_ids: set[str],
) -> None:
    calendar_names = {normalize_key(row["plant_text"]) for row in calendar}
    rows = []
    for row in registry:
        source_is_local = row.get("source_scope") == "local-image"
        resolved_taxonomy = row.get("verification_status", "").startswith(
            "taxonomy-requires-species-or-cultivar-resolution"
        )
        has_calendar_record = normalize_key(row["display_name"]) in calendar_names
        rows.append(
            {
                "plant_id": plant_id(row["display_name"]),
                "common_name": row["display_name"],
                "botanical_name_as_recorded": row.get("latin_name", ""),
                "family_as_recorded": row.get("family", ""),
                "source_id": "ERRINGTON-CHART-IMAGES" if source_is_local else "PROJECT-HANDOFF",
                "source_path": (
                    "Planting Calander-Crops.png; Planting Calander-Ornamentals.png"
                    if source_is_local
                    else "ERRINGTON_ENCYCLOPEDIA_HANDOFF.md"
                ),
                "source_title": (
                    "Errington 8b crop and ornamental chart images"
                    if source_is_local
                    else "Errington encyclopedia project handoff"
                ),
                "source_author": "Not identified",
                "publication_date": "Unknown",
                "access_date": "2026-11-22",
                "page_or_section": (
                    "not available in chart image"
                    if source_is_local
                    else row.get("category", "")
                ),
                "evidence_type": "chart-list transcription" if source_is_local else "project-scope record",
                "relevant_transcription": row.get("source_name", row["display_name"]),
                "editorial_interpretation": "Registry item retained; no plant-level claim independently reviewed.",
                "confidence": "unassessed",
                "source_status": "source-transcribed" if source_is_local else "source-attributed-to-handoff",
                "taxonomy_status": "requires-resolution" if resolved_taxonomy else "pending-verification",
                "cultivar_status": "requires-resolution" if resolved_taxonomy else "pending-verification",
                "profile_status": "pending-verification",
                "timing_status": "source-record-exists-not-reviewed" if has_calendar_record else "pending-verification",
                "illustration_status": (
                    "illustration-approved"
                    if plant_id(row["display_name"]) in approved_plant_ids
                    else "pending-review"
                ),
            }
        )
    write_csv("plant_verification_register.csv", PLANT_REGISTER_COLUMNS, rows)


def build_illustration_manifest(registry: list[dict[str, str]]) -> None:
    filename = "plant_illustrations/illustration_manifest.csv"
    manifest_path = BASE_DIR / filename
    existing: dict[str, dict[str, str]] = {}
    if manifest_path.exists():
        with manifest_path.open(encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames != list(ILLUSTRATION_COLUMNS):
                raise ValueError(f"Unexpected illustration manifest columns: {manifest_path}")
            for row in reader:
                identifier = row["plant_id"]
                if not identifier or identifier in existing or None in row:
                    raise ValueError(f"Invalid or duplicate illustration plant ID: {identifier!r}")
                existing[identifier] = row
    registry_ids = {plant_id(row["display_name"]) for row in registry}
    if len(registry_ids) != len(registry):
        raise ValueError("Duplicate plant IDs in illustration registry")
    orphaned = existing.keys() - registry_ids
    if orphaned:
        raise ValueError(
            "Illustration manifest has plant IDs absent from registry; resolve without "
            f"discarding review data: {', '.join(sorted(orphaned))}"
        )
    rows = []
    for row in registry:
        identifier = plant_id(row["display_name"])
        if identifier in existing:
            rows.append(existing[identifier])
            continue
        rows.append(
            {
                "plant_id": identifier,
                "filename": f"{normalize_key(row['display_name'])}.png",
                "common_name": row["display_name"],
                "botanical_name_as_recorded": row.get("latin_name", ""),
                "image_source": "Not documented",
                "creator": "Unknown",
                "license": "Unknown",
                "generation_status": "unknown",
                "review_status": "pending",
                "approval_status": "not-approved",
                "reviewer_notes": "Filename is a request only; no image-to-plant association is approved.",
            }
        )
    write_csv(filename, ILLUSTRATION_COLUMNS, rows)


def build_status_reports(
    registry: list[dict[str, str]],
    entries: list[dict[str, str]],
    review_rows: list[dict[str, str]],
    approved_count: int,
) -> None:
    taxonomy_resolution_count = sum(
        row.get("verification_status", "").startswith(
            "taxonomy-requires-species-or-cultivar-resolution"
        )
        for row in registry
    )
    month_counts = Counter(row["month"] for row in entries)
    grouped = sum("/" in row["plant_text"] or "," in row["plant_text"] for row in entries)
    unreviewed_source_claims = len(registry)

    verification_lines = [
        "# Plant verification report",
        "",
        "## Status: `IN_PROGRESS` — not approved for publication",
        "",
        "| Measure | Count |",
        "|---|---:|",
        f"| Registry records retained | {len(registry)} |",
        "| Taxonomy independently verified in this repository | 0 |",
        f"| Records already flagged for species or cultivar resolution | {taxonomy_resolution_count} |",
        "| Individually reviewed horticultural profiles | 0 |",
        "| Locally reviewed planting timings | 0 |",
        f"| Records without claim-level source citations | {unreviewed_source_claims} |",
        f"| Approved illustrations | {approved_count} |",
        "",
        "Taxonomy values already present in `plant_registry.csv` are retained as recorded data, "
        "but `bulk-taxonomy-populated` is not verification. The register keeps taxonomy, cultivar, "
        "profile, timing, and illustration states independent. Existing botanical names and families "
        "require authoritative, claim-specific citations before they can be labeled verified.",
        "",
        "See `plant_verification_register.csv` for every stable plant ID, source attribution, and "
        "independent status dimension. A calendar source match means only that a transcription exists; "
        "it does not verify a planting recommendation.",
        "",
    ]
    (BASE_DIR / "PLANT_VERIFICATION_REPORT.md").write_text(
        "\n".join(verification_lines), encoding="utf-8"
    )

    month_lines = [
        "# Calendar review report",
        "",
        "## Status: `IN_PROGRESS` — transcription retained; recommendations unverified",
        "",
        f"The source transcription contains {len(entries)} entries across "
        f"{len(month_counts)} months. {grouped} entries combine multiple plant names, and "
        f"{len(review_rows)} entries are flagged for manual review. Every flagged row and its "
        "source page are listed in `calendar_review.csv`.",
        "",
        "The calendar PDF reports Zone 8a; both chart images report Zone 8b. April 15 and "
        "October 15 are presented by the source as expected frost anchors, not guaranteed frost "
        "dates. This project has not independently established a climate-zone or date correction.",
        "",
        "| Month | Transcribed entries |",
        "|---|---:|",
    ]
    month_lines.extend(f"| {month.title()} | {month_counts.get(month, 0)} |" for month in MONTHS)
    month_lines.extend(
        [
            "",
            "Structured records in `calendar_actions.csv` preserve the source text, page number, "
            "and mechanical action classification. Classifications are not editorially reviewed "
            "and must not be treated as local advice.",
            "",
        ]
    )
    (BASE_DIR / "CALENDAR_REVIEW_REPORT.md").write_text(
        "\n".join(month_lines), encoding="utf-8"
    )

    illustration_lines = [
        "# Illustration audit",
        "",
        "## Status: `IN_PROGRESS` — illustration review remains incomplete",
        "",
        f"The plant registry contains {len(registry)} records. {approved_count} illustration "
        "associations have an approved manifest entry and valid human-review sidecar. "
        "The original audit found 70 images on the separate `illustration-assets` branch, "
        "without documented identity, creator, license, or review history.",
        "",
        "The stable-ID manifest at `plant_illustrations/illustration_manifest.csv` does not "
        "associate any image based on a filename alone. The PDF builder requires both a "
        "stable plant ID and a valid hash-bound review sidecar.",
        "",
        "The candidate-generation workflow can use optional OpenAI or Gemini backends. "
        "A generated candidate is not botanical evidence or an approved illustration.",
        "",
        "Before approval, retrieve the external assets under controlled review, check identity, "
        "anatomy, resolution, duplicates, attribution, and license, then record reviewer notes "
        "against the stable plant ID. Preserve originals when rejecting an image.",
        "",
    ]
    (BASE_DIR / "ILLUSTRATION_AUDIT.md").write_text(
        "\n".join(illustration_lines), encoding="utf-8"
    )


def main() -> None:
    registry = read_csv("plant_registry.csv")
    entries = read_csv("errington_calendar_entries.csv")
    build_calendar_outputs(entries, registry)
    build_illustration_manifest(registry)
    from build_final_encyclopedia_pdf import load_plant_illustrations

    approved_plant_ids = set(load_plant_illustrations(BASE_DIR))
    build_plant_register(registry, entries, approved_plant_ids)
    review_rows = read_csv("calendar_review.csv")
    build_status_reports(registry, entries, review_rows, len(approved_plant_ids))
    print(
        f"Built provenance registers for {len(registry)} plants and "
        f"{len(entries)} calendar transcriptions."
    )


if __name__ == "__main__":
    main()
