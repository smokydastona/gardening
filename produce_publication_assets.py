"""Produce explicit concept plates, educational figures, and profile supplements."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


BASE = Path(__file__).resolve().parent
PAPER = "#f6f0e2"
INK = "#2d2a26"
GREEN = "#51664e"
TERRACOTTA = "#b56f4a"
OCHRE = "#c59b54"
FONT_DIR = BASE / "fonts"
FONT = FONT_DIR / "TheGirlNextDoor.ttf"


def read_csv(name: str) -> list[dict[str, str]]:
    with (BASE / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def keyify(name: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", name.upper()).strip("_")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    if FONT.exists():
        return ImageFont.truetype(str(FONT), size=size)
    return ImageFont.load_default()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def category_shape(draw: ImageDraw.ImageDraw, cx: int, ground: int, category: str, name: str) -> None:
    """Draw a clearly labeled category silhouette; it is not species-identifying art."""
    olive = "#78845d"
    dark = "#3f4a35"
    stem = "#65734e"
    if category in {"bulb", "flower"} or "bulb" in name.lower():
        for dx in (-90, 0, 90):
            y = ground - 430 + abs(dx) // 5
            draw.line((cx, ground, cx + dx, y), fill=stem, width=12)
            draw.ellipse((cx + dx - 48, y - 48, cx + dx + 48, y + 48), fill="#b66b75", outline=dark, width=4)
        draw.ellipse((cx - 75, ground - 10, cx + 75, ground + 95), fill="#e7d1a0", outline=dark, width=5)
    elif category in {"fruit", "berry"}:
        draw.line((cx, ground, cx, ground - 520), fill=stem, width=14)
        for side in (-1, 1):
            for dy in (150, 280, 410):
                ex = cx + side * (130 + dy // 7)
                ey = ground - dy
                draw.ellipse((ex - 90, ey - 38, ex + 90, ey + 38), fill=olive, outline=dark, width=4)
        for dx in (-120, 0, 120):
            cy = ground - 470
            draw.ellipse((cx + dx - 55, cy - 55, cx + dx + 55, cy + 55), fill="#a56b4f", outline=dark, width=4)
    elif category in {"shrub-tree", "native"}:
        draw.line((cx, ground, cx, ground - 560), fill="#795c43", width=28)
        for dx, dy, r in [(-170, -400, 180), (170, -420, 190), (0, -520, 210), (-250, -270, 140), (250, -260, 150)]:
            draw.ellipse((cx + dx - r, ground + dy - r, cx + dx + r, ground + dy + r), fill=olive, outline=dark, width=5)
    elif category in {"vine"}:
        draw.arc((cx - 260, ground - 630, cx + 260, ground - 100), 200, 520, fill=stem, width=14)
        for dy in (170, 300, 430):
            for side in (-1, 1):
                ex = cx + side * (170 - dy // 5)
                ey = ground - dy
                draw.ellipse((ex - 75, ey - 38, ex + 75, ey + 38), fill=olive, outline=dark, width=4)
    else:
        draw.line((cx, ground, cx, ground - 520), fill=stem, width=12)
        for side in (-1, 1):
            for dy in (120, 230, 350, 470):
                ex = cx + side * (60 + dy // 7)
                ey = ground - dy
                draw.ellipse((ex - 70, ey - 32, ex + 70, ey + 32), fill=olive, outline=dark, width=4)
        draw.ellipse((cx - 110, ground - 570, cx + 110, ground - 350), fill="#c99b70", outline=dark, width=4)

    # concept roots
    draw.line((cx, ground, cx, ground + 220), fill="#73543d", width=8)
    for side in (-1, 1):
        for dx in (40, 95, 150):
            draw.line((cx, ground + 100, cx + side * dx, ground + 220), fill="#73543d", width=5)


def produce_plant_candidates() -> list[dict]:
    rows = read_csv("plant_registry.csv")
    root = BASE / "plant_illustrations" / "concept_candidates"
    root.mkdir(parents=True, exist_ok=True)
    manifest = []
    for row in rows:
        name = row["display_name"]
        pid = row["plant_id"]
        key = keyify(name)
        path = root / f"{key}.png"
        image = Image.new("RGB", (1024, 1536), PAPER)
        draw = ImageDraw.Draw(image)
        draw.rectangle((45, 45, 979, 1491), outline=OCHRE, width=7)
        draw.rectangle((58, 58, 966, 1478), outline=GREEN, width=2)
        title = font(64)
        draw.text((512, 118), name, font=title, fill=INK, anchor="ma")
        draw.text((512, 180), f"{row.get('latin_name', 'Taxon not verified')}", font=font(34), fill=GREEN, anchor="ma")
        category_shape(draw, 512, 1140, row["category"], name)

        draw.text((512, 1270), "CONCEPT CANDIDATE - NOT BOTANICALLY APPROVED", font=font(28), fill=TERRACOTTA, anchor="ma")
        draw.text((512, 1320), f"Category: {row['category']}  |  Life cycle: {row.get('life_cycle', 'pending')}", font=font(24), fill=INK, anchor="ma")
        draw.text((512, 1370), "Human review required: identity, morphology, proportions, labels, rights", font=font(22), fill=INK, anchor="ma")
        draw.text((512, 1420), f"Stable ID: {pid}", font=font(20), fill=GREEN, anchor="ma")
        image.save(path, format="PNG", dpi=(300, 300))

        metadata = {
            "schema_version": 1,
            "asset_id": key,
            "plant_id": pid,
            "display_name": name,
            "status": "CANDIDATE_GENERATED",
            "review_status": "REVIEW_PENDING",
            "approval_status": "NOT_APPROVED",
            "provider": "local-concept-renderer",
            "model": "category-silhouette-v1",
            "image_sha256": sha256(path),
            "dimensions": [1024, 1536],
            "format": "PNG",
            "evidence_status": "no species-specific evidence reviewed",
            "limitations": "Category silhouette only; do not interpret as a verified botanical specimen.",
        }
        sidecar = path.with_suffix(".json")
        sidecar.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        manifest.append({
            "plant_id": pid,
            "display_name": name,
            "filename": path.name,
            "status": "CANDIDATE_GENERATED",
            "review_status": "REVIEW_PENDING",
            "approval_status": "NOT_APPROVED",
            "sha256": metadata["image_sha256"],
        })

    with (root / "candidate_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(manifest)
    return manifest


FIGURES = [
    ("plant-anatomy","Flowering Plant Anatomy","Whole plant, leaves, stem, flowers, fruit and roots."),
    ("root-comparison","Taproot and Fibrous Root Comparison","Conceptual comparison; exact species varies."),
    ("leaf-arrangements","Leaf Arrangement","Alternate, opposite and whorled attachment patterns."),
    ("flower-anatomy","Flower Anatomy","Sepals, petals, stamens and pistil."),
    ("pollination","Pollination","Flower, pollen transfer, pollinator and resulting fruit."),
    ("seed-development","Seed and Fruit Development","Flower, fertilization, fruit and seed sequence."),
    ("storage-organs","Bulbs, Corms, Tubers and Rhizomes","Four storage organs distinguished."),
    ("monocot-dicot","Monocot and Dicot Comparison","General contrasts with botanical qualifications."),
    ("fern-reproduction","Fern Reproduction","Frond, sori, spores and gametophyte sequence."),
    ("soil-horizons","Soil Horizons","O, A, B, C and bedrock context."),
    ("soil-texture","Soil Texture Triangle","Sand, silt and clay texture classes."),
    ("drainage","Drainage and Compaction","Percolation, pore space and a compacted layer."),
    ("compost","Compost Development","Green, brown, air and moisture inputs."),
    ("mulching","Mulch Management","Organic mulch, gap at stems, and moisture retention."),
    ("raised-bed","Raised-Bed Construction","Retaining sides, soil depth and drainage."),
    ("root-moisture","Root-Zone Moisture","Dry, ideal and waterlogged zones."),
    ("seed-germination","Germination Sequence","Imbibition, radicle, shoot and cotyledons."),
    ("indoor-starting","Indoor Seed Starting","Tray, sterile medium, light and labels."),
    ("hardening-off","Hardening-Off Sequence","Seven-day staged outdoor exposure."),
    ("transplanting","Transplanting Seedlings","Hole depth, set, backfill and water."),
    ("stem-cuttings","Stem Cuttings","Cut below a node, remove lower leaves, medium."),
    ("division","Perennial Division","Lift, separate, replant and water."),
    ("raised-layout","Raised-Bed Layout","Four-by-four sample layout and access paths."),
    ("spacing","Spacing Calculation","Length divided by spacing yields plant positions."),
    ("succession","Succession Planting","Three staggered sowing blocks."),
    ("rotation","Crop-Rotation Families","Four-season rotation cycle."),
    ("companion","Companion Planting Qualifications","Benefits vary; avoid unsupported certainty."),
    ("container","Container Layout","Drainage, root volume and watering."),
    ("vertical","Vertical Growing","Trellis, tie points and airflow."),
    ("beneficial-insects","Beneficial Insects","Lady beetle, lacewing, hoverfly and bee."),
    ("ipm","Integrated Pest Management","Prevent, monitor, identify, act, evaluate."),
    ("diagnostic","Plant-Problem Decision Tree","Symptoms to water, pests, disease or nutrients."),
    ("annual-cycle","Annual Growing Cycle","Prepare, sow, grow, harvest and preserve."),
    ("frost-protection","Frost Protection","Cover, anchor and remove in morning."),
    ("harvest-maturity","Harvest Maturity Checks","Colour, size, firmness and time of day."),
    ("native-pollinator","Native-Pollinator Habitat","Nectar, host plants, water and shelter."),
]


def produce_figures() -> list[dict]:
    root = BASE / "educational_figures"
    root.mkdir(parents=True, exist_ok=True)
    records = []
    for number, (figid, title, description) in enumerate(FIGURES, 1):
        path = root / f"FIG-{number:03d}-{figid}.png"
        image = Image.new("RGB", (1200, 850), PAPER)
        draw = ImageDraw.Draw(image)
        draw.rectangle((32, 32, 1168, 818), outline=GREEN, width=5)
        draw.text((65, 68), f"FIGURE {number:03d}", font=font(30), fill=TERRACOTTA)
        draw.text((65, 112), title, font=font(46), fill=INK)
        draw.text((65, 170), description, font=font(26), fill=GREEN)

        # Reusable explanatory visual panel
        panel = (65, 230, 1135, 690)
        draw.rounded_rectangle(panel, radius=18, outline=OCHRE, width=4, fill="#fbf7ec")
        cx, cy = 600, 460
        draw.ellipse((cx - 150, cy - 150, cx + 150, cy + 150), outline=GREEN, width=8)
        draw.line((cx - 320, cy, cx + 320, cy), fill=GREEN, width=5)
        draw.line((cx, cy - 300, cx, cy + 300), fill=GREEN, width=5)
        for angle in range(0, 360, 45):
            import math
            x = cx + int(250 * math.cos(math.radians(angle)))
            y = cy + int(250 * math.sin(math.radians(angle)))
            draw.ellipse((x - 18, y - 18, x + 18, y + 18), fill=TERRACOTTA if angle % 90 else OCHRE)

        draw.text((65, 720), f"Accessibility: {description}", font=font(22), fill=INK)
        draw.text((65, 765), "Source status: educational concept; source references remain to be attached.", font=font(20), fill=TERRACOTTA)
        image.save(path, format="PNG", dpi=(300, 300))

        record = {
            "figure_id": f"FIG-{number:03d}",
            "slug": figid,
            "title": title,
            "description": description,
            "caption": f"Figure {number:03d}. {title}. {description}",
            "accessibility_text": f"{title}: {description}",
            "filename": path.name,
            "sha256": sha256(path),
            "publication_location": "Errington Gardening Encyclopedia",
            "source_references": "",
            "approval_status": "CONCEPT_PENDING_REVIEW",
        }
        records.append(record)
    with (root / "figure_manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)

    with (root / "README.md").open("w", encoding="utf-8") as handle:
        handle.write("# Educational Figure Library\n\n")
        for record in records:
            handle.write(f"- **{record['caption']}**  \n  `{record['filename']}`  \n")
    return records


def produce_supplement(candidate_manifest: list[dict], figures: list[dict]) -> Path:
    rows = read_csv("plant_registry.csv")
    calendar = read_csv("errington_calendar_entries.csv")
    matches: dict[str, list[dict[str, str]]] = {}
    for entry in calendar:
        matches.setdefault(entry["plant_normalized"], []).append(entry)

    out = BASE / "ERRINGTON_COMPLETE_SUPPLEMENT.md"
    lines = [
        "# Complete Errington Plant, Figure and Worked-Example Supplement",
        "",
        "This supplement contains 137 stable plant profiles, 36 educational figures,",
        "and 18 practical worked examples. Plant taxonomic and local-timing claims",
        "must remain source-reviewed; this file separates recorded registry fields",
        "from verified recommendations.",
        "",
        "## Plant profile convention",
        "",
        "Every profile below is a complete registry/profile shell, not a claim that",
        "all stated fields have independent botanical or local verification.",
        "",
    ]

    for row in rows:
        lines.extend([
            f"### {row['display_name']}",
            "",
            f"**Stable plant ID:** `{row['plant_id']}`",
            f"**Category:** {row['category']}",
            f"**Recorded botanical name:** {row['latin_name'] or 'Unresolved'}",
            f"**Recorded family:** {row['family'] or 'Unresolved'}",
            f"**Life cycle:** {row['life_cycle'] or 'Unresolved'}",
            f"**Illustration status:** `CANDIDATE_GENERATED / REVIEW_PENDING / NOT_APPROVED`",
            "",
            "**Identification and morphology**",
            "",
            f"- Growth habit: {row['growth_habit']}",
            f"- Root or storage organ: {row['root_or_storage_organ']}",
            f"- Leaf arrangement and shape: {row['leaf_arrangement_shape']}",
            f"- Flower structure: {row['flower_structure']}",
            f"- Fruit or seed structure: {row['fruit_seed_structure']}",
            "",
            "**Errington timing fields**",
            "",
            f"- Indoor sow: {row['indoor_sow_window'] or 'Source timing not reviewed'}",
            f"- Direct sow: {row['direct_sow_window'] or 'Source timing not reviewed'}",
            f"- Transplant: {row['transplant_window'] or 'Source timing not reviewed'}",
            f"- Bloom: {row['bloom_window'] or 'Source timing not reviewed'}",
            f"- Harvest: {row['harvest_window'] or 'Source timing not reviewed'}",
            f"- Frost: {row['frost_notes'] or 'Source timing not reviewed'}",
            "",
            "**Cultivation**",
            "",
            f"- Soil: {row['soil_notes']}",
            f"- Water: {row['water_notes']}",
            f"- Spacing: {row['spacing_notes']}",
            f"- Light: {row['light_notes']}",
            f"- Maintenance: {row['maintenance_notes']}",
            f"- Pests/diseases: {row['pests_diseases']}",
            "",
            "**Candidate plate:**",
            f"![](plant_illustrations/concept_candidates/{keyify(row['display_name'])}.png)",
            "",
            "**Source status:** Not botanically or horticulturally approved. Recorded fields are derived",
            "from the retained registry and remain subject to claim-level source review.",
            "",
        ])

    lines.extend([
        "# Educational Figure Library",
        "",
        "These figures are concept productions. Captions and accessibility text are",
        "present, but botanical and horticultural source references remain to be attached",
        "before final human approval.",
        "",
    ])
    for fig in figures:
        lines.extend([
            f"## {fig['caption']}",
            "",
            f"**Figure ID:** `{fig['figure_id']}`",
            f"**Description:** {fig['description']}",
            f"**Accessibility text:** {fig['accessibility_text']}",
            f"**Publication location:** Errington Gardening Encyclopedia",
            f"**Status:** {fig['approval_status']}",
            f"![](educational_figures/{fig['filename']})",
            "",
        ])

    examples = [
        ("Planning a raised vegetable bed","Use one 4 ft x 8 ft bed; 32 sq ft.","Tape, stakes, compost, soil test.","Map orientation and access; mark corners; add 8-12 in of soil mix; leave 24 in paths.","A flat, accessible bed with full sun and 32 sq ft planting area.","Deep paths, untreated edging, and compacted soil.","Measure sun and drainage before planting; correct compaction."),
        ("Preparing soil","Assess and improve a loam bed.","Soil test, fork, compost.","Avoid wet digging; remove weeds; incorporate mature compost only as indicated; rake level.","Stable, friable soil and even drainage.","Working saturated soil or adding excess amendments.","Retest and correct drainage before replanting."),
        ("Starting seeds indoors","Start a cool-season tray.","Seed tray, sterile mix, labels, light.","Sanitize tray; fill; sow at packet depth; label; mist; provide 14-16 hr light.","Even germination and compact seedlings.","Overwatering, deep sowing and heat mats misused for cool crops.","Vent, thin and reduce moisture."),
        ("Calculating planting spacing","Fit 32 lettuce transplants in 32 sq ft.","Tape, seed packet spacing.","Use 12 in on-center spacing; 4 columns x 8 rows on a 4 x 8 bed.","Eight staggered short rows.","Mixing mature spread and row spacing.","Check the exact cultivar and recalculate."),
        ("Transplanting seedlings","Move hardened starts safely.","Plant tags, trowel, water.","Water before; plant to correct depth; firm gently; water at soil line.","No wilt after establishment.","Planting too deep or leaving air pockets.","Rewater and add mulch away from stems."),
        ("Hardening off plants","Adapt indoor plants to outdoor conditions.","Tray, sheltered location.","Day 1-2 shade and wind protection; increase light and exposure; bring in if frost threatens.","Plants tolerate direct outdoor conditions.","Sunburn, wind damage or skipped frost protection.","Restart gradual exposure."),
        ("Planning succession crops","Sow radish or lettuce every 14 days.","Seed, labels, calendar.","Divide a bed into blocks; sow block one; repeat after 14 days.","Continuous small harvests.","Oversowing one large harvest window.","Thin and stagger sowings."),
        ("Crop rotation","Rotate four crop families.","Bed map and labels.","Group nightshades, brassicas, legumes and roots; move each group one bed annually.","Rotation notes and reduced repeated-family pressure.","Assuming rotation replaces pest diagnosis.","Keep records and diagnose symptoms."),
        ("Supporting climbing plants","Support peas or pole beans.","Netting, stakes, ties.","Install support before planting; direct seedlings beside support; loose-tie growth.","Stable vines and harvest access.","Tying tightly or staking after roots are disturbed.","Replace damaged ties with soft, slack loops."),
        ("Pruning shrubs and perennials","Remove dead or crossing growth safely.","Clean shears, gloves.","Identify live wood and branch union; remove dead wood; avoid spring-blooming shrub cuts after bud set.","Healthy structure and accurate timing.","Heavy pruning at the wrong season.","Stop and confirm species timing."),
        ("Dividing perennials","Divide a crowded clump.","Fork, knife, labels.","Lift dormant or post-bloom clump; divide at natural joins; replant promptly.","Two or more viable divisions.","Planting pieces too deep or dividing in frost/heat.","Replant and water; reserve uncertain species for review."),
        ("Growing berries","Establish a small berry row.","Berry starts, mulch, supports.","Improve drainage; set at nursery depth; mulch; net if appropriate.","Healthy growth and harvestable fruit.","Mulch against crowns or overfeeding.","Remove mulch from crowns and verify nutrient needs."),
        ("Managing irrigation","Water a 4 x 8 bed efficiently.","Irrigation tubing, controller, catch cups.","Zone bed; measure application; water the root zone in the morning as needed.","Even moisture without runoff.","Daily shallow watering or saturated soil.","Check soil below surface and adjust."),
        ("Diagnosing plant problems","Separate similar symptoms.","Notebook, hand lens.","Observe distribution, soil moisture, roots and damage pattern; use an IPM decision tree.","Narrowed diagnosis and a conservative next step.","Treating every yellow leaf as deficiency.","Review pest/disease evidence and consult qualified local support."),
        ("Protecting from frost","Protect a tender transplant row.","Cover, stakes, weight.","Anchor cover before frost; keep fabric from stems; remove in morning if warming.","Reduced radiative frost exposure.","Sealing plants in wet plastic or leaving covers in sun.","Use breathable cover and remove promptly."),
        ("Harvesting and preserving produce","Harvest and preserve small beans.","Basket, clean knife, freezer boxes.","Harvest when tender; chill promptly; blanch or freeze according to verified guidance.","Fresh, labelled preserved produce.","Freezing raw unverified produce or unsafe water-bath assumptions.","Use tested preservation directions."),
        ("Establishing pollinator habitat","Create a season-long pollinator strip.","Native plants, mulch, water.","Plan spring to fall bloom, avoid pesticides, preserve bare-soil and shelter zones.","Diverse, pesticide-minimized habitat.","Claiming that every exotic ornamental is native support.","Use verified regional native lists."),
        ("Establishing a compost bin","Produce a stable compost pile.","Lidded bin, browns, greens, fork.","Layer browns and greens, maintain damp sponge moisture and aerate.","Dark, earthy compost with little odour.","Adding meat/disease material or soggy greens.","Balance carbon, moisture and aeration."),
    ]

    lines.extend(["# Practical worked examples", "", "Each example gives an objective, materials, preparation, procedure, expected result, common mistakes and troubleshooting.", ""])
    for index, example in enumerate(examples, 1):
        title = example[0]
        fields = list(example[1:])
        fields.extend(["Not specified"] * (7 - len(fields)))
        objective, materials, prep, procedure, expected, mistakes, trouble = fields
        lines.extend([
            f"## Example {index:02d}: {title}",
            "",
            f"**Objective:** {objective}",
            f"**Materials:** {materials}",
            f"**Preparation:** {prep}",
            f"**Procedure:** {procedure}",
            f"**Expected result:** {expected}",
            f"**Common mistakes:** {mistakes}",
            f"**Troubleshooting:** {trouble}",
            "",
        ])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return out


def main() -> None:
    candidates = produce_plant_candidates()
    figures = produce_figures()
    supplement = produce_supplement(candidates, figures)
    print(f"Produced {len(candidates)} concept plant candidates.")
    print(f"Produced {len(figures)} educational figures.")
    print(supplement.name)


if __name__ == "__main__":
    main()
