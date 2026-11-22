#!/usr/bin/env python3
"""Generate evidence-gated botanical plates and record human approval."""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

from illustration_assets import ORGANS, REVIEW_FIELDS, keyify, sha256_file, sha256_json


STYLE = """Portrait botanical encyclopedia plate matching the Errington illustration
assets: warm ivory textured paper, fine hand-drawn archival ink and graphite,
delicate cross-hatching, richly but naturally colored transparent watercolor.
Arrange one clear whole specimen vertically with room for documented anatomical
details and a title above it; elegant vintage field-guide composition, readable
at book size. Leave clear margins for a frame and callouts.
Do not add text, lettering, titles, labels, borders or watermarks: these can be
added separately after verification. Not a photograph, 3-D render, clip-art,
cartoon, decorative pattern or imaginary habitat. Depict only the documented
taxon and its verified characteristics. Do not copy the subject of a style
reference. Never invent flowers, fruit, roots, organs or life stages; omit
undocumented details. No other species or decorative objects."""

TRAITS = ("growth_habit", "leaf_arrangement", "leaf_morphology", "diagnostic_features")
DEFAULT_MODEL = "gpt-image-2.6-sunburst"
DEFAULT_GEMINI_MODEL = "gemini-2.5-flash-image"
DEFAULT_FONT = Path(__file__).with_name("fonts") / "ReenieBeanie.ttf"


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def web_url(value: object, field: str) -> str:
    url = text(value, field)
    parsed = urlparse(url)
    if parsed.scheme not in ("https", "http") or not parsed.netloc:
        raise ValueError(f"{field} must be an HTTP(S) URL")
    return url


