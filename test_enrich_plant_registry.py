from pathlib import Path

from enrich_plant_registry import clean_alias_part, entry_aliases, load_registry_rows, registry_aliases


def test_clean_alias_part_drops_descriptors() -> None:
    assert clean_alias_part("early Tulips") == "TULIPS"
    assert clean_alias_part("overwintering Garlic") == "GARLIC"


def test_entry_aliases_split_grouped_names() -> None:
    aliases = entry_aliases("Apple / Pear / Plum / Cherry")
    assert "APPLE" in aliases
    assert "PEAR" in aliases
    assert "PLUM" in aliases
    assert "CHERRY" in aliases


def test_registry_aliases_add_plural_variants() -> None:
    row = {"display_name": "Sweet Pea", "source_name": "Sweet Pea", "normalized_name": "Sweet Pea"}
    aliases = registry_aliases(row)
    assert "SWEET_PEA" in aliases
    assert "SWEET_PEAS" in aliases


def test_load_registry_rows_repairs_legacy_short_rows(tmp_path: Path) -> None:
    path = tmp_path / "plant_registry.csv"
    path.write_text(
        "category,subcategory,display_name,source_name,normalized_name,source_scope,source_status,verification_status,latin_name,family,life_cycle,growth_habit,root_or_storage_organ,leaf_arrangement_shape,flower_structure,fruit_seed_structure,indoor_sow_window,direct_sow_window,transplant_window,bloom_window,harvest_window,frost_notes,soil_notes,water_notes,spacing_notes,light_notes,maintenance_notes,pests_diseases,illustration_brief_status,illustration_prompt_status,notes\n"
        "vegetable,,Arugula,Arugula,Arugula,local-image,verified-local,pending-verification,,,,,,,,,,,,,,,,,,,not-started,not-started,\n",
        encoding="utf-8",
    )

    rows = load_registry_rows(path)

    assert rows[0]["maintenance_notes"] == ""
    assert rows[0]["pests_diseases"] == ""
    assert rows[0]["illustration_brief_status"] == "not-started"
    assert rows[0]["illustration_prompt_status"] == "not-started"