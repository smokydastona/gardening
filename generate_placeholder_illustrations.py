"""Generate neutral pending placeholders for every plant record.

These are publication workflow cards, not botanical illustrations. They intentionally
contain no species anatomy and cannot be approved or embedded by the publication
builder without independent evidence and human review.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE_DIR = Path(__file__).resolve().parent
PENDING_DIR = BASE_DIR / "plant_illustrations" / "pending_review"
EVIDENCE_DIR = BASE_DIR / "botanical_evidence"


def keyify(value: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", value.upper()).strip("_")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_json(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def read_registry() -> list[dict[str, str]]:
    with (BASE_DIR / "plant_registry.csv").open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def make_placeholder(row: dict[str, str]) -> tuple[Path, Path]:
    key = keyify(row["display_name"])
    evidence_path = EVIDENCE_DIR / f"{key}.json"
    if not evidence_path.is_file():
        raise FileNotFoundError(f"Missing evidence template: {evidence_path}")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))

    pending = PENDING_DIR / key
    pending.mkdir(parents=True, exist_ok=True)
    output = pending / "pending-placeholder.png"
    sidecar = output.with_suffix(".json")
    if output.exists() and sidecar.exists():
        existing = json.loads(sidecar.read_text(encoding="utf-8"))
        if existing.get("status") == "pending-human-review" and existing.get("asset_id") == key:
            if existing.get("file") == output.name and existing.get("image_sha256") == sha256_file(output):
                return output, sidecar

    width, height = 1024, 1536
    image = Image.new("RGB", (width, height), "#f6f0e2")
    draw = ImageDraw.Draw(image)
    ink = "#2d2a26"
    green = "#51664e"
    draw.rectangle((38, 38, width - 38, height - 38), outline=green, width=8)
    draw.rectangle((58, 58, width - 58, height - 58), outline="#927f61", width=3)

    font_regular = BASE_DIR / "fonts" / "TheGirlNextDoor.ttf"
    if font_regular.is_file():
        title_font = ImageFont.truetype(str(font_regular), 84)
        small_font = ImageFont.truetype(str(font_regular), 42)
    else:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    title = row["display_name"]
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = bbox[2] - bbox[0]
    draw.text(((width - title_width) / 2, 280), title, font=title_font, fill=ink)

    draw.line((180, 390, width - 180, 390), fill="#927f61", width=4)
    draw.text((width / 2, 620), "BOTANICAL ILLUSTRATION", font=small_font, fill=green, anchor="ma")
    draw.text((width / 2, 690), "PENDING HUMAN REVIEW", font=small_font, fill=green, anchor="ma")
    draw.text((width / 2, 790), "NOT A BOTANICAL DEPICTION", font=small_font, fill=ink, anchor="ma")
    draw.text((width / 2, 860), "No identity or license verified", font=small_font, fill=ink, anchor="ma")

    image.save(output, format="PNG")

    metadata = {
        "schema_version": 1,
        "asset_id": key,
        "display_name": row["display_name"],
        "file": output.name,
        "status": "pending-human-review",
        "backend": "local-pending-placeholder",
        "model": "deterministic-plant-card-v1",
        "conditioning": "none",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "provenance": "Repository-generated neutral workflow placeholder; does not depict the species.",
        "creator": "Errington Gardening Encyclopedia pipeline",
        "license": "Unclaimed; placeholder is not a botanical illustration and must not be published as such.",
        "image_sha256": sha256_file(output),
        "evidence": evidence,
        "evidence_sha256": sha256_json(evidence),
        "reference_sha256": [],
        "style_reference_sha256": None,
        "plantgen_sha256": None,
    }
    sidecar.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return output, sidecar


def main() -> int:
    registry = read_registry()
    created = 0
    for row in registry:
        key = keyify(row["display_name"])
        before = (PENDING_DIR / key / "pending-placeholder.png").exists()
        make_placeholder(row)
        if not before:
            created += 1
    print(f"Pending placeholder cards ready: {len(registry)}; newly created: {created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
