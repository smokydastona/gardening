from __future__ import annotations

import csv
import hashlib
import json
import re
import tempfile
from collections import Counter
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from gardening.assets import audit_assets
from gardening.validation.data_model import validate_authoritative_registry
from gardening.validation.pipeline import (
    RELEASE_PDFS,
    validate_publication_set,
    validate_source_hashes,
)


class VerificationStatus(StrEnum):
    UNREVIEWED = "UNREVIEWED"
    PENDING = "PENDING"
    RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
    PARTIALLY_VERIFIED = "PARTIALLY_VERIFIED"
    VERIFIED = "VERIFIED"
    CONFLICTING_EVIDENCE = "CONFLICTING_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"
    REQUIRES_HUMAN_REVIEW = "REQUIRES_HUMAN_REVIEW"
    REJECTED = "REJECTED"
    APPROVED = "APPROVED"
    EXPIRED = "EXPIRED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class VerificationDimension(StrEnum):
    SOURCE_INTEGRITY = "source_integrity"
    SOURCE_AVAILABILITY = "source_availability"
    SOURCE_PROVENANCE = "source_provenance"
    TAXONOMY = "taxonomy"
    CULTIVAR_IDENTITY = "cultivar_identity"
    BOTANICAL_MORPHOLOGY = "botanical_morphology"
    HORTICULTURAL_RECOMMENDATIONS = "horticultural_recommendations"
    CLIMATE_APPLICABILITY = "climate_applicability"
    CALENDAR_ACCURACY = "calendar_accuracy"
    PEST_AND_DISEASE = "pest_and_disease"
    SAFETY_AND_TOXICITY = "safety_and_toxicity"
    ILLUSTRATION_IDENTITY = "illustration_identity"
    ILLUSTRATION_ACCURACY = "illustration_accuracy"
    IMAGE_PROVENANCE_AND_LICENSING = "image_provenance_and_licensing"
    EDUCATIONAL_FIGURE_ACCURACY = "educational_figure_accuracy"
    EDITORIAL_ACCURACY = "editorial_accuracy"
    PUBLICATION_INTEGRITY = "publication_integrity"
    ACCESSIBILITY = "accessibility"
    VISUAL_QUALITY = "visual_quality"
    BUILD_REPRODUCIBILITY = "build_reproducibility"


class VerificationInputError(ValueError):
    """Raised when an authoritative input cannot be interpreted safely."""


_STATUS_ALIASES = {
    "pending-verification": VerificationStatus.RESEARCH_REQUIRED,
    "pending-review": VerificationStatus.REQUIRES_HUMAN_REVIEW,
    "concept-pending-review": VerificationStatus.REQUIRES_HUMAN_REVIEW,
    "source-record-exists-not-reviewed": VerificationStatus.REQUIRES_HUMAN_REVIEW,
    "source-transcribed": VerificationStatus.REQUIRES_HUMAN_REVIEW,
    "source-attributed-to-handoff": VerificationStatus.REQUIRES_HUMAN_REVIEW,
    "requires-resolution": VerificationStatus.CONFLICTING_EVIDENCE,
    "conflicting-evidence": VerificationStatus.CONFLICTING_EVIDENCE,
    "partially-verified": VerificationStatus.PARTIALLY_VERIFIED,
    "verified-local": VerificationStatus.REQUIRES_HUMAN_REVIEW,
    "bulk-taxonomy-populated": VerificationStatus.UNREVIEWED,
    "not-started": VerificationStatus.UNREVIEWED,
    "unassessed": VerificationStatus.UNREVIEWED,
    "not-reviewed": VerificationStatus.UNREVIEWED,
    "not-verified": VerificationStatus.PENDING,
    "verified": VerificationStatus.VERIFIED,
    "approved": VerificationStatus.APPROVED,
    "rejected": VerificationStatus.REJECTED,
    "pending": VerificationStatus.PENDING,
    "research-required": VerificationStatus.RESEARCH_REQUIRED,
    "insufficient-evidence": VerificationStatus.INSUFFICIENT_EVIDENCE,
    "requires-human-review": VerificationStatus.REQUIRES_HUMAN_REVIEW,
    "expired": VerificationStatus.EXPIRED,
    "not-applicable": VerificationStatus.NOT_APPLICABLE,
}

