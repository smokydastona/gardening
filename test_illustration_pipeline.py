import csv
import base64
import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from PIL import Image

import generate_illustrations as generator
from build_encyclopedia_outputs import build_illustration_asset_manifest
from build_final_encyclopedia_pdf import SOURCE_FILES, build_pdf, load_plant_illustrations
from illustration_assets import ORGANS


def image(path: Path, color: str = "red") -> None:
    Image.new("RGB", (20, 30), color).save(path)


@pytest.fixture
def ready(tmp_path: Path):
    registry = tmp_path / "plant_registry_enriched.csv"
    registry.write_text("category,display_name,latin_name\nflower,Iris,Iris germanica\n", encoding="utf-8")
    row = generator.read_registry(registry)[0]
    evidence = generator.evidence_template(row)
    evidence.update(accepted_name="Iris germanica", taxon_verified=True, taxonomic_authority="Flora")
    evidence["human_verification"] = {"reviewer": "Botanist", "date": "2026-01-01", "notes": "Checked"}
    for field in generator.TRAITS:
        evidence["diagnostic_traits"][field] = "Verified trait"
    for i, ref in enumerate(evidence["reference_images"]):
        image(tmp_path / f"ref{i}.png", ("red", "green")[i])
        ref.update(path=f"ref{i}.png", creator="Photographer", license="CC0",
                   source_url=f"https://example.org/ref{i}")
    for i, source in enumerate(evidence["sources"]):
        source.update(title=f"Source {i}", url=f"https://example.org/source{i}", supports="Morphology")
    path = tmp_path / "botanical_evidence" / "IRIS.json"
    generator.write_json(path, evidence)
    return tmp_path, row, evidence


def test_evidence_rejects_duplicate_photographs_and_wrong_taxon(ready):
    repo, row, evidence = ready
    path = repo / "botanical_evidence" / "IRIS.json"
    evidence["reference_images"][1]["path"] = "ref0.png"
    generator.write_json(path, evidence)
    with pytest.raises(ValueError, match="distinct images"):
        generator.read_evidence(path, row, repo)
    evidence["plant_key"] = "ROSE"
    generator.write_json(path, evidence)
    with pytest.raises(ValueError, match="match the registry"):
        generator.read_evidence(path, row, repo)


def test_import_approve_and_publication_gate(ready, capsys):
    repo, _, _ = ready
    legacy = repo / "legacy.png"
    image(legacy)
    prefix = ["--repo", str(repo)]
    import_args = prefix + ["import", "--plant", "Iris", "--candidate", "legacy",
                            "--image", str(legacy), "--provenance", "Owned illustration"]
    assert run_cli(import_args) == 0
    assert not load_plant_illustrations(repo)
    checklist = repo / "review.json"
    checklist.write_text(json.dumps({**{k: "pass" for k in ORGANS}, "style": "pass"}))
    approval = prefix + ["approve", "--plant", "Iris", "--candidate", "legacy",
                         "--checklist", str(checklist), "--reviewer", "Reviewer",
                         "--notes", "Compared every visible part against sources."]
    assert run_cli(approval) == 0
    assets = load_plant_illustrations(repo)
    assert assets["IRIS"].name == "IRIS.png"
    build_illustration_asset_manifest(repo)
    with (repo / "plant_illustrations" / "illustration_asset_manifest.csv").open(newline="") as handle:
        assert next(csv.DictReader(handle))["asset_status"] == "present"
    image(assets["IRIS"], "blue")
    assert not load_plant_illustrations(repo)
    assert "changed after review" in capsys.readouterr().err


def run_cli(args: list[str]) -> int:
    from unittest.mock import patch
    with patch("sys.argv", ["generate_illustrations.py", *args]):
        return generator.main()


