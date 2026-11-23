from pathlib import Path

from data_model import read_csv
from generate_release_status import (
    BASE_DIR,
    build_reconciliation,
    generate_status,
)


def test_historical_plan_reconciles_without_dropping_registry_records() -> None:
    registry = read_csv(BASE_DIR / "plant_registry.csv")
    plan = (BASE_DIR / "ERRINGTON_MASTER_PLAN.md").read_text(encoding="utf-8")

    rows, summary = build_reconciliation(plan, registry)

    assert summary == {
        "historical_entries": 125,
        "distinct_historical_records": 123,
        "repeated_entries": 2,
        "alias_normalized_entries": 4,
        "registry_records": 137,
        "additional_registry_records": 14,
    }
    assert sum(row["record_type"] == "registry-additional-scope" for row in rows) == 14
    assert {
        row["registry_name"]
        for row in rows
        if row["record_type"] == "repeated-historical-entry"
    } == {"Asparagus", "Garry Oak"}


def test_release_status_preserves_unverified_and_human_review_gates() -> None:
    report = generate_status()

    assert "NOT READY FOR PUBLICATION" in report
    assert "123 distinct registry records" in report
    assert "14 are additional" in report
    assert "not run by this report" in report
    assert "qualified human" in report


def test_reconciliation_csv_is_reproducible_and_has_scope_only_rows() -> None:
    generate_status()
    reconciliation_path = BASE_DIR / "reports" / "PLANT_SCOPE_RECONCILIATION.csv"

    rows = read_csv(reconciliation_path)

    assert len(rows) == 139
    assert sum(row["record_type"] == "registry-additional-scope" for row in rows) == 14