_PLANT_DIMENSION_FIELDS = {
    VerificationDimension.TAXONOMY: "taxonomy_status",
    VerificationDimension.CULTIVAR_IDENTITY: "cultivar_status",
    VerificationDimension.HORTICULTURAL_RECOMMENDATIONS: "profile_status",
    VerificationDimension.CLIMATE_APPLICABILITY: "timing_status",
    VerificationDimension.ILLUSTRATION_IDENTITY: "illustration_status",
}


def normalize_status(value: str) -> VerificationStatus:
    normalized = re.sub(r"[\s_]+", "-", value.strip().casefold())
    if normalized in _STATUS_ALIASES:
        return _STATUS_ALIASES[normalized]
    try:
        return VerificationStatus(normalized.upper().replace("-", "_"))
    except ValueError as error:
        raise ValueError(f"Unknown verification status: {value!r}") from error


def _read_csv(path: Path, required: set[str]) -> list[dict[str, str]]:
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            missing = required - set(reader.fieldnames or ())
            if missing:
                raise VerificationInputError(
                    f"{path.name}: missing columns {', '.join(sorted(missing))}"
                )
            return list(reader)
    except (OSError, UnicodeError, csv.Error) as error:
        raise VerificationInputError(f"Cannot read {path}: {error}") from error


def _source_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _status_counts(statuses: list[VerificationStatus]) -> dict[str, int]:
    counts = Counter(status.value for status in statuses)
    return {status.value: counts[status.value] for status in VerificationStatus if counts[status.value]}


def _status_for_plant(
    plant: dict[str, str],
    dimension: VerificationDimension,
    taxonomy_conflict: bool,
) -> VerificationStatus:
    if dimension is VerificationDimension.TAXONOMY and taxonomy_conflict:
        return VerificationStatus.CONFLICTING_EVIDENCE
    field = _PLANT_DIMENSION_FIELDS.get(dimension)
    if field is None:
        return VerificationStatus.RESEARCH_REQUIRED
    return normalize_status(plant.get(field, ""))


def _finding(
    code: str,
    severity: str,
    message: str,
    *,
    entity_id: str = "",
    dimension: VerificationDimension | None = None,
) -> dict[str, str]:
    return {
        "code": code,
        "severity": severity,
        "entity_id": entity_id,
        "dimension": dimension.value if dimension else "",
        "message": message,
    }


