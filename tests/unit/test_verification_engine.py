import json
from pathlib import Path

import pytest

from gardening.cli import main
from gardening.verification.engine import (
    VerificationStatus,
    build_verification_report,
    normalize_status,
    write_verification_report,
)


REPOSITORY = Path(__file__).resolve().parents[2]


def test_legacy_statuses_map_without_promoting_populated_data():
    assert normalize_status("pending-verification") is VerificationStatus.RESEARCH_REQUIRED
    assert normalize_status("requires-resolution") is VerificationStatus.CONFLICTING_EVIDENCE
    assert normalize_status("source-record-exists-not-reviewed") is (
        VerificationStatus.REQUIRES_HUMAN_REVIEW
    )
    assert normalize_status("bulk-taxonomy-populated") is VerificationStatus.UNREVIEWED
    with pytest.raises(ValueError, match="Unknown verification status"):
        normalize_status("looks-good")


def test_audit_reports_each_plant_and_keeps_project_unverified():
    report = build_verification_report(REPOSITORY)

    assert report["scope"]["plants"] == 137
    assert report["scope"]["calendar_entries"] == 359
    assert report["scope"]["claim_source_records"] == 2
    assert report["claim_sources"]["status_counts"] == {
        "CONFLICTING_EVIDENCE": 2
    }
    assert report["claim_sources"]["records_with_supporting_location_or_extract"] == 0
    claim_records = {
        record["claim_id"]: record for record in report["claim_sources"]["records"]
    }
    assert claim_records["arugula-identity-kew"]["contradicts_claim_ids"] == (
        "arugula-identity-wfo"
    )
    assert claim_records["arugula-identity-wfo"]["contradicts_claim_ids"] == (
        "arugula-identity-kew"
    )
    assert not claim_records["arugula-identity-kew"]["source_sha256"]
    assert report["readiness"]["decision"] == "NOT_READY"
    assert report["structural_validation"]["source_hashes"] == "PASS"
    assert report["structural_validation"]["publications"]
    assert report["structural_validation"]["plant_asset_audit"]["approved"] == 0
    assert report["structural_validation"]["figure_asset_audit"][
        "without_source_references"
    ] == 36

    arugula = next(plant for plant in report["plants"] if plant["plant_id"] == "plant-arugula")
    assert arugula["dimensions"]["taxonomy"] == "CONFLICTING_EVIDENCE"
    assert arugula["dimensions"]["horticultural_recommendations"] == "RESEARCH_REQUIRED"
    assert report["project_dimensions"]["publication_integrity"]["status"] == "VERIFIED"
    assert report["project_dimensions"]["visual_quality"]["status"] == "REQUIRES_HUMAN_REVIEW"


def test_json_report_is_deterministic_and_cli_strict_gate_stays_closed(tmp_path, caplog):
    report = build_verification_report(REPOSITORY)
    output = tmp_path / "verification.json"
    write_verification_report(report, output)
    first = output.read_text(encoding="utf-8")
    write_verification_report(build_verification_report(REPOSITORY), output)

    assert output.read_text(encoding="utf-8") == first
    assert json.loads(first)["readiness"]["decision"] == "NOT_READY"
    assert main(
        [
            "--repo",
            str(REPOSITORY),
            "verify",
            "audit",
            "--require-ready",
        ]
    ) == 1
    assert "Release requirements remain unmet." in caplog.text
