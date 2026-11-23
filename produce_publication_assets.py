"""Produce explicit concept plates, educational figures, and profile supplements."""

from __future__ import annotations

import csv
import hashlib
import json
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from enrich_plant_registry import entry_aliases, registry_aliases


BASE = Path(__file__).resolve().parent
PAPER = "#f6f0e2"
INK = "#2d2a26"
GREEN = "#51664e"
TERRACOTTA = "#b56f4a"
OCHRE = "#c59b54"
FONT_DIR = BASE / "fonts"
FONT = FONT_DIR / "ReenieBeanie.ttf"

PLANT_SECTIONS = (
    ("Vegetables and Perennial Edibles", frozenset({"vegetable", "perennial-edible"})),
    ("Herbs", frozenset({"herb"})),
    ("Fruits and Berries", frozenset({"fruit"})),
    ("Flowers, Ornamentals, Shrubs, Trees, and Vines", frozenset({"flower", "ornamental", "shrub-tree", "vine"})),
    ("Native Plant Candidates", frozenset({"native"})),
    ("Other Plant Records", frozenset({""})),
)


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
    claim_path = BASE / "claims" / "CLAIM_SOURCES.csv"
    claims = read_csv("claims/CLAIM_SOURCES.csv") if claim_path.is_file() else []

    out = BASE / "ERRINGTON_COMPLETE_SUPPLEMENT.md"
    lines = [
        "# Errington Plant Field Index and Learning Aids",
        "",
        "This section brings together the repository's plant inventory, matching calendar",
        "transcriptions, available plant-claim research notes, educational figure concepts,",
        "and practical worked examples. A source transcription or recorded name is not a",
        "verified recommendation. Plant-specific soil, water, spacing, pest, and disease",
        "guidance is not independently reviewed in this repository.",
        "",
        "## How to use the plant index",
        "",
        "Use the monthly reference for the complete source transcription. The entries below",
        "are a cross-reference, not additional planting advice. Calendar matches are shown",
        "verbatim with their source month and page. When a source row names multiple plants,",
        "the whole grouped row is retained; it does not establish a separate timing for each",
        "plant. All recorded taxonomy remains unverified; names marked for resolution need further research.",
        "Entries are alphabetical within their recorded categories; a category, including",
        "native status, is a project classification and is not independent verification.",
        "For the full field layout and evidence requirements, see the Grower's Handbook.",
        "",
    ]

    section_by_category = {
        category: section
        for section, categories in PLANT_SECTIONS
        for category in categories
    }
    unknown_categories = sorted({
        row.get("category", "") for row in rows
        if row.get("category", "") not in section_by_category
    })
    if unknown_categories:
        raise ValueError(f"Unrecognized plant categories: {', '.join(unknown_categories)}")
    section_order = {section: index for index, (section, _) in enumerate(PLANT_SECTIONS)}
    rows = sorted(
        rows,
        key=lambda row: (
            section_order[section_by_category[row.get("category", "")]],
            row["display_name"].casefold(),
            row.get("plant_id", ""),
        ),
    )
    current_section = None
    for row in rows:
        section = section_by_category[row.get("category", "")]
        if section != current_section:
            lines.extend([f"## {section}", ""])
            current_section = section
        aliases = registry_aliases(row)
        plant_matches = [
            entry
            for entry in calendar
            if aliases
            & entry_aliases(
                entry.get("plant_text", "") or entry.get("plant_normalized", "")
            )
        ]
        plant_claims = [
            claim for claim in claims if claim.get("plant_id") == row.get("plant_id")
        ]
        lines.extend([
            f"### {row['display_name']}",
            "",
            f"**Stable plant ID:** `{row['plant_id']}`\\",
            f"**Category:** {row.get('category') or 'Unresolved'}\\",
            "**Botanical name as recorded (unverified):** "
            f"{row.get('latin_name') or 'Unresolved'}\\",
            "**Family as recorded (unverified):** "
            f"{row.get('family') or 'Unresolved'}\\",
            "**Life cycle as recorded (unverified):** "
            f"{row.get('life_cycle') or 'Unresolved'}\\",
            "**Growing profile:** Plant-specific light, water, soil, hardiness, size, "
            "planting, cultivation, pests, harvest, and storage remain pending verification.",
            "",
            "**Errington calendar source mentions**",
            "",
        ])
        if plant_matches:
            for entry in plant_matches:
                source_name = (
                    entry.get("plant_text", "")
                    or entry.get("plant_normalized", "")
                )
                grouped = "/" in source_name or "," in source_name
                group_note = (
                    " — grouped source entry; individual timing is unresolved"
                    if grouped
                    else ""
                )
                transcription = (
                    entry.get("row_text", "")
                    or entry.get("plant_text", "")
                    or "Transcription unavailable"
                )
                lines.append(
                    f"- **{entry.get('month') or 'Month unresolved'}, source p. "
                    f"{entry.get('page_number') or 'unresolved'}** — "
                    f"{transcription}{group_note}"
                )
        else:
            lines.append("- No matching plant-specific calendar row in the current transcription.")
        lines.extend(["", "**Available plant-claim research notes**", ""])
        if plant_claims:
            for claim in plant_claims:
                source = claim.get("source_title", "Source not identified")
                organization = claim.get("organization", "")
                if organization:
                    source = f"{source} ({organization})"
                url = claim.get("url", "")
                source_link = f"[{source}]({url})" if url else source
                lines.append(
                    f"- **{claim.get('status') or 'status unrecorded'}** — "
                    f"{claim.get('claim_text') or 'Claim text unavailable'} "
                    f"Source: {source_link}. "
                    f"Page/section: {claim.get('page_or_section') or 'not recorded'}. "
                    f"Publication date: {claim.get('publication_date') or 'not recorded'}. "
                    f"Access date: {claim.get('access_date') or 'not recorded'}. "
                    f"Evidence type: {claim.get('evidence_type') or 'not recorded'}. "
                    f"Confidence: {claim.get('confidence') or 'not assessed'}. "
                    f"Geographic scope: "
                    f"{claim.get('geographic_applicability') or 'not recorded'}. "
                    f"Review note: {claim.get('notes') or 'No review note recorded.'}"
                )
        else:
            lines.append("- No claim-level research record is currently linked to this plant.")
        lines.append("")

    lines.extend([
        "# Educational Figure Library",
        "",
        "These are figure concepts, not reviewed teaching diagrams. Their source references",
        "are incomplete and their artwork is intentionally withheld from the encyclopedia.",
        "",
    ])
    for fig in figures:
        lines.extend([
            f"## {fig['caption']}",
            "",
            f"**Figure ID:** `{fig['figure_id']}`",
            f"**Description:** {fig['description']}",
            f"**Accessibility text:** {fig['accessibility_text']}",
            f"**Status:** {fig['approval_status']}",
            "",
        ])

    examples = [
        {
            "title": "Plan and prepare a raised vegetable bed",
            "objective": "Lay out a reachable 4 × 8 ft bed (32 sq ft) at a site suitable for the selected crops.",
            "difficulty": "Beginner; about 1–2 hours for layout, excluding delivery and construction.",
            "materials": "Tape, stakes, string, level, shovel, site map, and bed material selected for food-growing use.",
            "prerequisites": "Check site history, access to water, drainage, sun exposure, utilities, slope, and any contamination concern before excavation or filling.",
            "preparation": "Mark the actual bed footprint and paths; test reach from every side; observe sun and wet spots rather than assuming them.",
            "procedure": [
                "Stake a 4 × 8 ft rectangle and measure the inside dimensions.",
                "Confirm the center can be reached without stepping on growing soil; widen paths only to suit actual access and tools.",
                "Remove persistent weeds and loosen compacted underlying soil only when it is workable and safe to dig.",
                "Select a suitable fill based on intended crops and site conditions; use a soil test to guide nutrient amendments.",
                "Estimate geometric volume as length × width × fill depth, then confirm settling and delivery quantity with the supplier.",
                "Fill, level, water to settle, and recheck drainage and low spots before planting."
            ],
            "result": "A stable, accessible 32 sq ft bed with documented fill and no assumed nutrient or drainage diagnosis.",
            "mistakes": [
                "Making the bed too wide to reach its center.",
                "Filling over a drainage, contamination, or compaction problem without assessment.",
                "Adding fertilizer or lime without a diagnosis."
            ],
            "troubleshooting": [
                "Water pools: pause planting and investigate the bed and underlying drainage.",
                "Fill settles unevenly: top up with the same suitable material and recheck level.",
                "Access is awkward: adjust the path or bed width before installing permanent irrigation."
            ],
            "local": "Use the supplied frost dates only as approximate source anchors; site exposure and soil conditions vary within Errington.",
            "references": "OSU Extension, Raised Bed Gardening (FS 270), https://extension.oregonstate.edu/catalog/fs-270-raised-bed-gardening; BC Soil Nutrient Management, https://www2.gov.bc.ca/gov/content/industry/agriculture-seafood/agricultural-land-and-environment/soil-nutrients/management."
        },
        {
            "title": "Assess and prepare garden soil",
            "objective": "Observe a proposed bed and decide what evidence is needed before disturbing or amending its soil.",
            "difficulty": "Beginner; 30–60 minutes for inspection, plus laboratory turnaround if a test is submitted.",
            "materials": "Trowel, clean sample container, notebook, labels, and laboratory supplies if testing.",
            "prerequisites": "Know the intended growing area and crop group; follow the selected laboratory's sampling instructions.",
            "preparation": "Compare several locations after wet and dry weather; keep visibly different areas as separate observations or samples.",
            "procedure": [
                "Record standing water, crusting, compaction, construction debris, and where the surface dries first.",
                "Check a small soil handful at working depth; wait if it smears or forms a dense wet mass.",
                "Inspect a small profile for abrupt fill layers or dense pans without cutting important roots or utilities.",
                "Submit a representative sample when pH or nutrient decisions are needed.",
                "Use the report and crop-specific guidance to choose an amendment; otherwise avoid speculative inputs."
            ],
            "result": "A documented soil condition and a justified next step: wait, sample, amend conservatively, or address a physical site issue.",
            "mistakes": [
                "Working saturated soil and compacting it further.",
                "Treating a jar texture test or leaf color as a complete fertility diagnosis.",
                "Applying lime, fertilizer, manure, or concentrated amendment without evidence."
            ],
            "troubleshooting": [
                "Soil smears when squeezed: wait for it to dry to a workable condition.",
                "A sample has mixed soil types: resample distinct areas separately.",
                "Test results are unclear: ask the laboratory or qualified local advisor to interpret them for the intended crop."
            ],
            "local": "No property-specific soil condition is established by the Errington calendar; inspect each garden independently.",
            "references": "BC Soil Nutrient Management, https://www2.gov.bc.ca/gov/content/industry/agriculture-seafood/agricultural-land-and-environment/soil-nutrients/management."
        },
        {
            "title": "Start seeds indoors",
            "objective": "Sow a small, labeled batch using instructions for the identified crop and seed lot.",
            "difficulty": "Beginner; 20–40 minutes to sow, followed by routine checks.",
            "materials": "Clean draining containers, suitable seed-starting medium, labels, seeds, water, and appropriate light.",
            "prerequisites": "Check the packet or plant-specific source for sowing depth, germination temperature, light response, and whether indoor sowing is appropriate.",
            "preparation": "Clean reused containers; prepare labels before sowing; moisten the medium evenly without saturating it.",
            "procedure": [
                "Fill containers loosely and level the surface.",
                "Sow at the source-stated depth and label crop, cultivar if known, and date.",
                "Provide the stated germination conditions and keep the medium evenly moist.",
                "After emergence, provide adequate light, airflow, and room for seedlings.",
                "Thin or transplant gently; handle seedlings by a leaf rather than crushing the stem."
            ],
            "result": "Clearly identified seedlings that emerge under the selected source's conditions and remain compact and healthy.",
            "mistakes": [
                "Applying one depth or temperature to all seeds.",
                "Keeping containers waterlogged or allowing the surface to dry during germination.",
                "Using weak light that produces elongated seedlings."
            ],
            "troubleshooting": [
                "No emergence: check seed age, depth, temperature, and moisture before resowing.",
                "Seedlings stretch: improve light placement and spacing according to fixture guidance.",
                "Algae or persistent wetness: improve drainage and reduce excess water; do not abruptly dry emerging seeds."
            ],
            "local": "Indoor sowing dates in the supplied calendar are transcriptions, not independently verified plant-specific recommendations.",
            "references": "Use the seed supplier's crop-specific instructions; regional context: OSU Extension, Growing Vegetables in the Pacific Northwest Coastal Region, https://extension.oregonstate.edu/catalog/em-9695-growing-vegetables-pacific-northwest-coastal-region."
        },
        {
            "title": "Calculate plant spacing",
            "objective": "Convert a verified spacing recommendation into a measured layout without confusing row spacing and plant spacing.",
            "difficulty": "Beginner; 15–30 minutes.",
            "materials": "Tape, string, stakes, bed plan, and a source giving spacing for the identified crop or cultivar.",
            "prerequisites": "Confirm whether the source specifies plant-to-plant distance, row spacing, or both; do not substitute a generic value.",
            "preparation": "Measure the usable inside length and width, accounting for edge clearance, paths, supports, and mature canopy.",
            "procedure": [
                "Write the source's recommended plant and row distances separately.",
                "Convert bed dimensions and spacing to the same units.",
                "Estimate a grid with floor(usable length ÷ plant spacing) × floor(usable width ÷ row spacing).",
                "Mark a small test section and check that mature plants and access will fit.",
                "Revise the count for the actual cultivar and layout before planting the whole bed."
            ],
            "result": "A layout whose assumptions and source spacing are recorded; the arithmetic is not mistaken for a crop recommendation.",
            "mistakes": [
                "Using an unsupported universal 12-inch lettuce spacing.",
                "Treating mature plant spread as the same measure as row spacing.",
                "Counting to the bed edge without clearance."
            ],
            "troubleshooting": [
                "Plants overlap early: compare the source's spacing definition and cultivar size; thin or harvest only as appropriate.",
                "Rows are difficult to reach: add access before planting the remaining bed.",
                "The calculation yields too many plants: reduce count for edge clearance and mature canopy."
            ],
            "local": "No single spacing value is established for all Errington sites or cultivars.",
            "references": "Use the identified cultivar's seed packet or a crop-specific extension reference; this is a calculation method, not crop spacing advice."
        },
        {
            "title": "Transplant seedlings",
            "objective": "Move a healthy, hardened seedling into prepared soil with minimal root disturbance.",
            "difficulty": "Beginner; about 10–20 minutes per small group.",
            "materials": "Labeled seedlings, hand trowel, water, and suitable temporary protection if needed.",
            "prerequisites": "Confirm identity, species-specific planting depth, root-ball condition, soil workability, and current forecast.",
            "preparation": "Water the root ball if dry; prepare the planting position and protection before removing seedlings from containers.",
            "procedure": [
                "Make a hole that accommodates the root ball without sharply bending roots.",
                "Set the plant at the depth appropriate to its species.",
                "Backfill and firm gently so the plant is supported without compressing wet soil.",
                "Water in when appropriate for the plant and soil; label the planting.",
                "Check establishment and root-zone moisture over the following days."
            ],
            "result": "A stable transplant at species-appropriate depth with roots in contact with moist, aerated soil.",
            "mistakes": [
                "Planting every species at the same depth.",
                "Leaving large air gaps or crushing the stem while handling.",
                "Transplanting an unhardened plant into harsh sun, wind, or frost risk."
            ],
            "troubleshooting": [
                "Plant wilts: check root-ball moisture, wind, sun exposure, and planting depth before adding water.",
                "Plant rocks in the hole: firm the surrounding soil gently and support it until established.",
                "Leaves scorch: provide suitable temporary shade and reassess exposure; do not assume nutrient deficiency."
            ],
            "local": "The April 15 source anchor is approximate and is not a universal transplant date.",
            "references": "OSU Extension, Growing Vegetables in the Pacific Northwest Coastal Region, https://extension.oregonstate.edu/catalog/em-9695-growing-vegetables-pacific-northwest-coastal-region."
        },
        {
            "title": "Harden off transplants",
            "objective": "Acclimate indoor-grown plants to outdoor light, wind, and temperature without prescribing a universal schedule.",
            "difficulty": "Beginner; repeated short checks over several days, adjusted to plant and weather.",
            "materials": "Seedling tray, sheltered outdoor area, labels, and a way to bring plants back under protection.",
            "prerequisites": "Know the crop's tolerance and ensure a safe indoor or protected location is available if weather changes.",
            "preparation": "Choose mild conditions and a protected site; postpone exposure during harsh wind, damaging cold, or intense sun.",
            "procedure": [
                "Begin with brief exposure in shade or bright shelter.",
                "Inspect leaf condition and moisture before extending the next exposure.",
                "Gradually increase duration, light, and airflow only while plants tolerate the change.",
                "Return plants to protection when conditions exceed their known tolerance.",
                "Plant out only after hardening and site conditions are both suitable."
            ],
            "result": "Plants tolerate the intended outdoor location without sudden sun or wind injury.",
            "mistakes": [
                "Treating seven days as a fixed prescription for every crop and weather pattern.",
                "Leaving trays exposed to strong sun, drying wind, or unexpected cold.",
                "Assuming hardening off makes a frost-sensitive plant frost-hardy."
            ],
            "troubleshooting": [
                "Bleached or scorched leaves: return to shade and resume more gradually after recovery.",
                "Leaves wilt outdoors: check moisture and wind exposure; shorten the next session.",
                "Forecast worsens: delay planting and protect plants rather than completing a schedule by date."
            ],
            "local": "Outdoor exposure should respond to the actual garden forecast; the local frost anchors are not guarantees.",
            "references": "OSU Extension, Growing Vegetables in the Pacific Northwest Coastal Region, https://extension.oregonstate.edu/catalog/em-9695-growing-vegetables-pacific-northwest-coastal-region."
        },
        {
            "title": "Plan succession crops",
            "objective": "Spread sowing and harvest workload using crop-specific maturity and seasonal limits.",
            "difficulty": "Beginner; 20–40 minutes to plan, repeated sowing as conditions allow.",
            "materials": "Bed map, labels, seed source, calendar, and harvest notes.",
            "prerequisites": "Confirm crop identity, days-to-maturity interpretation, seasonal suitability, and whether later sowings fit local conditions.",
            "preparation": "Choose a modest bed area and define the first crop and observable condition that will free the next block.",
            "procedure": [
                "Divide the available area into labeled blocks.",
                "Read the crop-specific sowing interval and maturity guidance; do not assume a universal 14-day interval.",
                "Sow the first block and record date, conditions, and quantity.",
                "Make the next sowing only if the crop source and remaining season support it.",
                "Compare emergence and harvest timing; adjust the next year's interval from records."
            ],
            "result": "Staggered, traceable sowings sized to household use and actual bed availability.",
            "mistakes": [
                "Repeating a fixed interval without checking crop or seasonal guidance.",
                "Sowing more blocks than can be watered, harvested, or used.",
                "Planting a follow-on crop before the bed is available."
            ],
            "troubleshooting": [
                "Later sowing fails to emerge: check temperature, moisture, seed depth, and seasonal suitability.",
                "Harvests overlap: lengthen the next interval only if the crop's remaining window permits.",
                "Bed is not free: shift the sowing based on an observable harvest trigger."
            ],
            "local": "Do not infer local sowing windows from a generic calendar when the supplied record is unreviewed.",
            "references": "Use crop-specific seed-packet or extension timing; the local calendar remains a transcription requiring review."
        },
        {
            "title": "Plan crop rotation by family",
            "objective": "Record successive crops by verified botanical family to reduce repeated-family concentration where practical.",
            "difficulty": "Intermediate; about 30–60 minutes for a multi-bed map.",
            "materials": "Bed map, plant registry with verified family fields, and planting records.",
            "prerequisites": "Resolve plant identity and family first; a common name such as “roots” is not a family.",
            "preparation": "Label beds and list crop families; mark perennials and crops that cannot be moved annually.",
            "procedure": [
                "Assign each identified annual crop to its verified family.",
                "Keep crops from the same family together only where useful for planning, not as a biological guarantee.",
                "Map family locations for each year and move susceptible annual groups when space permits.",
                "Record exceptions, perennial crops, and the reason a crop remained in place.",
                "Continue scouting and managing pests; rotation alone does not diagnose or prevent every problem."
            ],
            "result": "A rotation record based on botanical families rather than edible portions, with limitations visible.",
            "mistakes": [
                "Treating all root crops as one family.",
                "Assuming family rotation guarantees pest or disease control.",
                "Assigning a family from an ambiguous common name."
            ],
            "troubleshooting": [
                "Family is uncertain: leave it unresolved and verify taxonomy before assigning a rotation group.",
                "Too few beds: rotate only where practical and combine with other prevention strategies.",
                "A problem recurs despite rotation: identify the causal organism and site conditions rather than extending rotation blindly."
            ],
            "local": "The registry's recorded families are not all independently verified; confirm a taxon before using it as a rotation fact.",
            "references": "Taxonomic family claims require a current botanical source; no family-level control outcome is guaranteed here."
        },
        {
            "title": "Support climbing plants",
            "objective": "Install a stable support before climbing growth becomes difficult to handle.",
            "difficulty": "Beginner; 30–60 minutes depending on support and site.",
            "materials": "Support stakes or frame, suitable netting or trellis, ties, mallet, and gloves.",
            "prerequisites": "Identify the plant's mature height, climbing method, expected crop load, and the support's wind and soil anchorage needs.",
            "preparation": "Position support to preserve access and avoid shading neighboring plants; install anchors before sowing or transplanting.",
            "procedure": [
                "Choose a support rated for the mature plant and fruit or pod load.",
                "Secure posts or frame in stable ground, checking for overhead or buried hazards.",
                "Attach mesh or crossbars without sharp exposed ends.",
                "Guide young stems loosely; do not constrict expanding growth.",
                "Inspect ties and anchors after wind and as plant weight increases."
            ],
            "result": "A stable, accessible plant with room for growth and no constricting ties.",
            "mistakes": [
                "Choosing a light support for a heavy mature crop.",
                "Installing stakes through established roots.",
                "Tying stems tightly or blocking airflow."
            ],
            "troubleshooting": [
                "Support leans: unload if safe and reinforce anchors before adding more plant weight.",
                "Stem is constricted: replace the tie with a loose, soft loop.",
                "Plant will not climb: verify its growth habit; some plants require tying rather than twining."
            ],
            "local": "Wind exposure varies by garden; inspect supports after local wind events.",
            "references": "Select support dimensions and anchoring for the identified plant and site; no universal weight rating is assumed."
        },
        {
            "title": "Prune a shrub or perennial safely",
            "objective": "Make only justified, well-placed cuts after identifying the plant and its flowering or regrowth habit.",
            "difficulty": "Intermediate; 20–60 minutes depending on plant size.",
            "materials": "Clean, sharp pruners or saw appropriate to branch diameter, gloves, and plant label.",
            "prerequisites": "Identify the species or cultivar and consult its recommended pruning season, flowering wood, and local safety guidance.",
            "preparation": "Observe the whole plant, distinguish dead from live wood, and identify branch unions before cutting.",
            "procedure": [
                "Remove only clearly dead, damaged, or crossing material when the cut is safe and appropriate.",
                "Use a clean tool suited to the branch; avoid tearing or leaving a long stub.",
                "Keep cuts outside the branch collar where present; do not flush-cut the trunk.",
                "Stop before major renovation if species-specific timing or response is unknown.",
                "Clean tools between plants when disease spread is a concern."
            ],
            "result": "Limited, deliberate cuts that preserve the plant's structure and do not claim a species-specific pruning schedule.",
            "mistakes": [
                "Pruning a spring-flowering plant at an unverified time and removing flower buds.",
                "Making indiscriminate heavy cuts to an unidentified shrub.",
                "Cutting flush to the trunk or leaving ragged tears."
            ],
            "troubleshooting": [
                "A cut reveals discolored tissue: stop and seek a diagnosis before removing more.",
                "Plant fails to flower: review species, pruning date, light, and prior year's growth.",
                "Branch is too large for hand pruners: use an appropriate saw or consult a qualified arborist."
            ],
            "local": "The calendar's grouped pruning entries do not establish one timing for all listed tree or shrub species.",
            "references": "Species-specific pruning guidance is required before timing or renovation cuts."
        },
        {
            "title": "Divide a perennial",
            "objective": "Assess whether an identified perennial can be divided and re-establish viable divisions.",
            "difficulty": "Intermediate; 30–90 minutes depending on root mass.",
            "materials": "Garden fork, clean sharp knife or spade, labels, water, and prepared planting area.",
            "prerequisites": "Identify species, confirm suitable division season and growth form, and check soil moisture and forecast.",
            "preparation": "Prepare the new site before lifting; water the plant if soil is dry and mark the original planting depth.",
            "procedure": [
                "Lift only the amount of root system that can be replanted promptly.",
                "Separate at natural crowns, rhizomes, or rooted sections as appropriate to the species.",
                "Retain viable roots and growing points on each division.",
                "Replant at the species-appropriate depth, water as appropriate, and label.",
                "Monitor establishment and protect from conditions beyond the plant's tolerance."
            ],
            "result": "Labeled divisions with viable growing points and minimal time exposed above ground.",
            "mistakes": [
                "Applying one calendar window to all perennials.",
                "Making divisions without roots or growing points.",
                "Leaving lifted material exposed until roots dry."
            ],
            "troubleshooting": [
                "Division wilts: check root contact and moisture; reduce stress without waterlogging.",
                "No growth returns: verify viability, depth, and whether the species is dormant.",
                "Clump resists separation: stop rather than forcing an unknown root structure."
            ],
            "local": "The supplied ornamental calendar has division cues, but they are transcriptions, not universal species advice.",
            "references": "Use an identified plant's propagation reference for timing and division form."
        },
        {
            "title": "Plan a berry planting",
            "objective": "Prepare a site plan for one identified berry species before purchasing or planting stock.",
            "difficulty": "Intermediate; 1–2 hours for site assessment and layout.",
            "materials": "Site map, tape, soil test supplies if needed, labels, and species-specific nursery guidance.",
            "prerequisites": "Choose the berry species and cultivar; verify mature size, pollination requirements, light, soil, drainage, spacing, and pruning needs.",
            "preparation": "Assess sunlight, water access, drainage, access for harvest, and whether netting or support is needed.",
            "procedure": [
                "Record site measurements and existing constraints.",
                "Compare the site's soil and exposure with a reliable source for the selected berry.",
                "Check cultivar pollination and mature-size information before setting row spacing.",
                "Prepare supports or protection before planting if the verified plan requires them.",
                "Plant at the nursery- or species-specified depth and label each plant."
            ],
            "result": "A species-specific planting plan; this generic example intentionally supplies no unsupported berry spacing or pruning date.",
            "mistakes": [
                "Treating strawberries, cane berries, currants, and blueberries as having one soil or pruning requirement.",
                "Planting before checking drainage or mature size.",
                "Applying fertilizer or mulch against crowns without plant-specific guidance."
            ],
            "troubleshooting": [
                "Poor establishment: review planting depth, root condition, moisture, and site match.",
                "Little fruit: verify age, cultivar, pollination needs, light, and pruning history.",
                "Crowded row: compare mature size with the plan before moving established plants."
            ],
            "local": "Local timing must be checked for the chosen species; grouped berry entries in the source calendar are not interchangeable.",
            "references": "Use species- and cultivar-specific extension or nursery guidance; no single berry profile is implied."
        },
        {
            "title": "Measure irrigation delivery",
            "objective": "Check whether a watering system delivers water evenly and wets the intended root zone.",
            "difficulty": "Beginner; 30–60 minutes.",
            "materials": "Catch cups, ruler, timer, notebook, and trowel or soil probe.",
            "prerequisites": "Know which zone is being tested; do not run electrical or pressurized equipment outside its instructions.",
            "preparation": "Place catch cups at the beginning, middle, and end of the irrigation line; note recent rain and soil condition.",
            "procedure": [
                "Run the system for a recorded interval.",
                "Compare collected amounts to locate uneven output; clear or repair emitters according to the product instructions.",
                "Check soil moisture below the surface in several parts of the bed.",
                "Adjust duration or emitter layout in a small step, then repeat the measurement.",
                "Record the setting and repeat checks as plants and weather change."
            ],
            "result": "A measured distribution and root-zone check rather than a fixed daily schedule.",
            "mistakes": [
                "Assuming all emitters deliver the same amount.",
                "Judging moisture only from the soil surface.",
                "Using a water-volume conversion as a universal irrigation prescription."
            ],
            "troubleshooting": [
                "One cup collects much less: check blockage, pressure, or line length.",
                "Runoff begins: reduce application rate or split the run, then recheck infiltration.",
                "Soil is wet but plants wilt: investigate roots, drainage, and plant stress rather than adding water automatically."
            ],
            "local": "Summer dry-spell descriptions are source-reported; respond to measured soil and current conditions.",
            "references": "OSU Extension, Growing Vegetables in the Pacific Northwest Coastal Region, https://extension.oregonstate.edu/catalog/em-9695-growing-vegetables-pacific-northwest-coastal-region."
        },
        {
            "title": "Diagnose a plant problem",
            "objective": "Narrow possible causes before treatment by recording symptoms, distribution, and site conditions.",
            "difficulty": "Beginner; 15–45 minutes for initial checks.",
            "materials": "Notebook, phone or camera, hand lens, plant label, and clean sample bag if a diagnostic service requests it.",
            "prerequisites": "Do not apply a pesticide or fertilizer until a likely cause and appropriate action are supported.",
            "preparation": "Photograph the whole plant, affected area, and close details; note date and recent changes.",
            "procedure": [
                "Describe the symptom without naming a pest or disease.",
                "Map whether one plant, one species, one bed edge, or many plants are affected.",
                "Check leaf surfaces, stems, root-zone moisture, drainage, and recent weather or management changes.",
                "Compare several diagnostic features with a reliable source or ask a qualified diagnostic service.",
                "Choose the least disruptive justified action and record the result for follow-up."
            ],
            "result": "A documented differential and next check, not an unsupported diagnosis from one symptom.",
            "mistakes": [
                "Treating every yellow leaf as a nutrient deficiency.",
                "Confusing waterlogged roots with drought.",
                "Spraying before identifying a target organism."
            ],
            "troubleshooting": [
                "Symptoms spread quickly: isolate affected material where safe and seek timely diagnostic help.",
                "No pest is visible: review water, roots, weather, exposure, and recent changes.",
                "First intervention fails: revisit the diagnosis rather than escalating product use."
            ],
            "local": "A verified Errington-specific pest and disease matrix is not yet available.",
            "references": "Use current BC plant diagnostic or extension guidance appropriate to the identified plant and symptom."
        },
        {
            "title": "Protect a plant from frost",
            "objective": "Reduce exposure during a forecast cold event without treating a calendar anchor as a guarantee.",
            "difficulty": "Beginner; 10–20 minutes before the event, plus checks during warming.",
            "materials": "Suitable frost cloth or cover, hoops if needed, clips or weights, and forecast source.",
            "prerequisites": "Identify plant tolerance and cover instructions; have protection sized to the bed and wind exposure.",
            "preparation": "Check the forecast, locate supports, and plan how to vent or remove cover as conditions change.",
            "procedure": [
                "Install hoops or supports so the cover does not crush foliage.",
                "Drape and secure the cover before the event, closing gaps while avoiding damage to the plant.",
                "Use plastic only with an appropriate support and follow its instructions; do not leave plants sealed in sun.",
                "Check conditions and remove or vent the cover as temperatures rise.",
                "Inspect damage after the event before deciding whether pruning or replacement is needed."
            ],
            "result": "A secured, temporary protection setup with an active removal/venting plan.",
            "mistakes": [
                "Assuming April 15 or October 15 guarantees frost-free conditions.",
                "Allowing plastic to touch foliage or overheat plants.",
                "Leaving an unsecured cover in wind."
            ],
            "troubleshooting": [
                "Cover lifts: secure edges and add support without crushing plants.",
                "Plants overheat: vent or remove cover promptly when safe.",
                "Injury appears despite cover: record forecast and site conditions; cover performance varies."
            ],
            "local": "The supplied frost dates are approximate anchors; check current forecast and garden microclimate.",
            "references": "Follow the cover manufacturer's instructions and plant-specific cold-tolerance source."
        },
        {
            "title": "Harvest and preserve produce safely",
            "objective": "Prepare a small, identified harvest for one preservation method using a current tested procedure.",
            "difficulty": "Beginner for freezing; food-safety procedures vary by method.",
            "materials": "Clean basket, potable water, clean utensils, labeled containers, and tested recipe or preservation instructions.",
            "prerequisites": "Identify the crop and preservation method; use tested, current directions for blanching, freezing, drying, fermenting, or canning.",
            "preparation": "Check maturity cues for the crop, clean work surfaces, prepare containers, and reserve time to process promptly.",
            "procedure": [
                "Harvest only sound, correctly identified produce at the stage specified by a reliable crop source.",
                "Sort and wash as directed for the chosen preservation method.",
                "Follow the current tested method exactly, including preparation, processing, and storage steps.",
                "Label the food with contents and date; store under the method's stated conditions.",
                "Discard food when safety is uncertain; do not taste it to decide whether it is safe."
            ],
            "result": "Labeled produce processed under a tested procedure; the example does not invent times, temperatures, or canning recipes.",
            "mistakes": [
                "Using an untested canning recipe or changing proportions and processing time.",
                "Freezing without following the crop's quality and preparation guidance.",
                "Assuming appearance or smell proves food safety."
            ],
            "troubleshooting": [
                "A jar seal fails: follow current food-safety guidance for the specific product and elapsed time; do not assume it is shelf stable.",
                "Freezer containers are unlabeled: identify contents only if certain; otherwise do not guess.",
                "Processing instructions are missing: pause and obtain a tested procedure before proceeding."
            ],
            "local": "Harvest dates and maturity depend on the crop and actual season; the supplied calendar is not a food-safety authority.",
            "references": "National Center for Home Food Preservation, https://nchfp.uga.edu/; follow its current tested recipes and guidance."
        },
        {
            "title": "Plan a pollinator-supportive garden area",
            "objective": "Plan habitat resources for identified local pollinators without labeling unverified plants as native or beneficial.",
            "difficulty": "Intermediate; 1–2 hours for a first site and plant list.",
            "materials": "Site map, locally appropriate plant references, labels, water-source plan, and habitat observation notebook.",
            "prerequisites": "Verify candidate plant identities and regional status; check invasive-plant guidance and site conditions.",
            "preparation": "Map sun, soil moisture, nesting habitat, existing vegetation, and pesticide exposure.",
            "procedure": [
                "Select a small area and list habitat needs to investigate: flowering resources, host plants, shelter, nesting substrate, and water.",
                "Use authoritative regional sources to select suitable plants and confirm names before purchase.",
                "Plan a varied sequence of bloom only where supported by regional plant references; do not infer Errington dates from a wider ecoregion.",
                "Retain suitable undisturbed habitat where safe and compatible with the garden.",
                "Observe visitors and plant performance over seasons; revise the plan from evidence."
            ],
            "result": "A site-specific habitat plan with verified plant identities and explicit unknowns.",
            "mistakes": [
                "Calling every ornamental a native plant or pollinator resource.",
                "Removing all nesting habitat or applying pesticides prophylactically.",
                "Treating a regional bloom table as an Errington-specific calendar."
            ],
            "troubleshooting": [
                "Few visits observed: check bloom availability, weather, observation timing, and plant establishment before assuming failure.",
                "Plant identity uncertain: do not use it as a native reference until verified.",
                "Water source attracts pests or becomes stagnant: change or remove it using appropriate local guidance."
            ],
            "local": "The Eastern Vancouver Island pollinator guide cited in the draft is not available for verification; the plant list remains pending.",
            "references": "Verify plant identity and native status through E-Flora BC and regional ecological sources before publication."
        },
        {
            "title": "Set up a composting trial",
            "objective": "Start a small, observable compost batch using suitable materials while avoiding unsupported exact ratios.",
            "difficulty": "Beginner; 30–60 minutes to set up, with periodic monitoring.",
            "materials": "Ventilated bin or contained pile, suitable plant-based materials, fork, water source, and thermometer if available.",
            "prerequisites": "Check local wildlife, nuisance, and municipal guidance; exclude materials inappropriate for the chosen system.",
            "preparation": "Choose a drained, accessible location; gather a mix of dry structural material and moist fresh plant material.",
            "procedure": [
                "Add a loose mixture of dry and fresh suitable material; avoid packing it tightly.",
                "Moisten evenly so the material is damp, not saturated; do not rely on a fixed ratio unless a chosen source specifies one.",
                "Check odor, moisture, and airflow periodically; turn or loosen if the system is compacted and the method calls for aeration.",
                "Add dry material if overly wet, or water gradually if too dry.",
                "Use finished material only when it is mature for the intended application and its source is known."
            ],
            "result": "A monitored batch with documented inputs and an adjustment path, not a guaranteed composting timeline.",
            "mistakes": [
                "Adding unsuitable food or diseased material without checking local and system guidance.",
                "Making the pile waterlogged or tightly compacted.",
                "Assuming color alone proves maturity."
            ],
            "troubleshooting": [
                "Strong sour or rotten odor: check excess moisture and compaction; add suitable dry structure and aerate if appropriate.",
                "Pile is dry and inactive: add water gradually and check material mix.",
                "Wildlife accesses the bin: secure it and revise inputs according to local guidance."
            ],
            "local": "Choose a secure location that does not create runoff or wildlife conflict on the property.",
            "references": "Use current provincial or municipal composting guidance for accepted materials and wildlife considerations."
        },
    ]

    lines.extend([
        "# Practical worked examples",
        "",
        "These examples demonstrate procedures; they do not supply unsupported plant-specific timing, spacing, or treatment recommendations.",
        "Each example distinguishes the task from its expected outcome and includes actionable troubleshooting.",
        "",
    ])
    for index, example in enumerate(examples, 1):
        lines.extend([
            f"## Example {index:02d}: {example['title']}",
            "",
            f"**Objective:** {example['objective']}",
            f"**Difficulty and time:** {example['difficulty']}",
            f"**Materials:** {example['materials']}",
            f"**Prerequisites:** {example['prerequisites']}",
            f"**Preparation:** {example['preparation']}",
            "",
            "**Procedure**",
            "",
        ])
        lines.extend(f"{step_index}. {step}" for step_index, step in enumerate(example["procedure"], 1))
        lines.extend([
            "",
            f"**Expected result:** {example['result']}",
            "",
            "**Common mistakes**",
            "",
        ])
        lines.extend(f"- {mistake}" for mistake in example["mistakes"])
        lines.extend(["", "**Troubleshooting**", ""])
        lines.extend(f"- {item}" for item in example["troubleshooting"])
        lines.extend([
            "",
            f"**Local considerations:** {example['local']}",
            f"**References:** {example['references']}",
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
