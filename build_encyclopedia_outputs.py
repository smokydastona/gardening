from __future__ import annotations

import csv
from collections import defaultdict
from pathlib import Path
import re


MONTH_ORDER = [
    "JANUARY",
    "FEBRUARY",
    "MARCH",
    "APRIL",
    "MAY",
    "JUNE",
    "JULY",
    "AUGUST",
    "SEPTEMBER",
    "OCTOBER",
    "NOVEMBER",
    "DECEMBER",
]

ILLUSTRATION_MD = "ERRINGTON_ILLUSTRATION_BRIEFS_AND_PROMPTS.md"
ILLUSTRATION_CSV = "errington_illustration_briefs.csv"
ILLUSTRATION_ASSET_DIR = "plant_illustrations"
ILLUSTRATION_MANIFEST_CSV = "illustration_asset_manifest.csv"
ILLUSTRATION_MANIFEST_MD = "illustration_asset_manifest.md"
ILLUSTRATION_MISSING_TXT = "missing_illustrations.txt"
ILLUSTRATION_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")

BRASSICA_KEYS = {"ARUGULA", "BROCCOLI", "BRUSSELS_SPROUTS", "CABBAGE", "CAULIFLOWER", "KOHLRABI", "AUBRETIA", "IBERIS", "WALLFLOWER"}
ROOT_UMBEL_KEYS = {"CARROTS", "PARSNIPS", "DILL", "FENNEL", "PARSLEY", "CHERVIL", "CILANTRO", "CELERY", "CELERIAC", "AMMI_MAJUS", "ORLAYA"}
ROOT_STORAGE_KEYS = {"BEETS", "RADISH", "TURNIPS", "RUTABAGA", "CELERIAC", "POTATOES", "POTATO", "SWEET_POTATO", "SWEET_POTATOES"}
ALLIUM_KEYS = {"GARLIC", "LEEKS", "CHIVES", "ALLIUM", "HYACINTH", "HYACINTHS", "DAFFODIL", "DAFFODILS", "TULIP", "TULIPS", "MUSCARI"}
SOLANUM_KEYS = {"BELL_PEPPER", "PEPPER", "PEPPERS", "EGGPLANT", "TOMATO", "TOMATOES", "POTATO", "POTATOES", "PETUNIAS", "NICOTIANA"}
CUCURBIT_KEYS = {"CANTALOUPE", "MELONS", "CUCUMBER", "CUCUMBERS", "SUMMER_SQUASH", "WINTER_SQUASH", "ZUCCHINI", "PUMPKIN", "PUMPKINS"}
LEGUME_KEYS = {"BEANS", "PEAS", "SWEET_PEA", "LUPINE"}
LEAFY_KEYS = {"LETTUCE", "SPINACH", "SWISS_CHARD", "MACHE", "CLAYTONIA"}
PERENNIAL_EDIBLE_KEYS = {"ASPARAGUS", "RHUBARB", "GLOBE_ARTICHOKE"}
HERB_WOODY_KEYS = {"ROSEMARY", "THYME", "OREGANO", "LAVENDER", "SALVIA_NEMOROSA"}
HERB_SOFT_KEYS = {"BASIL", "DILL", "PARSLEY", "CHIVES", "CHERVIL", "CILANTRO", "FENNEL"}
DAISY_KEYS = {"MARIGOLD", "ZINNIA", "COSMOS", "SUNFLOWER", "CALENDULA", "RUDBECKIA", "ECHINACEA", "GAILLARDIA", "ASTER", "ASTERS", "SCABIOSA", "STRAWFLOWER", "CELOSIA", "DAHLIA"}
SPIKE_KEYS = {"DELPHINIUM", "SNAPDRAGONS", "ANTIRRHINUM", "STOCKS", "STATICE", "LOBELIA", "LARKSPUR", "FOXGLOVE", "GLADIOLUS"}
BULB_KEYS = {"TULIP", "TULIPS", "DAFFODIL", "DAFFODILS", "HYACINTH", "HYACINTHS", "MUSCARI", "ALLIUM", "CROCUS", "CAMASSIA", "ANEMONE", "GLADIOLUS"}
FOLIAGE_PERENNIAL_KEYS = {"HOSTAS", "HOSTA", "DAYLILY", "DAYLILIES", "HEUCHERA", "ASTILBE", "SEDUM", "FERNS", "SWORD_FERN", "ORNAMENTAL_GRASSES"}
VINE_KEYS = {"WISTERIA", "CLEMATIS_GROUP_3", "CLEMATIS_MONTANA", "HONEYSUCKLE", "MORNING_GLORY", "SWEET_PEA", "GRAPES", "GRAPE"}
TREE_FRUIT_KEYS = {"APPLE", "PEAR", "PLUM", "CHERRY"}
BERRY_KEYS = {"STRAWBERRIES", "STRAWBERRY", "RASPBERRIES", "RASPBERRY", "BLUEBERRIES", "BLUEBERRY", "CURRANTS", "CURRANT", "GOOSEBERRIES", "GOOSEBERRY"}
WOODLAND_NATIVE_KEYS = {"TRILLIUM", "BLEEDING_HEART", "CAMAS", "OSOBERRY", "RED_FLOWERING_CURRANT", "GARRY_OAK"}