def read_registry(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    keys: set[str] = set()
    if not rows or "display_name" not in rows[0]:
        raise ValueError("Registry must contain plant records and display_name")
    for row in rows:
        key = keyify(text(row.get("display_name"), "registry display_name"))
        if not key or key in keys:
            raise ValueError(f"Duplicate or empty registry key: {key}")
        keys.add(key)
    return rows


def evidence_template(row: dict[str, str]) -> dict:
    return {
        "plant_key": keyify(row["display_name"]),
        "display_name": row["display_name"],
        "registry_latin_name_candidate": row.get("latin_name", ""),
        "accepted_name": "",
        "taxon_verified": False,
        "taxonomic_authority": "",
        "cultivar_or_group": "",
        "diagnostic_traits": {name: "" for name in (*TRAITS, "flower_structure", "fruit_or_seed_structure", "root_or_storage_structure", "known_variation_or_uncertainty")},
        "reference_images": [
            {"path": "", "source_url": "", "creator": "", "license": "", "view": view}
            for view in ("whole plant", "diagnostic close-up")
        ],
        "sources": [{"title": "", "url": "", "supports": ""} for _ in range(2)],
        "human_verification": {"reviewer": "", "date": "", "notes": ""},
        "plantgen_species": "",
    }


def read_evidence(path: Path, row: dict[str, str], repo: Path) -> tuple[dict, list[Path]]:
    evidence = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(evidence, dict):
        raise ValueError("Evidence must be a JSON object")
    key = keyify(row["display_name"])
    if evidence.get("plant_key") != key or evidence.get("display_name") != row["display_name"]:
        raise ValueError("Evidence plant_key and display_name must match the registry")
    if evidence.get("taxon_verified") is not True:
        raise ValueError("Evidence taxon_verified must be true after human verification")
    for field in ("accepted_name", "taxonomic_authority"):
        text(evidence.get(field), field)
    verification = evidence.get("human_verification")
    if not isinstance(verification, dict):
        raise ValueError("Missing human_verification")
    for field in ("reviewer", "date", "notes"):
        text(verification.get(field), f"human_verification.{field}")
    traits = evidence.get("diagnostic_traits")
    if not isinstance(traits, dict):
        raise ValueError("diagnostic_traits must be an object")
    for field in TRAITS:
        text(traits.get(field), f"diagnostic_traits.{field}")
    for field, value in traits.items():
        if not isinstance(value, str):
            raise ValueError(f"diagnostic_traits.{field} must be a string")
    sources = evidence.get("sources")
    if not isinstance(sources, list) or len(sources) < 2:
        raise ValueError("At least two traceable sources are required")
    source_urls = set()
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("Each source must be an object")
        text(source.get("title"), "source title")
        text(source.get("supports"), "source supports")
        source_urls.add(web_url(source.get("url"), "source url"))
    if len(source_urls) < 2:
        raise ValueError("Sources must have at least two distinct URLs")
    refs = evidence.get("reference_images")
    if not isinstance(refs, list) or len(refs) < 2:
        raise ValueError("At least two licensed reference photographs are required")
    paths = []
    for ref in refs:
        if not isinstance(ref, dict):
            raise ValueError("Each reference must be an object")
        for field in ("path", "creator", "license", "view"):
            text(ref.get(field), f"reference {field}")
        web_url(ref.get("source_url"), "reference source_url")
        path = (repo / ref["path"]).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Reference image not found: {path}")
        verify_image(path)
        paths.append(path)
    if len({sha256_file(p) for p in paths}) < 2:
        raise ValueError("Reference photographs must contain at least two distinct images")
    return evidence, paths


def verify_image(path: Path, portrait: bool = False) -> None:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required; install the repository requirements") from exc
    with Image.open(path) as image:
        if portrait and (image.format != "PNG" or image.width >= image.height):
            raise ValueError("Generated candidate must be a portrait PNG")
        image.verify()


def prompt_for(evidence: dict, has_style: bool, has_geometry: bool) -> str:
    traits = "\n".join(f"- {k.replace('_', ' ')}: {v}" for k, v in evidence["diagnostic_traits"].items() if v.strip())
    return (
        f"Create one botanical plate for {evidence['display_name']}, "
        f"accepted name {evidence['accepted_name']}, group {evidence.get('cultivar_or_group') or 'not specified'}.\n"
        f"Verified morphology:\n{traits}\n"
        "Use reference photographs as botanical evidence when supplied. "
        + ("The last reference is only a style exemplar, not botanical evidence. " if has_style else "")
        + ("A PlantGen render is a tentative geometry aid, not botanical evidence. " if has_geometry else "")
        + "\n" + STYLE
    )


def generate_openai(prompt: str, output: Path, model: str, refs: list[Path]) -> None:
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError("Install the optional OpenAI SDK: python -m pip install openai") from exc
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not set")
    with ExitStack() as stack:
        handles = [stack.enter_context(path.open("rb")) for path in refs]
        result = OpenAI().images.edit(model=model, image=handles, prompt=prompt,
                                      size="1024x1536", quality="high", output_format="png")
    if not result.data or not result.data[0].b64_json:
        raise RuntimeError("Image API returned no image data")
    output.write_bytes(base64.b64decode(result.data[0].b64_json, validate=True))


def generate_gemini(prompt: str, output: Path, model: str, refs: list[Path]) -> None:
    if not os.environ.get("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY is not set")
    try:
        from google import genai
        from google.genai import errors, types
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional Gemini SDK: python -m pip install google-genai==3.6.1"
        ) from exc
    from PIL import Image

    with ExitStack() as stack:
        images = [stack.enter_context(Image.open(path)) for path in refs]
        try:
            response = genai.Client(api_key=os.environ["GEMINI_API_KEY"]).models.generate_content(
                model=model,
                contents=[prompt, *images],
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio="2:3"),
                ),
            )
        except errors.APIError as exc:
            raise RuntimeError(f"Gemini image request failed (HTTP {exc.code}).") from exc
    for part in response.parts or []:
        data = part.inline_data
        if data and data.mime_type and data.mime_type.startswith("image/") and data.data:
            with Image.open(io.BytesIO(data.data)) as image:
                image.save(output, format="PNG")
            return
    raise RuntimeError("Gemini returned no image; the request may have been blocked or refused.")