def build_verification_report(repository: Path) -> dict[str, Any]:
    repository = repository.resolve()
    registry = _read_csv(
        repository / "plant_registry.csv",
        {"plant_id", "display_name"},
    )
    plant_verification = _read_csv(
        repository / "plant_verification_register.csv",
        {
            "plant_id",
            "source_status",
            "taxonomy_status",
            "cultivar_status",
            "profile_status",
            "timing_status",
            "illustration_status",
        },
    )
    claims = _read_csv(
        repository / "claims" / "CLAIM_SOURCES.csv",
        {
            "claim_id",
            "plant_id",
            "claim_text",
            "source_title",
            "organization",
            "url",
            "page_or_section",
            "source_id",
            "source_version",
            "source_sha256",
            "supporting_passage",
            "evidence_quality",
            "independent_source_group",
            "contradicts_claim_ids",
            "reviewer",
            "review_date",
            "status",
            "evidence_type",
        },
    )
    calendar = _read_csv(
        repository / "errington_calendar_entries.csv",
        {"month", "plant_text", "row_text", "page_number"},
    )
    calendar_actions = _read_csv(
        repository / "calendar_actions.csv",
        {"month", "plant_text", "verification_status", "grouped_plant_text"},
    )

    findings: list[dict[str, str]] = []
    registry_ids = [row["plant_id"].strip() for row in registry]
    if any(not plant_id for plant_id in registry_ids):
        findings.append(_finding("BLANK_PLANT_ID", "ERROR", "Plant registry contains a blank plant_id."))
    duplicate_ids = sorted(
        plant_id for plant_id, count in Counter(registry_ids).items() if plant_id and count > 1
    )
    for plant_id in duplicate_ids:
        findings.append(
            _finding("DUPLICATE_PLANT_ID", "ERROR", f"Duplicate plant ID: {plant_id}", entity_id=plant_id)
        )

    verification_by_id: dict[str, dict[str, str]] = {}
    for row in plant_verification:
        plant_id = row["plant_id"].strip()
        if plant_id in verification_by_id:
            findings.append(
                _finding("DUPLICATE_VERIFICATION_RECORD", "ERROR", "Duplicate plant verification record.", entity_id=plant_id)
            )
        verification_by_id[plant_id] = row
    registry_id_set = set(registry_ids)
    verification_id_set = set(verification_by_id)
    for plant_id in sorted(registry_id_set - verification_id_set):
        findings.append(
            _finding("MISSING_PLANT_VERIFICATION", "ERROR", "Plant has no verification register row.", entity_id=plant_id)
        )
    for plant_id in sorted(verification_id_set - registry_id_set):
        findings.append(
            _finding("ORPHANED_PLANT_VERIFICATION", "ERROR", "Verification row references an unknown plant.", entity_id=plant_id)
        )

    claim_ids = [row["claim_id"].strip() for row in claims]
    duplicate_claim_ids = sorted(
        claim_id for claim_id, count in Counter(claim_ids).items() if claim_id and count > 1
    )
    claim_id_set = set(claim_ids)
    for claim_id in duplicate_claim_ids:
        findings.append(
            _finding("DUPLICATE_CLAIM_ID", "ERROR", f"Duplicate claim ID: {claim_id}", entity_id=claim_id)
        )
    known_claim_plants = {row["plant_id"].strip() for row in registry}
    for claim in claims:
        claim_id = claim["claim_id"].strip()
        plant_id = claim["plant_id"].strip()
        if plant_id not in known_claim_plants:
            findings.append(
                _finding("ORPHANED_CLAIM", "ERROR", "Claim references an unknown plant.", entity_id=claim_id)
            )
        status = normalize_status(claim["status"])
        if (
            not claim["claim_text"].strip()
            or not claim["source_title"].strip()
            or not claim["organization"].strip()
            or not claim["url"].strip()
            or not claim["source_id"].strip()
        ):
            findings.append(
                _finding(
                    "INCOMPLETE_CLAIM_SOURCE",
                    "BLOCKER",
                    "Claim lacks its text or required source metadata.",
                    entity_id=claim_id,
                )
            )
        parsed_url = urlsplit(claim["url"].strip())
        if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
            findings.append(
                _finding(
                    "INVALID_CLAIM_SOURCE_URL",
                    "ERROR",
                    "Claim source URL must be an absolute HTTP or HTTPS URL.",
                    entity_id=claim_id,
                    dimension=VerificationDimension.SOURCE_PROVENANCE,
                )
            )
        evidence_excerpt = claim.get("evidence_excerpt", "").strip() or claim.get(
            "supporting_passage", ""
        ).strip()
        if not (claim["page_or_section"].strip() or evidence_excerpt):
            findings.append(
                _finding(
                    "MISSING_CLAIM_SUPPORT",
                    "ERROR" if status is VerificationStatus.VERIFIED else "BLOCKER",
                    "Claim has no source location or evidence extract.",
                    entity_id=claim_id,
                )
            )
        if status is VerificationStatus.CONFLICTING_EVIDENCE:
            findings.append(
                _finding(
                    "CONFLICTING_CLAIM_EVIDENCE",
                    "BLOCKER",
                    "Conflicting evidence is retained and requires botanical review.",
                    entity_id=claim_id,
                    dimension=VerificationDimension.TAXONOMY
                    if "taxon" in claim["evidence_type"].casefold()
                    else None,
                )
            )
        if not claim["source_version"].strip() or not claim["source_sha256"].strip():
            findings.append(
                _finding(
                    "SOURCE_SNAPSHOT_MISSING",
                    "BLOCKER",
                    "Source version and content hash have not been captured.",
                    entity_id=claim_id,
                    dimension=VerificationDimension.SOURCE_PROVENANCE,
                )
            )
        elif not re.fullmatch(r"[a-fA-F0-9]{64}", claim["source_sha256"].strip()):
            findings.append(
                _finding(
                    "INVALID_SOURCE_SNAPSHOT_HASH",
                    "ERROR",
                    "Source snapshot hash must be a SHA-256 digest.",
                    entity_id=claim_id,
                    dimension=VerificationDimension.SOURCE_PROVENANCE,
                )
            )
        if not claim["independent_source_group"].strip():
            findings.append(
                _finding(
                    "SOURCE_INDEPENDENCE_UNASSESSED",
                    "BLOCKER",
                    "Independence from other sources has not been assessed.",
                    entity_id=claim_id,
                    dimension=VerificationDimension.SOURCE_PROVENANCE,
                )
            )
        for contradicted_id in filter(
            None,
            (item.strip() for item in claim["contradicts_claim_ids"].split(";")),
        ):
            if contradicted_id not in claim_id_set or contradicted_id == claim_id:
                findings.append(
                    _finding(
                        "INVALID_CONTRADICTION_REFERENCE",
                        "ERROR",
                        f"Invalid contradictory claim reference: {contradicted_id}",
                        entity_id=claim_id,
                    )
                )
        if status is VerificationStatus.VERIFIED and (
            not claim["reviewer"].strip() or not claim["review_date"].strip()
        ):
            findings.append(
                _finding(
                    "VERIFIED_CLAIM_WITHOUT_REVIEWER",
                    "ERROR",
                    "Verified claims require a named reviewer and review date.",
                    entity_id=claim_id,
                )
            )

    taxonomy_conflicts = {
        claim["plant_id"].strip()
        for claim in claims
        if normalize_status(claim["status"]) is VerificationStatus.CONFLICTING_EVIDENCE
        and "taxon" in claim["evidence_type"].casefold()
    }

    plant_dimensions = [
        dimension
        for dimension in VerificationDimension
        if dimension
        in {
            VerificationDimension.SOURCE_PROVENANCE,
            VerificationDimension.TAXONOMY,
            VerificationDimension.CULTIVAR_IDENTITY,
            VerificationDimension.BOTANICAL_MORPHOLOGY,
            VerificationDimension.HORTICULTURAL_RECOMMENDATIONS,
            VerificationDimension.CLIMATE_APPLICABILITY,
            VerificationDimension.CALENDAR_ACCURACY,
            VerificationDimension.PEST_AND_DISEASE,
            VerificationDimension.SAFETY_AND_TOXICITY,
            VerificationDimension.ILLUSTRATION_IDENTITY,
            VerificationDimension.ILLUSTRATION_ACCURACY,
            VerificationDimension.IMAGE_PROVENANCE_AND_LICENSING,
        }
    ]
    plants = []
    for row in registry:
        plant_id = row["plant_id"].strip()
        verification = verification_by_id.get(plant_id, {})
        dimensions: dict[str, str] = {}
        for dimension in plant_dimensions:
            if dimension is VerificationDimension.SOURCE_PROVENANCE:
                status = normalize_status(verification.get("source_status", ""))
            elif dimension is VerificationDimension.CALENDAR_ACCURACY:
                status = VerificationStatus.REQUIRES_HUMAN_REVIEW
            elif dimension is VerificationDimension.ILLUSTRATION_ACCURACY:
                status = VerificationStatus.REQUIRES_HUMAN_REVIEW
            elif dimension is VerificationDimension.IMAGE_PROVENANCE_AND_LICENSING:
                status = VerificationStatus.RESEARCH_REQUIRED
            else:
                status = _status_for_plant(
                    verification, dimension, plant_id in taxonomy_conflicts
                )
            dimensions[dimension.value] = status.value
        plants.append(
            {
                "plant_id": plant_id,
                "display_name": row["display_name"].strip(),
                "dimensions": dimensions,
            }
        )

    plant_dimension_counts = {
        dimension.value: _status_counts(
            [VerificationStatus(plant["dimensions"][dimension.value]) for plant in plants]
        )
        for dimension in plant_dimensions
    }

    grouped_entries = sum(
        "/" in row["plant_text"] or "," in row["plant_text"] for row in calendar
    )
    if len(calendar) != len(calendar_actions):
        findings.append(
            _finding(
                "CALENDAR_ACTION_COUNT_MISMATCH",
                "ERROR",
                f"Calendar source has {len(calendar)} entries but action registry has {len(calendar_actions)}.",
                dimension=VerificationDimension.CALENDAR_ACCURACY,
            )
        )
    calendar_statuses = [normalize_status(row["verification_status"]) for row in calendar_actions]

    plant_assets = audit_assets(repository, "plant")
    figure_assets = audit_assets(repository, "figure")
    for kind, asset_audit in (("plant", plant_assets), ("educational figure", figure_assets)):
        for message in asset_audit.errors:
            if kind == "educational figure" and "lack source references" in message:
                continue
            findings.append(
                _finding(
                    "ASSET_AUDIT_ERROR",
                    "BLOCKER" if "lack source references" in message else "ERROR",
                    f"{kind}: {message}",
                    dimension=(
                        VerificationDimension.ILLUSTRATION_IDENTITY
                        if kind == "plant"
                        else VerificationDimension.EDUCATIONAL_FIGURE_ACCURACY
                    ),
                )
            )
    figure_rows = _read_csv(
        repository / "educational_figures" / "figure_manifest.csv",
        {"figure_id", "source_references", "approval_status"},
    )
    figures_without_sources = sum(not row["source_references"].strip() for row in figure_rows)
    if figures_without_sources:
        findings.append(
            _finding(
                "FIGURE_SOURCE_REFERENCES_MISSING",
                "BLOCKER",
                f"{figures_without_sources} educational figures have no recorded source references.",
                dimension=VerificationDimension.EDUCATIONAL_FIGURE_ACCURACY,
            )
        )
    if plant_assets.approved_count < len(registry):
        findings.append(
            _finding(
                "PLANT_ILLUSTRATIONS_UNAPPROVED",
                "BLOCKER",
                f"{len(registry) - plant_assets.approved_count} registry plants lack approved artwork.",
                dimension=VerificationDimension.ILLUSTRATION_IDENTITY,
            )
        )
    if figure_assets.approved_count < len(figure_rows):
        findings.append(
            _finding(
                "EDUCATIONAL_FIGURES_UNAPPROVED",
                "BLOCKER",
                f"{len(figure_rows) - figure_assets.approved_count} educational figures lack approval.",
                dimension=VerificationDimension.EDUCATIONAL_FIGURE_ACCURACY,
            )
        )

    validation_errors = []
    try:
        validate_source_hashes(repository)
    except (OSError, ValueError) as error:
        validation_errors.append(f"Protected source integrity failed: {error}")
    try:
        registry_counts = validate_authoritative_registry(repository)
    except (OSError, ValueError) as error:
        registry_counts = {}
        validation_errors.append(f"Authoritative registry validation failed: {error}")
    try:
        publication_results = validate_publication_set(repository)
    except (OSError, ValueError) as error:
        publication_results = {}
        validation_errors.append(f"PDF structural validation failed: {error}")
    for message in validation_errors:
        findings.append(
            _finding(
                "INTEGRITY_VALIDATION_FAILED",
                "ERROR",
                message,
                dimension=VerificationDimension.SOURCE_INTEGRITY,
            )
        )

    source_files = (
        "SOURCE_SHA256SUMS.txt",
        "plant_registry.csv",
        "plant_verification_register.csv",
        "claims/CLAIM_SOURCES.csv",
        "errington_calendar_entries.csv",
        "calendar_actions.csv",
        "plant_illustrations/concept_candidates/candidate_manifest.csv",
        "educational_figures/figure_manifest.csv",
        *RELEASE_PDFS,
    )
    input_hashes = {
        filename: _source_hash(repository / filename)
        for filename in source_files
        if (repository / filename).is_file()
    }

    project_dimensions = {
        VerificationDimension.SOURCE_INTEGRITY.value: {
            "status": (
                VerificationStatus.VERIFIED.value
                if not any("Protected source integrity failed" in item for item in validation_errors)
                else VerificationStatus.REJECTED.value
            ),
            "scope": "Checksum validation only; does not establish source authenticity.",
        },
        VerificationDimension.SOURCE_AVAILABILITY.value: {
            "status": VerificationStatus.PENDING.value,
            "scope": "Network availability was not checked by this offline audit.",
        },
        VerificationDimension.SOURCE_PROVENANCE.value: {
            "status": VerificationStatus.RESEARCH_REQUIRED.value,
            "scope": "Recorded provenance has not been independently authenticated.",
        },
        VerificationDimension.CALENDAR_ACCURACY.value: {
            "status": (
                VerificationStatus.REQUIRES_HUMAN_REVIEW.value
                if calendar
                else VerificationStatus.INSUFFICIENT_EVIDENCE.value
            ),
            "scope": "Entries are source-linked transcriptions; source-page comparison is incomplete.",
        },
        VerificationDimension.EDUCATIONAL_FIGURE_ACCURACY.value: {
            "status": VerificationStatus.RESEARCH_REQUIRED.value,
            "scope": "Figure artwork is not scientifically reviewed or approved.",
        },
        VerificationDimension.EDITORIAL_ACCURACY.value: {
            "status": VerificationStatus.RESEARCH_REQUIRED.value,
            "scope": "Automated content review is not a substitute for editorial fact-checking.",
        },
        VerificationDimension.PUBLICATION_INTEGRITY.value: {
            "status": (
                VerificationStatus.VERIFIED.value
                if publication_results
                else VerificationStatus.REJECTED.value
            ),
            "scope": "Structural PDF checks only; scientific content and visual quality are excluded.",
        },
        VerificationDimension.ACCESSIBILITY.value: {
            "status": VerificationStatus.RESEARCH_REQUIRED.value,
            "scope": "Accessibility conformance has not been independently evaluated.",
        },
        VerificationDimension.VISUAL_QUALITY.value: {
            "status": VerificationStatus.REQUIRES_HUMAN_REVIEW.value,
            "scope": "A full human print-size review remains required.",
        },
        VerificationDimension.BUILD_REPRODUCIBILITY.value: {
            "status": VerificationStatus.PENDING.value,
            "scope": "This audit does not compare independent clean builds.",
        },
    }
    claim_status_counts = _status_counts(
        [normalize_status(claim["status"]) for claim in claims]
    )
    project_status_counts = {
        dimension: item["status"] for dimension, item in project_dimensions.items()
    }
    claim_evidence_complete = sum(
        bool(
            claim["claim_text"].strip()
            and claim["source_title"].strip()
            and claim["organization"].strip()
            and claim["url"].strip()
            and (
                claim["page_or_section"].strip()
                or claim.get("evidence_excerpt", "").strip()
                or claim.get("supporting_passage", "").strip()
            )
        )
        for claim in claims
    )
    blocking_dimensions = sorted(
        dimension
        for dimension, item in project_dimensions.items()
        if item["status"]
        not in {
            VerificationStatus.VERIFIED.value,
            VerificationStatus.APPROVED.value,
            VerificationStatus.NOT_APPLICABLE.value,
        }
    )
    blocker_count = sum(finding["severity"] == "BLOCKER" for finding in findings)
    error_count = sum(finding["severity"] == "ERROR" for finding in findings)

    return {
        "schema_version": "1.0",
        "inputs_sha256": input_hashes,
        "scope": {
            "plants": len(registry),
            "plant_verification_records": len(plant_verification),
            "calendar_entries": len(calendar),
            "grouped_calendar_entries": grouped_entries,
            "claim_source_records": len(claims),
            "educational_figures": len(figure_rows),
        },
        "structural_validation": {
            "source_hashes": "PASS"
            if not any("Protected source integrity failed" in item for item in validation_errors)
            else "FAIL",
            "registry": registry_counts,
            "publications": publication_results,
            "plant_asset_audit": {
                "records": plant_assets.record_count,
                "checked_files": plant_assets.checked_files,
                "approved": plant_assets.approved_count,
            },
            "figure_asset_audit": {
                "records": figure_assets.record_count,
                "checked_files": figure_assets.checked_files,
                "approved": figure_assets.approved_count,
                "without_source_references": figures_without_sources,
            },
        },
        "plants": plants,
        "plant_dimension_status_counts": plant_dimension_counts,
        "claim_sources": {
            "records": [
                {
                    "claim_id": claim["claim_id"].strip(),
                    "plant_id": claim["plant_id"].strip(),
                    "status": normalize_status(claim["status"]).value,
                    "evidence_type": claim["evidence_type"].strip(),
                    "source_title": claim["source_title"].strip(),
                    "author": claim.get("author", "").strip(),
                    "organization": claim["organization"].strip(),
                    "url": claim["url"].strip(),
                    "source_id": claim["source_id"].strip(),
                    "source_version": claim["source_version"].strip(),
                    "source_sha256": claim["source_sha256"].strip(),
                    "publication_date": claim.get("publication_date", "").strip(),
                    "access_date": claim.get("access_date", "").strip(),
                    "page_or_section": claim["page_or_section"].strip(),
                    "supporting_passage": claim["supporting_passage"].strip(),
                    "evidence_quality": claim["evidence_quality"].strip(),
                    "independent_source_group": claim["independent_source_group"].strip(),
                    "contradicts_claim_ids": claim["contradicts_claim_ids"].strip(),
                    "has_source_location": bool(claim["page_or_section"].strip()),
                    "has_evidence_extract": bool(
                        claim.get("evidence_excerpt", "").strip()
                        or claim.get("supporting_passage", "").strip()
                    ),
                    "reviewer": claim.get("reviewer", "").strip(),
                    "review_date": claim.get("review_date", "").strip(),
                    "notes": claim.get("notes", "").strip(),
                }
                for claim in sorted(claims, key=lambda row: row["claim_id"])
            ],
            "status_counts": claim_status_counts,
            "records_with_supporting_location_or_extract": claim_evidence_complete,
        },
        "calendar": {
            "status_counts": _status_counts(calendar_statuses),
            "all_entries_require_source_comparison": bool(calendar),
        },
        "project_dimensions": project_dimensions,
        "readiness": {
            "decision": "NOT_READY"
            if blocker_count or error_count
            or blocking_dimensions
            else "READY",
            "blocker_findings": blocker_count,
            "blocked_project_dimensions": blocking_dimensions,
            "errors": error_count,
            "note": "A successful audit or build does not establish scientific, licensing, or human approval.",
        },
        "findings": sorted(
            findings,
            key=lambda item: (
                item["severity"],
                item["code"],
                item["entity_id"],
                item["message"],
            ),
        ),
    }


def write_verification_report(report: dict[str, Any], output: Path) -> None:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            newline="\n",
            dir=output.parent,
            prefix=f".{output.name}.",
            suffix=".tmp",
            delete=False,
        ) as stream:
            temp_name = stream.name
            stream.write(payload)
        Path(temp_name).replace(output)
    except OSError:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)
        raise