def normalize_key(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", text.upper()).strip("_")


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError(f"No rows available to write to {path.name}.")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def months_summary(row: dict[str, str]) -> str:
    return row["calendar_months"].replace("; ", ", ") if row.get("calendar_months") else "Pending direct local timing match"


def source_summary(row: dict[str, str]) -> str:
    pieces = [
        row.get("source_scope", "").replace("-", " "),
        row.get("calendar_match_status", ""),
    ]
    return ", ".join(piece for piece in pieces if piece)


def preferred_illustration_filename(display_name: str) -> str:
    return f"{normalize_key(display_name)}.png"


def load_existing_illustration_assets(illustrations_dir: Path) -> dict[str, Path]:
    if not illustrations_dir.exists():
        return {}

    assets: dict[str, Path] = {}
    for path in illustrations_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in ILLUSTRATION_EXTENSIONS:
            continue
        key = normalize_key(path.stem)
        if key and key not in assets:
            assets[key] = path
    return assets


def profile_for_row(row: dict[str, str]) -> dict[str, str | list[str]]:
    key = normalize_key(row["display_name"])
    category = row["category"]
    subcategory = row.get("subcategory", "")

    profile = {
        "habit": "show the mature plant in full habit with one enlarged detail panel",
        "root_system": "show the root flare and fine feeder roots with the soil line clearly indicated",
        "leaf_arrangement": "depict the true leaf arrangement and mature leaf outline in a structure-first view",
        "flower_structure": "include the characteristic flower structure or inflorescence in a labeled close-up",
        "fruit_seed_structure": "include fruit, pod, or seed structure when seasonally relevant",
        "storage_organ": "show storage tissue only if the species uses a bulb, corm, tuber, rhizome, or swollen root",
        "callouts": ["crown", "stem", "true leaves", "flower detail", "root system"],
    }

    if key in BRASSICA_KEYS:
        profile.update(
            habit="show a cool-season brassica in full habit with dense foliage mass and any edible head, stem, or bolting stalk visible",
            root_system="show a compact crown with branching feeder roots beneath the soil line",
            leaf_arrangement="depict basal to alternate leaves with lobing, veining, and waxy texture clearly described",
            flower_structure="include a close-up of four-petaled cross-shaped flowers carried in a loose raceme",
            fruit_seed_structure="include narrow siliques or seed pods as the reproductive detail",
            storage_organ="note that there is no separate storage organ unless the stem itself is swollen, as in kohlrabi",
            callouts=["crown", "outer leaves", "inner edible portion", "flower raceme", "seed pod", "feeder roots"],
        )
    elif key in ROOT_UMBEL_KEYS:
        profile.update(
            habit="show the entire plant at usable stage with foliage canopy and the edible or diagnostic crown-to-root transition visible",
            root_system="show a tapered taproot or fibrous crown root system with secondary feeder roots",
            leaf_arrangement="depict finely divided, compound, or strongly cut foliage from both side and top views",
            flower_structure="include a compound umbel or umbel-like bloom structure in a separate labeled detail",
            fruit_seed_structure="include the dry seed or schizocarp form used for identification",
            storage_organ="show the swollen taproot only when the edible organ is the crop focus",
            callouts=["crown", "petiole", "leaf division", "umbel", "seed structure", "taproot"],
        )
    elif key in ROOT_STORAGE_KEYS:
        profile.update(
            habit="show the plant in harvest-ready habit with the edible underground portion fully exposed in section view",
            root_system="show the swollen storage root or tuber with feeder roots and crown attachment",
            leaf_arrangement="depict the foliage rosette or stem leaves that identify the crop before lifting",
            flower_structure="include the flower detail only as a secondary inset when it aids identification",
            fruit_seed_structure="show seed structure only if it is a practical recognition feature",
            storage_organ="make the enlarged storage organ the dominant lower-half feature of the plate",
            callouts=["crown", "storage organ", "shoulder", "feeder roots", "leaf blade", "petiole"],
        )
    elif key in ALLIUM_KEYS:
        profile.update(
            habit="show the upright tufted or bulb-forming plant in full habit with foliage, neck, and underground organ visible",
            root_system="show a basal plate with roots emerging from the bulb or clump base",
            leaf_arrangement="depict strap-like, hollow, or flattened leaves arising from the base",
            flower_structure="include a spherical or clustered inflorescence detail where flowering is characteristic",
            fruit_seed_structure="include seed capsules only when they help distinguish the plant's reproductive stage",
            storage_organ="show bulbs, cloves, or layered storage tissue clearly in cross-section when relevant",
            callouts=["bulb or clove", "basal plate", "leaf sheath", "scape", "flower cluster", "roots"],
        )
    elif key in SOLANUM_KEYS:
        profile.update(
            habit="show the branching warm-season plant in full habit with foliage, flower cluster, and mature fruit or tuber detail",
            root_system="show a fibrous root system with the main stem base and branching laterals",
            leaf_arrangement="depict alternate leaves with mature blade shape, venation, and surface texture",
            flower_structure="include the star-shaped or fused-petal flower with visible reproductive parts",
            fruit_seed_structure="make the fruit cross-section or mature harvested organ a dedicated diagnostic panel",
            storage_organ="show tubers only when the crop forms underground storage, otherwise state that no separate storage organ is present",
            callouts=["main stem", "alternate leaf", "flower", "fruit or tuber", "calyx", "root system"],
        )
    elif key in CUCURBIT_KEYS:
        profile.update(
            habit="show the sprawling or trained vine with tendrils, large leaves, one flower, and one mature fruit visible at the same scale",
            root_system="show a shallow but spreading root system emerging from the crown",
            leaf_arrangement="depict alternate broad leaves with lobing and petiole attachment clearly labeled",
            flower_structure="include the large trumpet-like flower with male and female bloom distinctions if useful",
            fruit_seed_structure="show the mature fruit and a cut section with seed cavity detail",
            storage_organ="note that the crop does not rely on a separate storage organ beyond the fruit itself",
            callouts=["crown", "vine", "tendril", "leaf blade", "flower", "fruit cross-section"],
        )
    elif key in LEGUME_KEYS:
        profile.update(
            habit="show the plant in upright bush or climbing habit with foliage, flower, and pod development across one plate",
            root_system="show the main root system with fine feeder roots and, where appropriate, nodulated root detail",
            leaf_arrangement="depict compound leaves and leaflet arrangement clearly from side and face views",
            flower_structure="include a papilionaceous flower close-up with banner, wings, and keel labeled",
            fruit_seed_structure="show immature and mature pods with seed arrangement visible",
            storage_organ="note that there is no separate storage organ beyond the seed-bearing pod",
            callouts=["stem", "leaflet", "tendril or support point", "flower", "pod", "root nodules"],
        )
    elif key in LEAFY_KEYS:
        profile.update(
            habit="show the plant at harvest-ready leafy stage with a strong emphasis on usable foliage mass",
            root_system="show the shallow root plate or fibrous roots beneath the crown",
            leaf_arrangement="depict rosette or stem-borne leaves with leaf margin, midrib, and petiole structure clearly separated",
            flower_structure="include flowering structure only as a secondary bolt-stage inset when useful",
            fruit_seed_structure="include seed heads only if they are distinctive and aid identification",
            storage_organ="note that no separate storage organ is present; the edible portion is leaf or petiole tissue",
            callouts=["crown", "outer leaf", "inner leaf", "petiole", "midrib", "roots"],
        )
    elif key in PERENNIAL_EDIBLE_KEYS:
        profile.update(
            habit="show the perennial crop in mature clump habit with the harvestable organ highlighted on the same plate",
            root_system="show the long-lived crown, rhizome, or storage root system in a clear sectional view",
            leaf_arrangement="depict the mature foliage arrangement that identifies the plant between harvest periods",
            flower_structure="include the flower or flowering stem as a secondary detail when it is diagnostically useful",
            fruit_seed_structure="show seed detail only if it is relevant to identification or propagation",
            storage_organ="make the crown, rhizome, or perennial storage organ a prominent labeled feature",
            callouts=["crown", "emerging shoot", "mature foliage", "storage organ", "flower stalk", "roots"],
        )
    elif key in HERB_WOODY_KEYS or key in HERB_SOFT_KEYS or category == "herb":
        profile.update(
            habit="show the full herb in harvest stage with repeated cutting points and aromatic foliage emphasized",
            root_system="show the root crown and branching feeder roots appropriate to a repeatedly harvested herb",
            leaf_arrangement="depict the characteristic leaf arrangement and leaf edge details that distinguish the herb at a glance",
            flower_structure="include a close-up of the flowering spike, umbel, or cluster used for recognition",
            fruit_seed_structure="show seed structure when it is a common propagation or culinary feature",
            storage_organ="note that most herbs on this list do not use a major storage organ beyond crown tissue",
            callouts=["cutting point", "leaf arrangement", "flowering stem", "new shoot", "root crown"],
        )
    elif key in DAISY_KEYS:
        profile.update(
            habit="show the flowering ornamental in full bloom habit with one stem profile and one face-on flower view",
            root_system="show the crown and supporting roots beneath the stem base or clump",
            leaf_arrangement="depict the basal or alternate foliage arrangement with clear blade and petiole shape",
            flower_structure="make the composite flower head the primary detail, including ray and disc florets",
            fruit_seed_structure="show spent seed head or achene structure where it is part of the plant's practical use",
            storage_organ="show any tuber or fleshy base only when it is central to overwintering or division",
            callouts=["flower head", "ray florets", "disc florets", "stem", "leaf", "crown"],
        )
    elif key in SPIKE_KEYS:
        profile.update(
            habit="show the plant in vertical flowering habit with an emphasis on stem posture and bloom sequence",
            root_system="show the root crown and anchoring roots that support the flowering spike",
            leaf_arrangement="depict the lower foliage and its progression up the stem",
            flower_structure="make the spike or raceme the main detail, with individual florets drawn large enough for label callouts",
            fruit_seed_structure="include the developing capsule or seed head when it is useful for recognition or saving seed",
            storage_organ="show corm or tuber detail only when it is central to the plant's life cycle",
            callouts=["flower spike", "individual floret", "bud sequence", "stem", "leaf base", "roots"],
        )
    elif key in BULB_KEYS:
        profile.update(
            habit="show the flowering bulb or corm as a complete plant with the underground organ exposed beside the bloom",
            root_system="show the basal plate and roots emerging from the bulb, corm, or tunicate structure",
            leaf_arrangement="depict strap-like or sheath-forming leaves from base to tip",
            flower_structure="include the bloom in profile and face view with perianth or floral tube detail",
            fruit_seed_structure="show the seed capsule only as a supporting inset if it aids recognition",
            storage_organ="make the bulb, corm, or tunic cross-section a required lower-plate panel",
            callouts=["storage organ", "basal plate", "leaf blade", "flower profile", "flower face", "roots"],
        )
    elif key in FOLIAGE_PERENNIAL_KEYS or category == "ornamental":
        profile.update(
            habit="show the clump-forming ornamental in mature habit with foliage architecture as the primary identifying feature",
            root_system="show the crown, rhizome, clumping base, or fibrous roots in a division-ready view",
            leaf_arrangement="depict the rosette, fan, mound, or arching foliage arrangement with accurate leaf silhouette",
            flower_structure="include the flower stem or bloom only if the species is regularly grown for floral display",
            fruit_seed_structure="show seed heads only when they contribute to winter interest or identification",
            storage_organ="show rhizome, crown division points, or fleshy roots when these matter for maintenance",
            callouts=["clump base", "leaf blade", "division point", "flower stem", "crown", "roots"],
        )
    elif key in VINE_KEYS or category == "vine":
        profile.update(
            habit="show the climbing plant with one training support, the twining or clinging habit, and one flowering or fruiting stem",
            root_system="show the anchored root system at the base of the trained stem",
            leaf_arrangement="depict opposite, alternate, or compound leaves clearly along the climbing stem",
            flower_structure="include the characteristic flowering form in a magnified inset suited to identification",
            fruit_seed_structure="include pods, hips, berries, or seed heads where they are part of the plant's seasonal identity",
            storage_organ="note that no separate storage organ is present unless the species forms a perennial crown or rhizome",
            callouts=["support", "climbing stem", "leaf node", "flower", "fruit or pod", "root base"],
        )
    elif key in TREE_FRUIT_KEYS or key in BERRY_KEYS or category == "fruit":
        profile.update(
            habit="show the orchard tree, cane fruit, or berry shrub in productive habit with one branch or cane bearing bloom and fruit",
            root_system="show the woody crown or root flare with fibrous feeder roots appropriate to a permanent planting",
            leaf_arrangement="depict the mature leaf arrangement, margins, and attachment points that identify the plant outside fruiting season",
            flower_structure="include blossom detail large enough to show petals, reproductive parts, and cluster arrangement",
            fruit_seed_structure="make the ripe fruit and a cut section or cluster detail a core panel of the plate",
            storage_organ="note that the plant relies on a perennial woody framework rather than a discrete storage organ",
            callouts=["spur or cane", "leaf", "blossom", "fruit", "bud", "root flare"],
        )
    elif category == "shrub-tree" or key in WOODLAND_NATIVE_KEYS or category == "native":
        profile.update(
            habit="show the shrub, small tree, or native perennial in mature field-guide habit with branch architecture clearly separated",
            root_system="show the woody crown, rhizome, or anchoring root system that supports long-term establishment",
            leaf_arrangement="depict the leaf arrangement and margins in an uncluttered diagnostic view",
            flower_structure="include the bloom form or inflorescence that anchors recognition at flowering time",
            fruit_seed_structure="include berries, capsules, nuts, or seed clusters where they are a defining seasonal feature",
            storage_organ="show any rhizome or woody crown only when it affects division, coppice, or habitat value",
            callouts=["branch", "bud", "leaf arrangement", "flower cluster", "fruit or seed", "root crown"],
        )

    if subcategory == "annual" and "roots" not in " ".join(profile["callouts"]):
        profile["callouts"] = list(profile["callouts"]) + ["root collar"]

    return profile


def build_illustration_brief(row: dict[str, str]) -> tuple[str, str]:
    display_name = row["display_name"]
    key = normalize_key(display_name)
    brief = "\n".join(
        [
            f"- Candidate name: {display_name} (identity unverified).",
            f"- Stable ID: plant-{key.lower().replace('_', '-')}.",
            "- Review state: pending taxonomic, cultivar, and botanical-accuracy review.",
            "- Before drawing: document accepted name, source, diagnostic features, and life stage.",
            "- Do not infer roots, storage organs, flowers, fruits, or leaf structure from this name alone.",
        ]
    )
    prompt = (
        f"Prepare an illustration only after the plant identified as {display_name!r} "
        f"(stable ID plant-{key.lower().replace('_', '-')}) has been taxonomically resolved "
        "and its diagnostic traits have been cited. Do not invent or assume morphology, "
        "cultivar, season, or local growing conditions. Leave unresolved callouts blank; "
        "this generated prompt is a review checklist, not an image or an approved art brief."
    )
    return brief, prompt


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def build_monthly_reference(base_dir: Path) -> None:
    entries = load_csv(base_dir / "calendar_actions.csv")
    grouped: dict[str, dict[str, dict[str, list[dict[str, str]]]]] = defaultdict(
        lambda: defaultdict(lambda: defaultdict(list))
    )
    for entry in entries:
        grouped[entry["month"]][entry["page_type"]][entry["section"]].append(entry)

    labels = {
        "indoor-sowing": "INDOOR SOWING",
        "direct-sowing": "DIRECT SOWING",
        "transplanting": "TRANSPLANTING",
        "succession-sowing": "SUCCESSION SOWING",
        "harvesting": "HARVESTING",
        "flowering": "FLOWERING",
        "pruning": "PRUNING",
        "dividing": "DIVIDING",
        "propagation": "PROPAGATION",
        "seasonal-maintenance": "SEASONAL MAINTENANCE",
        "unclassified": "REVIEW ACTION",
    }
    parts = [
        "# Errington Monthly Garden Reference",
        "",
        "## How to read this calendar",
        "",
        "These are source transcriptions, not independently reviewed recommendations. The "
        "calendar PDF identifies Zone 8a while both chart images identify Zone 8b; the "
        "discrepancy remains unresolved. April 15 and October 15 are approximate source "
        "frost anchors, not guaranteed frost dates.",
        "",
        "Action labels are mechanically classified from transcribed wording. They are not "
        "editorially verified. Plant names joined by a slash or comma are retained as a "
        "source group and must not be interpreted as interchangeable crops.",
        "",
        "Each entry includes its original source page. Grayscale-readable labels are used "
        "instead of relying on the source chart colours.",
        "",
        "## Text action key",
        "",
        "| Label | Meaning in this transcription |",
        "|---|---|",
        "| INDOOR SOWING | Source wording indicates indoor seed starting |",
        "| DIRECT SOWING | Source wording indicates sowing outdoors |",
        "| TRANSPLANTING | Source wording indicates moving established plants |",
        "| SUCCESSION SOWING | Source wording indicates repeat sowing |",
        "| HARVESTING | Source wording indicates picking or harvest |",
        "| FLOWERING | Source wording indicates bloom |",
        "| PRUNING | Source wording indicates pruning or deadheading |",
        "| DIVIDING | Source wording indicates division |",
        "| PROPAGATION | Source wording indicates propagation |",
        "| SEASONAL MAINTENANCE | A seasonal action not matched to another label |",
        "| REVIEW ACTION | The action could not be classified |",
        "",
    ]
    for month in MONTH_ORDER:
        month_data = grouped.get(month)
        if not month_data:
            continue
        parts.extend([f"## {month.title()}", ""])
        for page_type in ["edibles", "ornamentals"]:
            page_data = month_data.get(page_type)
            if not page_data:
                continue
            section_title = "Vegetables and edible crops" if page_type == "edibles" else "Flowers and ornamentals"
            parts.extend([f"### {section_title}", ""])
            for section, section_entries in page_data.items():
                parts.extend([f"#### {section.title()}", ""])
                for entry in section_entries:
                    action_names = [
                        labels.get(action.strip(), action.strip().upper())
                        for action in entry["action_types"].split(";")
                        if action.strip()
                    ]
                    action_label = " / ".join(action_names) if action_names else "REVIEW ACTION"
                    group_note = (
                        " — grouped source entry; individual timing unresolved"
                        if entry["grouped_plant_text"] == "true"
                        else ""
                    )
                    parts.append(
                        f"- **[{action_label}]** {entry['source_transcription']} "
                        f"— source p. {entry['page_number']}{group_note}"
                    )
                parts.append("")

    (base_dir / "ERRINGTON_MONTHLY_REFERENCE.md").write_text("\n".join(parts), encoding="utf-8")


def build_plant_catalog(base_dir: Path) -> None:
    rows = load_csv(base_dir / "plant_registry_enriched.csv")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[row["category"]].append(row)

    parts = [
        "# Errington Plant Registry",
        "",
        "This index preserves the 137 source records. Names and taxonomy already present in "
        "the registry are not independently verified. Calendar matches are source transcriptions, "
        "not plant-specific growing recommendations; grouped source rows may include crops with "
        "different requirements. Generic profile scaffolds are intentionally omitted.",
        "",
    ]
    plant_register = {
        row["common_name"]: row
        for row in load_csv(base_dir / "plant_verification_register.csv")
    }
    for category in sorted(grouped):
        parts.extend([f"## {category.title()}", ""])
        for row in sorted(grouped[category], key=lambda current: current["display_name"]):
            verification = plant_register[row["display_name"]]
            parts.extend([f"### {row['display_name']}", ""])
            parts.append(f"- Stable plant ID: `{verification['plant_id']}`")
            if verification["botanical_name_as_recorded"]:
                parts.append(
                    f"- Botanical name as recorded (unverified): "
                    f"{verification['botanical_name_as_recorded']}"
                )
            if verification["family_as_recorded"]:
                parts.append(f"- Family as recorded (unverified): {verification['family_as_recorded']}")
            parts.append(f"- Source: `{verification['source_id']}` — {verification['source_path']}")
            parts.append(f"- Taxonomy status: `{verification['taxonomy_status']}`")
            parts.append(f"- Profile status: `{verification['profile_status']}`")
            parts.append(f"- Local timing status: `{verification['timing_status']}`")
            parts.append("")

    (base_dir / "ERRINGTON_PLANT_CATALOG.md").write_text("\n".join(parts), encoding="utf-8")


def build_illustration_outputs(base_dir: Path) -> None:
    rows = load_csv(base_dir / "plant_registry_enriched.csv")
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    csv_rows: list[dict[str, str]] = []

    for row in rows:
        row["illustration_brief_status"] = "brief-generated-not-image"
        row["illustration_prompt_status"] = "prompt-generated-not-image"
        grouped[row["category"]].append(row)

    parts = [
        "# Errington Illustration Briefs And Prompts",
        "",
        "This file is generated from the enriched plant registry and provides one botanical illustration brief and one matching plate prompt for every plant in scope.",
        "",
    ]

    for category in sorted(grouped):
        parts.extend([f"## {category.title()}", ""])
        for row in sorted(grouped[category], key=lambda current: current["display_name"]):
            brief, prompt = build_illustration_brief(row)
            parts.extend([f"### {row['display_name']}", "", "#### Botanical Illustration Brief", "", brief, "", "#### Botanical Plate Prompt", "", prompt, ""])
            csv_rows.append(
                {
                    "category": row["category"],
                    "subcategory": row.get("subcategory", ""),
                    "display_name": row["display_name"],
                    "calendar_match_status": row["calendar_match_status"],
                    "calendar_months": row["calendar_months"],
                    "brief": brief,
                    "prompt": prompt,
                }
            )

    (base_dir / ILLUSTRATION_MD).write_text("\n".join(parts), encoding="utf-8")
    write_csv(base_dir / ILLUSTRATION_CSV, csv_rows)
    write_csv(base_dir / "plant_registry_enriched.csv", rows)


def build_illustration_asset_manifest(base_dir: Path) -> None:
    rows = load_csv(base_dir / "plant_registry_enriched.csv")
    illustrations_dir = base_dir / ILLUSTRATION_ASSET_DIR
    illustrations_dir.mkdir(exist_ok=True)

    manifest_rows: list[dict[str, str]] = []
    manifest_parts = [
        "# Illustration Asset Manifest",
        "",
        "Filename suggestions are not image-to-plant assignments. All images require identity, "
        "license, and visual review; none are approved by this manifest.",
        "",
    ]

    for row in sorted(rows, key=lambda current: (current["category"], current["display_name"])):
        key = normalize_key(row["display_name"])
        expected_filename = preferred_illustration_filename(row["display_name"])
        exact_path = illustrations_dir / expected_filename
        asset_status = "pending-review" if exact_path.is_file() else "missing"
        asset_filename = exact_path.name if exact_path.is_file() else ""
        manifest_rows.append(
            {
                "plant_id": f"plant-{key.lower().replace('_', '-')}",
                "category": row["category"],
                "subcategory": row.get("subcategory", ""),
                "display_name": row["display_name"],
                "normalized_key": key,
                "expected_filename": expected_filename,
                "asset_status": asset_status,
                "resolved_filename": asset_filename,
                "creator": "unknown",
                "license": "unknown",
                "review_status": "pending",
                "approval_status": "not-approved",
            }
        )
        manifest_parts.append(
            f"- `{manifest_rows[-1]['plant_id']}` {row['display_name']}: "
            f"{asset_filename or expected_filename} [{asset_status}; not approved]"
        )

    write_csv(illustrations_dir / ILLUSTRATION_MANIFEST_CSV, manifest_rows)
    (illustrations_dir / ILLUSTRATION_MANIFEST_MD).write_text("\n".join(manifest_parts) + "\n", encoding="utf-8")
    missing_lines = [
        row["expected_filename"] for row in manifest_rows if row["asset_status"] == "missing"
    ]
    (illustrations_dir / ILLUSTRATION_MISSING_TXT).write_text(
        "\n".join(missing_lines) + ("\n" if missing_lines else ""), encoding="utf-8"
    )


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    build_monthly_reference(base_dir)
    build_illustration_outputs(base_dir)
    build_plant_catalog(base_dir)
    build_illustration_asset_manifest(base_dir)


if __name__ == "__main__":
    main()