def run_backend(args: argparse.Namespace, prompt: str, output: Path, refs: list[Path]) -> str:
    if args.backend == "openai":
        generate_openai(prompt, output, args.model or DEFAULT_MODEL, refs)
        return "photographs"
    if args.backend == "gemini":
        generate_gemini(prompt, output, args.model or DEFAULT_GEMINI_MODEL, refs)
        return "photographs"
    if args.backend == "o1":
        if not args.backend_dir or not args.model:
            raise ValueError("O1 requires --backend-dir and --model (local checkpoint directory)")
        if args.model_type not in ("full", "dev"):
            raise ValueError("O1 uses --model-type full or dev")
        root = Path(args.backend_dir).resolve()
        subprocess.run([args.backend_python, str(root / "inference.py"), "--model_path", str(Path(args.model).resolve()),
                        "--model_type", args.model_type, "--prompt", prompt,
                        "--ref_images", *map(str, refs), "--output_image", str(output),
                        "--width", "1024", "--height", "1536", "--seed", str(args.seed)],
                       cwd=root, check=True)
        return "photographs"
    if args.backend == "i1":
        if args.model_type != "full":
            raise ValueError("The I1 adapter supports --model-type full")
        helper = Path(__file__).with_name("illustration_i1.py")
        subprocess.run([args.backend_python, str(helper), "--prompt", prompt, "--output", str(output),
                        "--model-type", args.model_type, "--seed", str(args.seed)],
                       check=True)
        return "text-only"
    if not args.backend_dir:
        raise ValueError("Kandinsky requires --backend-dir")
    root = Path(args.backend_dir).resolve()
    subprocess.run([args.backend_python, str(root / "test.py"), "--config",
                    "./configs/k5_lite_t2i_sft_hd.yaml", "--prompt", prompt,
                    "--width", "768", "--height", "1280", "--seed", str(args.seed),
                    "--expand_prompt", "0", "--negative_prompt", "photograph, 3d render, cartoon, text, watermark",
                    "--output_filename", str(output)], cwd=root, check=True)
    return "text-only"


def select_row(rows: list[dict[str, str]], name: str) -> dict[str, str]:
    matches = [row for row in rows if row["display_name"].strip().casefold() == name.strip().casefold()]
    if len(matches) != 1:
        raise ValueError(f"Plant not found in registry: {name}")
    return matches[0]


def valid_candidate(name: str) -> bool:
    return bool(name) and all(c.isascii() and (c.isalnum() or c in "-_") for c in name)


def import_candidate(args: argparse.Namespace, repo: Path, row: dict[str, str]) -> None:
    key = keyify(row["display_name"])
    evidence, refs = read_evidence(repo / args.evidence_dir / f"{key}.json", row, repo)
    if not valid_candidate(args.candidate):
        raise ValueError("Invalid candidate name")
    image = Path(args.image).resolve()
    verify_image(image, portrait=True)
    pending = repo / args.pending_dir / key
    pending.mkdir(parents=True, exist_ok=True)
    output = pending / f"{args.candidate}.png"
    sidecar = output.with_suffix(".json")
    if output.exists() or sidecar.exists():
        raise FileExistsError(f"Candidate already exists: {output}")
    metadata = {
        "schema_version": 1, "asset_id": key, "display_name": row["display_name"],
        "file": output.name, "status": "pending-human-review", "backend": "imported",
        "model": "unknown", "conditioning": "unknown",
        "provenance": text(args.provenance, "import provenance and publication rights"),
        "imported_at_utc": datetime.now(timezone.utc).isoformat(),
        "image_sha256": sha256_file(image), "evidence": evidence,
        "evidence_sha256": sha256_json(evidence),
        "reference_sha256": [sha256_file(path) for path in refs],
    }
    shutil.copyfile(image, output)
    write_json(sidecar, metadata)
    print(f"Imported for human review: {output}")


