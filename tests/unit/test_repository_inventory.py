from __future__ import annotations

from scripts.migration.build_repository_inventory import _modified_dates, _tree


def test_inventory_reads_tracked_head_tree() -> None:
    head = _tree("HEAD")

    assert "plant_registry.csv" in head


def test_inventory_uses_git_history_dates_for_tracked_files() -> None:
    dates = _modified_dates("HEAD")

    assert dates["README.md"].startswith("20")
    assert "README.md" in dates
