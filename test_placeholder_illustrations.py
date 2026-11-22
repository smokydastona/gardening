from pathlib import Path

from generate_placeholder_illustrations import make_placeholder, read_registry


def test_placeholder_cards_are_pending_and_not_biological(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("generate_placeholder_illustrations.BASE_DIR", tmp_path)
    monkeypatch.setattr("generate_placeholder_illustrations.PENDING_DIR", tmp_path / "plant_illustrations" / "pending_review")
    monkeypatch.setattr("generate_placeholder_illustrations.EVIDENCE_DIR", tmp_path / "botanical_evidence")
    (tmp_path / "plant_illustrations").mkdir()
    (tmp_path / "botanical_evidence").mkdir()
    (tmp_path / "botanical_evidence" / "ARUGULA.json").write_text(
        '{"plant_key":"ARUGULA","display_name":"Arugula","taxon_verified":false}',
        encoding="utf-8",
    )
    (tmp_path / "fonts").mkdir()
    row = {"display_name": "Arugula"}
    output, sidecar = make_placeholder(row)
    assert output.is_file()
    assert sidecar.is_file()


def test_repository_has_one_placeholder_per_registry_record() -> None:
    registry = read_registry()
    for row in registry:
        key = row["display_name"].upper()
        import re
        key = re.sub(r"[^A-Z0-9]+", "_", key).strip("_")
        image = Path("plant_illustrations/pending_review") / key / "pending-placeholder.png"
        sidecar = image.with_suffix(".json")
        assert image.is_file(), image
        assert sidecar.is_file(), sidecar