def annotate(args: argparse.Namespace, repo: Path, row: dict[str, str]) -> None:
    from PIL import Image, ImageDraw, ImageFont

    key = keyify(row["display_name"])
    if not valid_candidate(args.candidate) or not valid_candidate(args.output_candidate):
        raise ValueError("Invalid candidate name")
    pending = repo / args.pending_dir / key
    source = pending / f"{args.candidate}.png"
    metadata = json.loads(source.with_suffix(".json").read_text(encoding="utf-8"))
    if metadata.get("status") != "pending-human-review" or metadata.get("asset_id") != key:
        raise ValueError("Source candidate is not pending for this plant")
    if metadata.get("file") != source.name or metadata.get("image_sha256") != sha256_file(source):
        raise ValueError("Source candidate changed since it was recorded")
    verify_image(source, portrait=True)
    layout = json.loads(Path(args.layout).read_text(encoding="utf-8"))
    if not isinstance(layout, dict) or set(layout) != {"labels"} or not isinstance(layout["labels"], list):
        raise ValueError('Layout must contain only a "labels" array')
    labels = []
    for label in layout["labels"]:
        if not isinstance(label, dict) or set(label) != {"text", "x", "y", "target_x", "target_y"}:
            raise ValueError("Each label needs text, x, y, target_x and target_y")
        title = text(label["text"], "label text")
        if "\n" in title or "\r" in title:
            raise ValueError("Labels must be single-line")
        values = [label[k] for k in ("x", "y", "target_x", "target_y")]
        if any(isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1 for v in values):
            raise ValueError("Label coordinates must be numbers between 0 and 1")
        labels.append((title, *values))
    output = pending / f"{args.output_candidate}.png"
    sidecar = output.with_suffix(".json")
    if output.exists() or sidecar.exists():
        raise FileExistsError(f"Candidate already exists: {output}")
    with Image.open(source) as source_image:
        plate = source_image.convert("RGB")
    width, height = plate.size
    draw = ImageDraw.Draw(plate)
    title_font = ImageFont.truetype(args.font, max(12, int(width * 0.06)))
    label_font = ImageFont.truetype(args.font, max(10, int(width * 0.04)))
    ink = (54, 43, 30)
    margin = max(1, int(width * 0.025))
    draw.rectangle((margin, margin, width - margin, height - margin), outline=ink, width=max(1, width // 750))
    draw.text((width / 2, height * 0.035), row["display_name"], font=title_font, fill=ink, anchor="ma")
    for title, x, y, target_x, target_y in labels:
        position = (x * width, y * height)
        draw.text(position, title, font=label_font, fill=ink, anchor="la")
        draw.line((position[0], position[1] + label_font.size * 1.2,
                   target_x * width, target_y * height), fill=ink, width=max(1, width // 1000))
    plate.save(output, format="PNG")
    metadata["file"] = output.name
    metadata["image_sha256"] = sha256_file(output)
    metadata["annotation"] = {
        "source_image_sha256": sha256_file(source),
        "layout": layout,
        "font_sha256": sha256_file(Path(args.font)),
        "title": row["display_name"],
    }
    write_json(sidecar, metadata)
    print(f"Annotated candidate awaiting human review: {output}")


def generate(args: argparse.Namespace, repo: Path, row: dict[str, str]) -> None:
    key = keyify(row["display_name"])
    evidence, refs = read_evidence(repo / args.evidence_dir / f"{key}.json", row, repo)
    if args.backend in ("i1", "kandinsky") and (args.style_reference or args.plantgen):
        raise ValueError(f"{args.backend} is text-only; it cannot use a style image or PlantGen render")
    if args.backend in ("i1", "kandinsky") and args.model:
        raise ValueError(f"{args.backend} uses its documented fixed checkpoint; --model is not supported")
    style = Path(args.style_reference).resolve() if args.style_reference else None
    if style:
        verify_image(style)
    if args.plantgen:
        text(evidence.get("plantgen_species"), "plantgen_species")
    prompt = prompt_for(evidence, bool(style), bool(args.plantgen))
    if args.dry_run:
        print(prompt)
        print(f"\nBackend: {args.backend}; candidate: {args.candidate or f'{args.backend}-{args.seed}'}")
        return
    candidate = args.candidate or f"{args.backend}-{args.seed}"
    if not valid_candidate(candidate):
        raise ValueError("Candidate name may contain only ASCII letters, numbers, hyphens and underscores")
    pending = repo / args.pending_dir / key
    pending.mkdir(parents=True, exist_ok=True)
    output = pending / f"{candidate}.png"
    sidecar = output.with_suffix(".json")
    if output.exists() or sidecar.exists():
        raise FileExistsError(f"Candidate already exists: {output}")
    with tempfile.TemporaryDirectory(prefix="illustration-", dir=pending) as temp:
        temporary = Path(temp)
        inputs = list(refs)
        geometry = None
        if args.plantgen:
            geometry = temporary / "geometry.png"
            subprocess.run([str(Path(args.plantgen).resolve()), "render", evidence["plantgen_species"],
                            "--out", str(geometry), "--view", "three-quarter", "--parts", "on"], check=True)
            verify_image(geometry)
            inputs.append(geometry)
        if style:
            inputs.append(style)
        generated = temporary / "candidate.png"
        conditioning = run_backend(args, prompt, generated, inputs)
        verify_image(generated, portrait=True)
        model = {
            "openai": args.model or DEFAULT_MODEL,
            "gemini": args.model or DEFAULT_GEMINI_MODEL,
            "o1": args.model,
            "i1": "HiDream-ai/HiDream-I1-Full",
            "kandinsky": "kandinskylab/Kandinsky-5.0-T2I-Lite",
        }[args.backend]
        metadata = {
            "schema_version": 1, "asset_id": key, "display_name": row["display_name"],
            "file": output.name, "status": "pending-human-review", "backend": args.backend,
            "model": model, "model_type": args.model_type if args.backend in ("o1", "i1") else None,
            "seed": args.seed if args.backend not in ("openai", "gemini") else None,
            "conditioning": conditioning, "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "prompt": prompt, "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "image_sha256": sha256_file(generated), "evidence": evidence,
            "evidence_sha256": sha256_json(evidence),
            "reference_sha256": [sha256_file(path) for path in refs],
            "style_reference_sha256": sha256_file(style) if style else None,
            "plantgen_sha256": sha256_file(geometry) if geometry else None,
        }
        if geometry:
            shutil.copyfile(geometry, pending / f"{candidate}.geometry.png")
        shutil.copyfile(generated, output)
        write_json(sidecar, metadata)
    print(f"Pending human review: {output}")
    if conditioning == "text-only":
        print("Warning: this backend did not receive photographs; review against them is mandatory.")


def approve(args: argparse.Namespace, repo: Path, row: dict[str, str]) -> None:
    key = keyify(row["display_name"])
    candidate = args.candidate
    if not valid_candidate(candidate):
        raise ValueError("Invalid candidate name")
    image = repo / args.pending_dir / key / f"{candidate}.png"
    metadata = json.loads(image.with_suffix(".json").read_text(encoding="utf-8"))
    if metadata.get("status") != "pending-human-review" or metadata.get("asset_id") != key:
        raise ValueError("Candidate is not pending for this plant")
    if metadata.get("file") != image.name or metadata.get("image_sha256") != sha256_file(image):
        raise ValueError("Candidate image changed after generation")
    evidence, refs = read_evidence(repo / args.evidence_dir / f"{key}.json", row, repo)
    if metadata.get("evidence_sha256") != sha256_json(evidence) or metadata.get("evidence") != evidence:
        raise ValueError("Evidence changed after generation; regenerate the candidate")
    if metadata.get("reference_sha256") != [sha256_file(path) for path in refs]:
        raise ValueError("Reference photographs changed after generation")
    verify_image(image, portrait=True)
    checklist = json.loads(Path(args.checklist).read_text(encoding="utf-8"))
    if not isinstance(checklist, dict) or set(checklist) != set(REVIEW_FIELDS):
        raise ValueError(f"Checklist must contain exactly: {', '.join(REVIEW_FIELDS)}")
    if checklist.get("style") != "pass" or any(checklist.get(k) not in ("pass", "not-depicted") for k in ORGANS):
        raise ValueError("Style must pass and every organ must be pass or not-depicted")
    if checklist["growth_habit"] != "pass" or checklist["leaves"] != "pass":
        raise ValueError("Growth habit and leaves must pass")
    reviewer = text(args.reviewer, "reviewer")
    notes = text(args.notes, "review notes")
    approved_dir = repo / args.output_dir
    approved_dir.mkdir(parents=True, exist_ok=True)
    for existing in approved_dir.iterdir():
        if existing.is_file() and existing.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp") and keyify(existing.stem) == key:
            raise FileExistsError(f"Existing illustration must be versioned or removed explicitly: {existing}")
    target = approved_dir / f"{key}.png"
    target_meta = target.with_suffix(".json")
    if target_meta.exists():
        raise FileExistsError(f"Existing metadata: {target_meta}")
    metadata["file"] = target.name
    metadata["status"] = "human-reviewed-approved"
    metadata["review"] = {"reviewer": reviewer, "reviewed_at_utc": datetime.now(timezone.utc).isoformat(),
                          "notes": notes, "checklist": checklist}
    shutil.copyfile(image, target)
    write_json(target_meta, metadata)
    print(f"Approved: {target}; commit the PNG and JSON sidecar together.")


def generate_pending_candidates(args: argparse.Namespace, repo: Path, rows: list[dict[str, str]]) -> None:
    """Generate Gemini concept candidates without claiming botanical verification.

    These candidates are review material only. They do not satisfy the human
    evidence gate and cannot be approved or embedded by the publication builder.
    """
    candidate = args.candidate
    if not valid_candidate(candidate):
        raise ValueError("Invalid candidate name")
    model = args.model or DEFAULT_GEMINI_MODEL
    pending_root = repo / args.pending_dir
    generated: list[str] = []
    blocked: list[str] = []

    for row in rows:
        key = keyify(row["display_name"])
        pending = pending_root / key
        pending.mkdir(parents=True, exist_ok=True)
        output = pending / f"{candidate}.png"
        sidecar = output.with_suffix(".json")
        if output.exists() and sidecar.exists():
            generated.append(row["display_name"])
            continue

        evidence_path = repo / args.evidence_dir / f"{key}.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8")) if evidence_path.is_file() else evidence_template(row)
        prompt = (
            f"Create one useful, portrait 2:3 botanical illustration concept for {row['display_name']}. "
            "This common name is unverified and may describe several taxa or cultivars. "
            "Do not claim a scientific identity, invent a cultivar, add text or labels, or depict a guaranteed anatomical arrangement. "
            "Use a coherent warm-paper field-guide composition with fine ink linework and restrained natural watercolor. "
            "Make the whole specimen, growth habit, leaves, flowers, fruit, and roots recognizable enough for a human reviewer to work from, "
            "but leave uncertain structures understated rather than fictional. No borders, lettering, border text, or watermark."
        )

        try:
            with tempfile.TemporaryDirectory(prefix="gemini-candidate-", dir=pending) as temp:
                temporary = Path(temp) / "candidate.png"
                last_error: Exception | None = None
                for attempt in range(3):
                    try:
                        generate_gemini(prompt, temporary, model, [])
                        break
                    except (RuntimeError, OSError) as exc:
                        last_error = exc
                        import time
                        time.sleep(2 * (attempt + 1))
                else:
                    raise RuntimeError(str(last_error or "Gemini candidate generation failed"))
                verify_image(temporary, portrait=True)
                metadata = {
                    "schema_version": 1,
                    "asset_id": key,
                    "display_name": row["display_name"],
                    "file": output.name,
                    "status": "pending-human-review",
                    "backend": "gemini",
                    "model": model,
                    "conditioning": "text-only; common-name concept",
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(),
                    "prompt": prompt,
                    "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                    "image_sha256": sha256_file(temporary),
                    "evidence": evidence,
                    "evidence_sha256": sha256_json(evidence),
                    "reference_sha256": [],
                    "style_reference_sha256": None,
                    "plantgen_sha256": None,
                    "provenance": "Gemini concept candidate; not botanical evidence, not independently identified, and not licensed for publication.",
                }
                shutil.copyfile(temporary, output)
                write_json(sidecar, metadata)
            generated.append(row["display_name"])
            print(f"Pending Gemini candidate: {output}")
        except (OSError, ValueError, RuntimeError) as exc:
            blocked.append(f"{row['display_name']}: {exc}")
            print(f"Blocked {row['display_name']}: {exc}", file=sys.stderr)

    report = repo / "gemini_generation_report.txt"
    report.write_text(
        f"Generated candidates: {len(generated)}\n"
        f"Blocked records: {len(blocked)}\n"
        + "\n".join(blocked)
        + "\n",
        encoding="utf-8",
    )
    print(f"Generated pending Gemini candidates: {len(generated)}; blocked: {len(blocked)}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--registry", default="plant_registry_enriched.csv")
    parser.add_argument("--evidence-dir", default="botanical_evidence")
    parser.add_argument("--pending-dir", default="plant_illustrations/pending_review")
    parser.add_argument("--output-dir", default="plant_illustrations")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("templates")
    review_parser = commands.add_parser("review-template")
    review_parser.add_argument("--output", type=Path, required=True)
    pending_candidates = commands.add_parser("generate-pending-candidates")
    pending_candidates.add_argument("--candidate", required=True)
    pending_candidates.add_argument("--model")
    generation = commands.add_parser("generate")
    generation.add_argument("--plant", required=True)
    generation.add_argument("--backend", choices=("openai", "gemini", "o1", "i1", "kandinsky"), default="openai")
    generation.add_argument("--backend-dir")
    generation.add_argument("--backend-python", default=sys.executable)
    generation.add_argument("--model")
    generation.add_argument("--model-type", choices=("full", "dev", "fast"), default="full")
    generation.add_argument("--seed", type=int, default=32)
    generation.add_argument("--candidate")
    generation.add_argument("--style-reference")
    generation.add_argument("--plantgen", help="Path to the plantc executable")
    generation.add_argument("--dry-run", action="store_true")
    imported = commands.add_parser("import")
    imported.add_argument("--plant", required=True)
    imported.add_argument("--candidate", required=True)
    imported.add_argument("--image", required=True)
    imported.add_argument("--provenance", required=True, help="Record origin and publication rights")
    annotation = commands.add_parser("annotate")
    annotation.add_argument("--plant", required=True)
    annotation.add_argument("--candidate", required=True)
    annotation.add_argument("--output-candidate", required=True)
    annotation.add_argument("--layout", required=True, help="JSON file of reviewed label positions")
    annotation.add_argument("--font", default=str(DEFAULT_FONT),
                            help="Licensed TrueType/OpenType font (default: Reenie Beanie)")
    approval = commands.add_parser("approve")
    approval.add_argument("--plant", required=True)
    approval.add_argument("--candidate", required=True)
    approval.add_argument("--checklist", required=True)
    approval.add_argument("--reviewer", required=True)
    approval.add_argument("--notes", required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    try:
        if args.command == "review-template":
            if args.output.exists():
                raise FileExistsError(args.output)
            write_json(args.output, {field: "" for field in REVIEW_FIELDS})
            print(f"Created review checklist: {args.output}")
            return 0
        rows = read_registry(repo / args.registry)
        if args.command == "templates":
            created = 0
            for row in rows:
                target = repo / args.evidence_dir / f"{keyify(row['display_name'])}.json"
                if not target.exists():
                    write_json(target, evidence_template(row))
                    created += 1
            print(f"Created {created} evidence templates; verification is required before generation.")
        elif args.command == "generate":
            generate(args, repo, select_row(rows, args.plant))
        elif args.command == "generate-pending-candidates":
            generate_pending_candidates(args, repo, rows)
        elif args.command == "import":
            import_candidate(args, repo, select_row(rows, args.plant))
        elif args.command == "annotate":
            annotate(args, repo, select_row(rows, args.plant))
        else:
            approve(args, repo, select_row(rows, args.plant))
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