def test_approval_rejects_changed_evidence_and_unreviewed_style(ready):
    repo, _, evidence = ready
    source = repo / "legacy.png"
    image(source)
    prefix = ["--repo", str(repo)]
    assert run_cli(prefix + ["import", "--plant", "Iris", "--candidate", "test",
                             "--image", str(source), "--provenance", "Owned"]) == 0
    checklist = repo / "review.json"
    checklist.write_text(json.dumps({**{k: "pass" for k in ORGANS}, "style": "fail"}))
    args = prefix + ["approve", "--plant", "Iris", "--candidate", "test", "--checklist", str(checklist),
                     "--reviewer", "Reviewer", "--notes", "Compared with references"]
    assert run_cli(args) == 1
    checklist.write_text(json.dumps({**{k: "pass" for k in ORGANS}, "style": "pass"}))
    evidence["accepted_name"] = "Iris pallida"
    generator.write_json(repo / "botanical_evidence" / "IRIS.json", evidence)
    assert run_cli(args) == 1
    assert not load_plant_illustrations(repo)


def test_generation_records_pending_and_blocks_changed_reference(ready, monkeypatch):
    repo, _, _ = ready
    def fake_backend(args, prompt, output, refs):
        assert len(refs) == 2
        image(output)
        return "photographs"
    monkeypatch.setattr(generator, "run_backend", fake_backend)
    prefix = ["--repo", str(repo)]
    assert run_cli(prefix + ["generate", "--plant", "Iris", "--candidate", "one"]) == 0
    assert not load_plant_illustrations(repo)
    checklist = repo / "review.json"
    checklist.write_text(json.dumps({**{k: "pass" for k in ORGANS}, "style": "pass"}))
    image(repo / "ref0.png", "blue")
    assert run_cli(prefix + ["approve", "--plant", "Iris", "--candidate", "one",
                             "--checklist", str(checklist), "--reviewer", "Reviewer",
                             "--notes", "Checked"]) == 1


def test_openai_uses_photographs_and_portrait_size(ready, monkeypatch):
    repo, _, _ = ready
    buf = io.BytesIO()
    Image.new("RGB", (20, 30), "red").save(buf, format="PNG")

    def edit(**kwargs):
        assert kwargs["size"] == "1024x1536"
        assert len(kwargs["image"]) == 2
        assert all(handle.read(8) == b"\x89PNG\r\n\x1a\n" for handle in kwargs["image"])
        return SimpleNamespace(data=[SimpleNamespace(b64_json=base64.b64encode(buf.getvalue()).decode())])

    monkeypatch.setitem(sys.modules, "openai", SimpleNamespace(
        OpenAI=lambda: SimpleNamespace(images=SimpleNamespace(edit=edit))))
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    assert run_cli(["--repo", str(repo), "generate", "--plant", "Iris"]) == 0
    metadata = json.loads((repo / "plant_illustrations/pending_review/IRIS/openai-32.json").read_text())
    assert metadata["conditioning"] == "photographs"


@pytest.mark.parametrize("backend", ["o1", "i1", "kandinsky"])
def test_local_backends_construct_upstream_commands(ready, monkeypatch, backend):
    repo, _, _ = ready
    def fake_run(command, **kwargs):
        if backend == "o1":
            assert "--ref_images" in command
            assert command[command.index("--width") + 1] == "1024"
            out = command[command.index("--output_image") + 1]
        elif backend == "i1":
            assert "illustration_i1.py" in command[1]
            out = command[command.index("--output") + 1]
        else:
            assert "k5_lite_t2i_sft_hd.yaml" in command[command.index("--config") + 1]
            out = command[command.index("--output_filename") + 1]
        image(Path(out))
    monkeypatch.setattr(generator.subprocess, "run", fake_run)
    args = ["--repo", str(repo), "generate", "--plant", "Iris", "--backend", backend]
    if backend != "i1":
        args += ["--backend-dir", str(repo)]
    if backend == "o1":
        args += ["--model", str(repo / "checkpoint")]
    assert run_cli(args) == 0
    metadata = json.loads((repo / f"plant_illustrations/pending_review/IRIS/{backend}-32.json").read_text())
    assert metadata["conditioning"] == ("photographs" if backend == "o1" else "text-only")


