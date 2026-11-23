from __future__ import annotations

import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

from pypdf import PdfReader

from data_model import validate_authoritative_registry
from validate_pipeline import (
    RELEASE_PDFS,
    validate_publication_set,
    validate_source_hashes,
)


BASE_DIR = Path(__file__).resolve().parent
PLAN_PATH = "ERRINGTON_MASTER_PLAN.md"
PLANT_ALIASES = {
    "daffodils": ("daffodil", "Plural form in historical scope list"),
    "daylilies": ("daylily", "Plural form in historical scope list"),
    "sweet peas": ("sweet pea", "Plural form in historical scope list"),
    "tulips": ("tulip", "Plural form in historical scope list"),
}
RECONCILIATION_COLUMNS = (
    "record_type",
    "historical_section",
    "historical_name",
    "registry_plant_id",
    "registry_name",
    "occurrence",
    "name_reconciliation",
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def plan_entries(plan_text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    section = ""
    in_inventory = False
    for line in plan_text.splitlines():
        if re.match(r"### Total Plants Requiring Full Entries:", line):
            break
        heading = re.fullmatch(r"### (.+?) \((\d+)\)", line)
        if heading:
            section = heading.group(1)
            in_inventory = True
            continue
        if not in_inventory:
            continue
        item = re.match(r"\s*\d+\.\s+(.+?)\.?\s*$", line)
        if item:
            entries.append((section, item.group(1).strip().rstrip(".")))
    return entries


def _normalized_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().casefold())


def build_reconciliation(
    plan_text: str, registry: list[dict[str, str]]
) -> tuple[list[dict[str, str]], dict[str, int]]:
    registry_by_name = {
        _normalized_name(row["display_name"]): row for row in registry
    }
    if len(registry_by_name) != len(registry):
        raise ValueError("Registry contains duplicate normalized display names")

    occurrences: Counter[str] = Counter()
    mapped_ids: set[str] = set()
    rows: list[dict[str, str]] = []
    historical_entries = plan_entries(plan_text)
    if not historical_entries:
        raise ValueError(f"No historical plant entries found in {PLAN_PATH}")
    declared_total = re.search(
        r"^### Total Plants Requiring Full Entries:\s*(\d+)\s*$",
        plan_text,
        re.MULTILINE,
    )
    if declared_total is None or int(declared_total.group(1)) != len(historical_entries):
        raise ValueError(
            "Historical master-plan total does not match the enumerated plant entries"
        )

    for section, historical_name in historical_entries:
        normalized = _normalized_name(historical_name)
        match_name, note = PLANT_ALIASES.get(
            normalized, (normalized, "Exact case-insensitive name match")
        )
        matched = registry_by_name.get(match_name)
        if matched is None:
            raise ValueError(
                f"Historical plant name has no registry match: {historical_name}"
            )
        plant_id = matched["plant_id"]
        occurrences[plant_id] += 1
        mapped_ids.add(plant_id)
        rows.append(
            {
                "record_type": (
                    "repeated-historical-entry"
                    if occurrences[plant_id] > 1
                    else "historical-entry"
                ),
                "historical_section": section,
                "historical_name": historical_name,
                "registry_plant_id": plant_id,
                "registry_name": matched["display_name"],
                "occurrence": str(occurrences[plant_id]),
                "name_reconciliation": note,
            }
        )

    registry_only = sorted(
        (row for row in registry if row["plant_id"] not in mapped_ids),
        key=lambda row: _normalized_name(row["display_name"]),
    )
    rows.extend(
        {
            "record_type": "registry-additional-scope",
            "historical_section": "",
            "historical_name": "",
            "registry_plant_id": row["plant_id"],
            "registry_name": row["display_name"],
            "occurrence": "",
            "name_reconciliation": (
                "Retained registry record not listed in historical 125-entry plan"
            ),
        }
        for row in registry_only
    )
    summary = {
        "historical_entries": len(historical_entries),
        "distinct_historical_records": len(mapped_ids),
        "repeated_entries": len(historical_entries) - len(mapped_ids),
        "alias_normalized_entries": sum(
            row["historical_name"].casefold() in PLANT_ALIASES
            for row in rows
            if row["record_type"] != "registry-additional-scope"
        ),
        "registry_records": len(registry),
        "additional_registry_records": len(registry_only),
    }
    return rows, summary


def _manifest_asset_counts(base_dir: Path, manifest_path: str) -> dict[str, int]:
    path = base_dir / manifest_path
    if not path.is_file():
        return {
            "records": 0,
            "valid_hashes": 0,
            "invalid_hashes": 0,
            "duplicate_hashes": 0,
        }
    rows = read_csv(path)
    valid_hashes = 0
    for row in rows:
        filename = row.get("filename", "").strip()
        expected = row.get("sha256", "").strip().lower()
        asset_path = path.parent / filename
        if (
            filename
            and re.fullmatch(r"[0-9a-f]{64}", expected)
            and asset_path.is_file()
            and hashlib.sha256(asset_path.read_bytes()).hexdigest() == expected
        ):
            valid_hashes += 1
    hashes = [
        row.get("sha256", "").strip().lower()
        for row in rows
        if re.fullmatch(r"[0-9a-f]{64}", row.get("sha256", "").strip().lower())
    ]
    duplicate_hashes = sum(count - 1 for count in Counter(hashes).values() if count > 1)
    return {
        "records": len(rows),
        "valid_hashes": valid_hashes,
        "invalid_hashes": len(rows) - valid_hashes,
        "duplicate_hashes": duplicate_hashes,
    }


def _verified_count(rows: list[dict[str, str]], field: str) -> int:
    return sum(row.get(field, "").strip().casefold() == "verified" for row in rows)


def _verification_audit_summary(base_dir: Path) -> tuple[str, dict[str, object] | None]:
    path = base_dir / "reports" / "VERIFICATION_AUDIT.json"
    if not path.is_file():
        return "missing", None
    report = json.loads(path.read_text(encoding="utf-8"))
    hashes = report.get("inputs_sha256")
    if not isinstance(hashes, dict):
        return "invalid", None
    root = base_dir.resolve()
    for filename, expected in hashes.items():
        source = (root / filename).resolve()
        if not source.is_relative_to(root) or not source.is_file():
            return "invalid", None
        if hashlib.sha256(source.read_bytes()).hexdigest() != expected:
            return "stale", report
    return "current", report


def generate_status(base_dir: Path = BASE_DIR) -> str:
    registry = read_csv(base_dir / "plant_registry.csv")
    calendar = read_csv(base_dir / "errington_calendar_entries.csv")
    verification = read_csv(base_dir / "plant_verification_register.csv")
    claims = read_csv(base_dir / "claims" / "CLAIM_SOURCES.csv")
    plan_text = (base_dir / PLAN_PATH).read_text(encoding="utf-8")
    reconciliation, scope = build_reconciliation(plan_text, registry)

    reconciliation_path = base_dir / "reports" / "PLANT_SCOPE_RECONCILIATION.csv"
    reconciliation_path.parent.mkdir(parents=True, exist_ok=True)
    with reconciliation_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=RECONCILIATION_COLUMNS,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(reconciliation)

    source_integrity = "PASS"
    try:
        validate_source_hashes(base_dir)
        registry_validation = validate_authoritative_registry(base_dir)
    except (OSError, ValueError) as error:
        source_integrity = f"FAIL — {error}"
        registry_validation = {}

    candidate_assets = _manifest_asset_counts(
        base_dir, "plant_illustrations/concept_candidates/candidate_manifest.csv"
    )
    figures = _manifest_asset_counts(
        base_dir, "educational_figures/figure_manifest.csv"
    )
    illustration_rows = read_csv(
        base_dir / "plant_illustrations" / "illustration_asset_manifest.csv"
    )
    approved_plant_assets = sum(
        row.get("approval_status", "").strip().casefold() == "approved"
        for row in illustration_rows
    )
    approved_figures = sum(
        row.get("approval_status", "").strip().casefold() == "approved"
        for row in read_csv(base_dir / "educational_figures" / "figure_manifest.csv")
    )

    pdf_lines = []
    missing_pdfs = []
    for filename in RELEASE_PDFS:
        path = base_dir / filename
        if not path.is_file():
            missing_pdfs.append(filename)
            pdf_lines.append(f"| `{filename}` | Missing |")
            continue
        try:
            page_count = len(PdfReader(str(path)).pages)
        except Exception as error:
            missing_pdfs.append(filename)
            pdf_lines.append(f"| `{filename}` | Invalid PDF: {error} |")
            continue
        pdf_lines.append(f"| `{filename}` | Present; {page_count} pages |")

    profile_states = Counter(
        row.get("profile_status", "").strip() for row in verification
    )
    taxonomy_states = Counter(
        row.get("taxonomy_status", "").strip() for row in verification
    )
    timing_states = Counter(
        row.get("timing_status", "").strip() for row in verification
    )
    claim_statuses = Counter(row.get("status", "").strip() for row in claims)
    grouped_calendar = sum(
        "/" in row.get("plant_text", "") or "," in row.get("plant_text", "")
        for row in calendar
    )
    figure_rows = read_csv(base_dir / "educational_figures" / "figure_manifest.csv")
    figures_without_sources = sum(
        not row.get("source_references", "").strip() for row in figure_rows
    )
    plant_asset_manifest = read_csv(
        base_dir / "plant_illustrations" / "illustration_asset_manifest.csv"
    )
    missing_plant_assets = sum(
        row.get("asset_status", "").strip().casefold() == "missing"
        for row in plant_asset_manifest
    )
    plants_without_claims = len(
        {
            row["plant_id"]
            for row in verification
            if row["plant_id"]
        }
        - {
            row["plant_id"]
            for row in claims
            if row.get("plant_id", "").strip()
        }
    )
    incomplete_claims = sum(
        row.get("status", "").strip().casefold() != "verified" for row in claims
    )
    unverified_profiles = sum(
        row.get("profile_status", "").strip().casefold() != "verified"
        for row in verification
    )
    unresolved_taxonomies = sum(
        row.get("taxonomy_status", "").strip().casefold() == "requires-resolution"
        for row in verification
    )

    publication_validation = "PASS"
    publication_validation_details = ""
    try:
        validated_pdfs = validate_publication_set(base_dir)
        publication_validation_details = (
            f"{len(validated_pdfs)} PDFs passed structural and metadata checks."
        )
    except (OSError, ValueError) as error:
        publication_validation = f"FAIL — {error}"
        publication_validation_details = "At least one required PDF failed validation."

    verification_audit_state, verification_audit = _verification_audit_summary(base_dir)
    if verification_audit_state == "current" and verification_audit is not None:
        audit_scope = verification_audit["scope"]
        audit_claims = verification_audit["claim_sources"]
        audit_readiness = verification_audit["readiness"]
        verification_lines = [
            f"- Deterministic verification snapshot: **CURRENT**; decision "
            f"**{audit_readiness['decision']}** for {audit_scope['plants']} plants and "
            f"{audit_scope['calendar_entries']} calendar entries.",
            f"- Claim evidence extracts or source locations recorded: "
            f"{audit_claims['records_with_supporting_location_or_extract']} of "
            f"{len(audit_claims['records'])}; current claim statuses: "
            f"`{audit_claims['status_counts']}`.",
            f"- Verification audit blockers: {audit_readiness['blocker_findings']}; structural "
            f"errors: {audit_readiness['errors']}. See `reports/VERIFICATION_AUDIT.json`.",
        ]
    else:
        verification_lines = [
            f"- Deterministic verification snapshot: **{verification_audit_state.upper()}**; "
            "run `gardening verify audit` after changing source, evidence, asset, or publication records."
        ]

    return "\n".join(
        [
            "# Current release status",
            "",
            "**Release decision: NOT READY FOR PUBLICATION.** This report reads current source, "
            "verification, asset, and PDF records. It does not treat populated fields or generated "
            "artwork as independent verification or approval.",
            "",
            "Regenerate with `python generate_release_status.py`.",
            "",
            "## Source and scope",
            "",
            f"- Source checksum and authoritative registry validation: **{source_integrity}**.",
            f"- Registry validator: `{registry_validation or 'not completed'}`.",
            f"- Historical plan: {scope['historical_entries']} category entries map to "
            f"{scope['distinct_historical_records']} distinct registry records; "
            f"{scope['repeated_entries']} repeated category entries are retained.",
            f"- {scope['alias_normalized_entries']} explicit plural-form name matches are used; "
            "these are common-name inventory matches, not taxonomic conclusions.",
            f"- {scope['registry_records']} registry records are retained; "
            f"{scope['additional_registry_records']} are additional to the distinct "
            "historical-plan names. See `reports/PLANT_SCOPE_RECONCILIATION.csv`.",
            f"- Calendar source entries retained: {len(calendar)}; grouped entries still marked "
            f"for review: {grouped_calendar}.",
            f"- Profiles not explicitly verified: {unverified_profiles}; taxonomy records "
            f"explicitly marked `requires-resolution`: {unresolved_taxonomies}.",
            f"- Plants without any claim-source row: {plants_without_claims}; claim rows not "
            f"marked verified: {incomplete_claims}.",
            "",
            "## Research and human verification",
            "",
            f"- Plant verification records: {len(verification)}; profile states: "
            f"`{dict(profile_states)}`; taxonomy states: `{dict(taxonomy_states)}`; "
            f"timing states: `{dict(timing_states)}`.",
            f"- Records explicitly marked verified in the plant register: "
            f"{_verified_count(verification, 'profile_status')} profiles, "
            f"{_verified_count(verification, 'taxonomy_status')} taxonomies, and "
            f"{_verified_count(verification, 'timing_status')} local timings.",
            f"- Claim-source rows: {len(claims)}; evidence states: `{dict(claim_statuses)}`. "
            "A source row is not a verified profile.",
            "- Climate zone and frost anchors remain disputed/unverified; external sources "
            "require direct review and local measurements/proxy limitations remain unresolved.",
            *verification_lines,
            "",
            "## Assets and publications",
            "",
            f"- Plant concept candidates: {candidate_assets['records']} manifest rows; "
            f"{candidate_assets['valid_hashes']} hashes match; "
            f"{candidate_assets['invalid_hashes']} missing or mismatched files/hashes; "
            f"{candidate_assets['duplicate_hashes']} repeated file hashes.",
            f"- Plant artwork manifest: {missing_plant_assets} expected asset files are marked "
            f"missing; {max(0, len(registry) - approved_plant_assets)} registry entries lack an "
            "approved illustration.",
            f"- Plant illustration assets explicitly marked approved in the asset manifest: "
            f"{approved_plant_assets}.",
            f"- Educational figures: {figures['records']} manifest rows; "
            f"{figures['valid_hashes']} hashes match; {figures['invalid_hashes']} missing or "
            f"mismatched files/hashes; {figures['duplicate_hashes']} repeated file hashes; "
            f"{approved_figures} marked approved.",
            f"- Educational figures without recorded source references: {figures_without_sources}.",
            "- Export-format completeness beyond the PNG files declared by current manifests is "
            "not assessable; required per-asset export formats are not recorded.",
            "",
            f"PDF publication-set structural validation: **{publication_validation}** "
            f"({publication_validation_details})",
            "",
            "| Publication PDF | Current file check |",
            "|---|---|",
            *pdf_lines,
            "",
            "## Outstanding release gates",
            "",
            "- Independently verify the taxonomy, horticultural claims, local timing, and "
            "climate evidence for all applicable plants.",
            "- Review calendar transcription and grouped recommendations against the source; "
            "keep source transcription separate from advice.",
            "- Verify every image's identity, morphology, creator, license, checksum, and "
            "hash-bound independent approval; keep unapproved assets out of publications.",
            "- Complete source-backed educational figures, accessibility review, and "
            "page-by-page print and visual QA.",
            "- Broken-reference checking is limited to PDF table-of-contents destinations; "
            "manuscript cross-references are not checked by this report.",
            "- Tests are not run by this report. Hosted CI is not queried; verify test and CI "
            "results for the current revision separately.",
            "- Obtain qualified human botanical, horticultural, rights, and publication review.",
            *(
                [f"- Missing or unreadable required PDFs: {', '.join(missing_pdfs)}."]
                if missing_pdfs
                else []
            ),
            "",
        ]
    )


def main() -> None:
    report = generate_status()
    output = BASE_DIR / "reports" / "CURRENT_RELEASE_STATUS.md"
    output.write_text(report, encoding="utf-8")
    print(f"Wrote {output.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
