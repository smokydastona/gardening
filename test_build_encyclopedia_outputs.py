import csv
import re

import produce_publication_assets
from build_encyclopedia_outputs import (
    build_illustration_asset_manifest,
    build_illustration_brief,
    build_monthly_reference,
    preferred_illustration_filename,
)


def test_illustration_brief_does_not_infer_plant_morphology() -> None:
    row = {
        "category": "vegetable",
        "subcategory": "",
        "display_name": "Beets",
        "source_scope": "local-image",
        "calendar_match_status": "matched",
        "calendar_months": "APRIL; MAY; JUNE",
    }

    brief, prompt = build_illustration_brief(row)

    assert "identity unverified" in brief
    assert "Do not infer roots" in brief
    assert "Do not invent or assume morphology" in prompt
    assert "approved art brief" in prompt


def test_preferred_illustration_filename_normalizes_display_name() -> None:
    assert preferred_illustration_filename("Sweet Pea") == "SWEET_PEA.png"
    assert preferred_illustration_filename("Clematis Group 3") == "CLEMATIS_GROUP_3.png"


def test_build_illustration_asset_manifest_marks_missing_assets(tmp_path) -> None:
    (tmp_path / "plant_registry_enriched.csv").write_text(
        "category,subcategory,display_name,calendar_match_status,calendar_months\n"
        "flower,annual,Sweet Pea,matched,MARCH; APRIL\n"
        "vine,,Wisteria,unmatched,\n",
        encoding="utf-8",
    )

    build_illustration_asset_manifest(tmp_path)

    manifest_rows = list(csv.DictReader((tmp_path / "plant_illustrations" / "illustration_asset_manifest.csv").open(encoding="utf-8", newline="")))
    missing_lines = (tmp_path / "plant_illustrations" / "missing_illustrations.txt").read_text(encoding="utf-8").splitlines()

    assert manifest_rows[0]["asset_status"] == "missing"
    assert manifest_rows[0]["approval_status"] == "not-approved"
    assert manifest_rows[0]["plant_id"] == "plant-sweet-pea"
    assert "SWEET_PEA.png" in missing_lines
    assert "WISTERIA.png" in missing_lines


def test_monthly_reference_classifies_actions_and_removes_inline_pictogram_artifacts(tmp_path) -> None:
    (tmp_path / "calendar_actions.csv").write_text(
        "month,page_type,section,source_transcription,page_number,action_types,grouped_plant_text\n"
        "JANUARY,ornamentals,PERENNIALS,Hellebores — cut 🌸 tatty foliage,8,pruning,false\n"
        "MARCH,edibles,VEGETABLES,Peas — Wk 3–4 (cold-tolerant) direct sow,18,"
        "direct-sowing; frost-risk,false\n",
        encoding="utf-8",
    )

    build_monthly_reference(tmp_path)
    output = (tmp_path / "ERRINGTON_MONTHLY_REFERENCE.md").read_text(encoding="utf-8")

    assert "[PRUNING]" in output
    assert "cut tatty foliage" in output
    assert "[DIRECT SOWING / FROST RISK]" in output
    assert "🌸" not in output
    assert "REVIEW ACTION" not in output


def test_worked_examples_keep_fields_semantically_correct_and_have_troubleshooting(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(produce_publication_assets, "BASE", tmp_path)
    columns = [
        "display_name", "plant_id", "category", "latin_name", "family", "life_cycle",
        "growth_habit", "root_or_storage_organ", "leaf_arrangement_shape",
        "flower_structure", "fruit_seed_structure", "indoor_sow_window",
        "direct_sow_window", "transplant_window", "bloom_window", "harvest_window",
        "frost_notes", "soil_notes", "water_notes", "spacing_notes", "light_notes",
        "maintenance_notes", "pests_diseases",
    ]
    (tmp_path / "plant_registry.csv").write_text(
        ",".join(columns) + "\n" + ",".join("Example" if c == "display_name" else "" for c in columns) + "\n",
        encoding="utf-8",
    )
    (tmp_path / "errington_calendar_entries.csv").write_text(
        "plant_normalized,month,row_text\n", encoding="utf-8"
    )

    supplement = produce_publication_assets.produce_supplement([], [])
    text = supplement.read_text(encoding="utf-8")
    examples = re.findall(
        r"## Example \d{2}: (.*?)(?=## Example \d{2}:|$)",
        text,
        flags=re.DOTALL,
    )

    assert len(examples) == 18
    for example in examples:
        assert "**Expected result:**" in example
        assert "**Common mistakes**" in example
        assert "**Troubleshooting**" in example
        assert "Not specified" not in example
    first = examples[0]
    assert "deep paths" not in first.lower()
    assert "A stable, accessible 32 sq ft bed" in first
    assert "procedure" in first.lower()
    assert "Use 12 in on-center spacing" not in text
    assert "repeat after 14 days" not in text


def test_supplement_cross_references_calendar_without_presenting_boilerplate_as_advice(
    tmp_path, monkeypatch
) -> None:
    monkeypatch.setattr(produce_publication_assets, "BASE", tmp_path)
    (tmp_path / "claims").mkdir()
    (tmp_path / "plant_registry.csv").write_text(
        "plant_id,category,display_name,source_name,normalized_name,latin_name,family,life_cycle\n"
        "plant-arugula,vegetable,Arugula,Arugula,Arugula,Eruca vesicaria subsp. sativa,"
        "Brassicaceae,Annual\n",
        encoding="utf-8",
    )
    (tmp_path / "errington_calendar_entries.csv").write_text(
        "month,page_number,plant_text,plant_normalized,row_text\n"
        "MARCH,18,Radish / Arugula / Mache,RADISH_ARUGULA_MACHE,"
        "Radish / Arugula / Mache — Wk 3-4 direct sow\n",
        encoding="utf-8",
    )
    (tmp_path / "claims" / "CLAIM_SOURCES.csv").write_text(
        "plant_id,claim_text,source_title,organization,url,geographic_applicability,status,notes\n"
        "plant-arugula,Two taxonomies conflict,Plants of the World Online,Kew,"
        "https://example.test,World,conflicting-evidence,Needs human review\n",
        encoding="utf-8",
    )

    supplement = produce_publication_assets.produce_supplement([], [])
    text = supplement.read_text(encoding="utf-8")

    assert "**Botanical name as recorded (unverified):**" in text
    assert "MARCH, source p. 18" in text
    assert "grouped source entry; individual timing is unresolved" in text
    assert "conflicting-evidence" in text
    assert "Growth habit should be resolved" not in text
    assert "Well-drained, fertile soil" not in text
    assert "Artwork withheld" not in text