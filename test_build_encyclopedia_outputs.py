import csv

from build_encyclopedia_outputs import build_illustration_asset_manifest, build_illustration_brief, preferred_illustration_filename


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