def test_text_only_backend_rejects_visual_conditioning(ready):
    repo, _, _ = ready
    assert run_cli(["--repo", str(repo), "generate", "--plant", "Iris", "--backend", "i1",
                    "--style-reference", str(repo / "ref0.png")]) == 1


def test_plantgen_render_is_retained_and_sent_as_geometry(ready, monkeypatch):
    repo, _, evidence = ready
    evidence["plantgen_species"] = "iris-germanica"
    generator.write_json(repo / "botanical_evidence/IRIS.json", evidence)
    def fake_run(command, **kwargs):
        assert command[1:3] == ["render", "iris-germanica"]
        image(Path(command[command.index("--out") + 1]), "green")
    def fake_backend(args, prompt, output, refs):
        assert len(refs) == 3
        assert "tentative geometry aid" in prompt
        image(output)
        return "photographs"
    monkeypatch.setattr(generator.subprocess, "run", fake_run)
    monkeypatch.setattr(generator, "run_backend", fake_backend)
    assert run_cli(["--repo", str(repo), "generate", "--plant", "Iris",
                    "--plantgen", str(repo / "plantc")]) == 0
    pending = repo / "plant_illustrations/pending_review/IRIS"
    assert (pending / "openai-32.geometry.png").is_file()
    metadata = json.loads((pending / "openai-32.json").read_text())
    assert metadata["plantgen_sha256"]


def test_annotation_creates_a_new_reviewable_candidate(ready):
    repo, _, _ = ready
    image(repo / "old.png")
    prefix = ["--repo", str(repo)]
    assert run_cli(prefix + ["import", "--plant", "Iris", "--candidate", "old",
                             "--image", str(repo / "old.png"), "--provenance", "Owned"]) == 0
    layout = repo / "layout.json"
    layout.write_text(json.dumps({"labels": [{"text": "Leaf", "x": 0.1, "y": 0.5,
                                               "target_x": 0.5, "target_y": 0.6}]}))
    assert run_cli(prefix + ["annotate", "--plant", "Iris", "--candidate", "old",
                             "--output-candidate", "plate", "--layout", str(layout)]) == 0
    metadata = json.loads((repo / "plant_illustrations/pending_review/IRIS/plate.json").read_text())
    assert metadata["annotation"]["layout"]["labels"][0]["text"] == "Leaf"
    assert metadata["annotation"]["title"] == "Iris"
    assert metadata["annotation"]["font_sha256"] == generator.sha256_file(generator.DEFAULT_FONT)
    checklist = repo / "review.json"
    checklist.write_text(json.dumps({**{k: "pass" for k in ORGANS}, "style": "pass"}))
    assert run_cli(prefix + ["approve", "--plant", "Iris", "--candidate", "plate",
                             "--checklist", str(checklist), "--reviewer", "Reviewer",
                             "--notes", "Compared labels and image against sources"]) == 0
    assert "IRIS" in load_plant_illustrations(repo)


def test_approved_asset_is_rendered_in_pdf(ready):
    from pypdf import PdfReader

    repo, _, _ = ready
    image(repo / "cover.png")
    image(repo / "old.png")
    for title, filename, _ in SOURCE_FILES:
        (repo / filename).write_text("### Iris\nPlant text" if title == "Plant Catalog" else "Text")
    prefix = ["--repo", str(repo)]
    assert run_cli(prefix + ["import", "--plant", "Iris", "--candidate", "old",
                             "--image", str(repo / "old.png"), "--provenance", "Owned"]) == 0
    checklist = repo / "review.json"
    checklist.write_text(json.dumps({**{k: "pass" for k in ORGANS}, "style": "pass"}))
    assert run_cli(prefix + ["approve", "--plant", "Iris", "--candidate", "old",
                             "--checklist", str(checklist), "--reviewer", "Reviewer",
                             "--notes", "Compared with references"]) == 0
    pdf = build_pdf(repo)
    text = "\n".join(page.extract_text() for page in PdfReader(pdf).pages)
    assert "Scientific illustration asset: IRIS.png" in text
