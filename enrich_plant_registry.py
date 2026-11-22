from __future__ import annotations

import csv
import re
from pathlib import Path


DESCRIPTOR_WORDS = {
    "EARLY",
    "LATE",
    "MAIN",
    "WINTER",
    "SUMMER",
    "SPRING",
    "FALL",
    "FORCED",
    "STORED",
    "BARE",
    "ROOT",
    "ROOTS",
    "NEW",
    "HARDY",
    "ORNAMENTAL",
    "PROTECTED",
    "OVERWINTERING",
    "OVERWINTERED",
}


def normalize(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", text.upper()).strip("_")


def alias_variants(value: str) -> set[str]:
    variants = set()
    if not value:
        return variants
    variants.add(value)
    if value.endswith("S"):
        variants.add(value[:-1])
    else:
        variants.add(f"{value}S")
    if value.endswith("IES"):
        variants.add(f"{value[:-3]}Y")
    if value.endswith("Y"):
        variants.add(f"{value[:-1]}IES")
    return {item for item in variants if item}


def clean_alias_part(part: str) -> str:
    part = re.sub(r"\([^)]*\)", "", part)
    part = part.replace("&", " ")
    words = [word for word in re.split(r"\s+", part.upper()) if word]
    while words and words[0] in DESCRIPTOR_WORDS:
        words.pop(0)
    return normalize(" ".join(words))


def entry_aliases(plant_text: str) -> set[str]:
    raw_parts = re.split(r"/|,", plant_text)
    aliases = {normalize(plant_text)}
    for part in raw_parts:
        cleaned = clean_alias_part(part)
        if cleaned:
            aliases.update(alias_variants(cleaned))
    return aliases


def registry_aliases(row: dict[str, str]) -> set[str]:
    aliases: set[str] = set()
    for key in ("display_name", "source_name", "normalized_name"):
        value = row.get(key, "").strip()
        if value:
            aliases.update(alias_variants(normalize(value)))
    return aliases


def load_calendar_entries(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def normalize_registry_row(fieldnames: list[str], row: list[str]) -> list[str]:
    if len(row) == len(fieldnames):
        return row

    maintenance_index = fieldnames.index("maintenance_notes")
    expected_tail_length = len(fieldnames) - maintenance_index
    current_tail_length = len(row) - maintenance_index

    if current_tail_length == expected_tail_length - 2:
        row = row[:maintenance_index] + ["", ""] + row[maintenance_index:]

    if len(row) < len(fieldnames):
        row = row + [""] * (len(fieldnames) - len(row))
    elif len(row) > len(fieldnames):
        row = row[: len(fieldnames)]

    return row


def load_registry_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle)
        try:
            fieldnames = next(reader)
        except StopIteration as error:
            raise RuntimeError("Plant registry is empty.") from error

        rows: list[dict[str, str]] = []
        for raw_row in reader:
            normalized_row = normalize_registry_row(fieldnames, raw_row)
            rows.append(dict(zip(fieldnames, normalized_row, strict=True)))
    return rows


PLANT_TAXONOMY = {
    "Arugula": ("Eruca vesicaria subsp. sativa", "Brassicaceae"),
    "Asparagus": ("Asparagus officinalis", "Asparagaceae"),
    "Beans": ("Phaseolus vulgaris", "Fabaceae"),
    "Beets": ("Beta vulgaris", "Amaranthaceae"),
    "Bell Pepper": ("Capsicum annuum", "Solanaceae"),
    "Broccoli": ("Brassica oleracea var. italica", "Brassicaceae"),
    "Brussels Sprouts": ("Brassica oleracea var. gemmifera", "Brassicaceae"),
    "Cabbage": ("Brassica oleracea var. capitata", "Brassicaceae"),
    "Cantaloupe": ("Cucumis melo", "Cucurbitaceae"),
    "Carrots": ("Daucus carota subsp. sativus", "Apiaceae"),
    "Cauliflower": ("Brassica oleracea var. botrytis", "Brassicaceae"),
    "Celery": ("Apium graveolens var. dulce", "Apiaceae"),
    "Corn": ("Zea mays", "Poaceae"),
    "Cucumber": ("Cucumis sativus", "Cucurbitaceae"),
    "Garlic": ("Allium sativum", "Amaryllidaceae"),
    "Kohlrabi": ("Brassica oleracea var. gongylodes", "Brassicaceae"),
    "Leeks": ("Allium ampeloprasum", "Amaryllidaceae"),
    "Lettuce": ("Lactuca sativa", "Asteraceae"),
    "Eggplant": ("Solanum melongena", "Solanaceae"),
    "Melons": ("Cucumis melo", "Cucurbitaceae"),
    "Okra": ("Abelmoschus esculentus", "Malvaceae"),
    "Parsnips": ("Pastinaca sativa", "Apiaceae"),
    "Peas": ("Pisum sativum", "Fabaceae"),
    "Potatoes": ("Solanum tuberosum", "Solanaceae"),
    "Spinach": ("Spinacia oleracea", "Amaranthaceae"),
    "Sweet Potato": ("Ipomoea batatas", "Convolvulaceae"),
    "Summer Squash": ("Cucurbita pepo", "Cucurbitaceae"),
    "Swiss Chard": ("Beta vulgaris subsp. cicla", "Amaranthaceae"),
    "Tomatoes": ("Solanum lycopersicum", "Solanaceae"),
    "Marigold": ("Tagetes patula", "Asteraceae"),
    "Zinnia": ("Zinnia elegans", "Asteraceae"),
    "Cosmos": ("Cosmos bipinnatus", "Asteraceae"),
    "Nasturtium": ("Tropaeolum majus", "Tropaeolaceae"),
    "Sunflower": ("Helianthus annuus", "Asteraceae"),
    "Sweet Pea": ("Lathyrus odoratus", "Fabaceae"),
    "Calendula": ("Calendula officinalis", "Asteraceae"),
    "Dahlia": ("Dahlia pinnata", "Asteraceae"),
    "Peony": ("Paeonia lactiflora", "Paeoniaceae"),
    "Iris": ("Iris × germanica", "Iridaceae"),
    "Daylily": ("Hemerocallis × hybrida", "Asphodelaceae"),
    "Lavender": ("Lavandula angustifolia", "Lamiaceae"),
    "Echinacea": ("Echinacea purpurea", "Asteraceae"),
    "Rudbeckia": ("Rudbeckia hirta", "Asteraceae"),
    "Tulip": ("Tulipa gesneriana", "Liliaceae"),
    "Daffodil": ("Narcissus pseudonarcissus", "Amaryllidaceae"),
    "Crocus": ("Crocus vernus", "Iridaceae"),
    "Allium": ("Allium hollandicum", "Amaryllidaceae"),
    "Hyacinth": ("Hyacinthus orientalis", "Asparagaceae"),
    "Hostas": ("Hosta spp.", "Asparagaceae"),
    "Ferns": ("Fern species / multiple genera", "Multiple families"),
    "Ornamental Grasses": ("Ornamental grass species / multiple genera", "Poaceae"),
    "Sedum": ("Hylotelephium telephium", "Crassulaceae"),
    "Heuchera": ("Heuchera sanguinea", "Saxifragaceae"),
    "Astilbe": ("Astilbe × arendsii", "Saxifragaceae"),
    "Rosemary": ("Salvia rosmarinus", "Lamiaceae"),
    "Thyme": ("Thymus vulgaris", "Lamiaceae"),
    "Oregano": ("Origanum vulgare", "Lamiaceae"),
    "Parsley": ("Petroselinum crispum", "Apiaceae"),
    "Chives": ("Allium schoenoprasum", "Amaryllidaceae"),
    "Basil": ("Ocimum basilicum", "Lamiaceae"),
    "Dill": ("Anethum graveolens", "Apiaceae"),
    "Cilantro": ("Coriandrum sativum", "Apiaceae"),
    "Chervil": ("Anthriscus cerefolium", "Apiaceae"),
    "Fennel": ("Foeniculum vulgare", "Apiaceae"),
    "Apple": ("Malus domestica", "Rosaceae"),
    "Pear": ("Pyrus communis", "Rosaceae"),
    "Plum": ("Prunus domestica", "Rosaceae"),
    "Cherry": ("Prunus avium", "Rosaceae"),
    "Grapes": ("Vitis vinifera", "Vitaceae"),
    "Strawberries": ("Fragaria × ananassa", "Rosaceae"),
    "Raspberries": ("Rubus idaeus", "Rosaceae"),
    "Blueberries": ("Vaccinium corymbosum", "Ericaceae"),
    "Currants": ("Ribes rubrum", "Grossulariaceae"),
    "Gooseberries": ("Ribes uva-crispa", "Grossulariaceae"),
    "Rhubarb": ("Rheum × hybridum", "Polygonaceae"),
    "Globe Artichoke": ("Cynara cardunculus var. scolymus", "Asteraceae"),
    "Snapdragons": ("Antirrhinum majus", "Plantaginaceae"),
    "Petunias": ("Petunia × atkinsiana", "Solanaceae"),
    "Lobelia": ("Lobelia erinus", "Campanulaceae"),
    "Pansy": ("Viola × wittrockiana", "Violaceae"),
    "Stocks": ("Matthiola incana", "Brassicaceae"),
    "Statice": ("Limonium sinuatum", "Plumbaginaceae"),
    "Antirrhinum": ("Antirrhinum majus", "Plantaginaceae"),
    "Impatiens": ("Impatiens walleriana", "Balsaminaceae"),
    "Nicotiana": ("Nicotiana alata", "Solanaceae"),
    "Cleome": ("Cleome hassleriana", "Cleomaceae"),
    "Larkspur": ("Consolida ajacis", "Ranunculaceae"),
    "Poppy": ("Papaver rhoeas", "Papaveraceae"),
    "Nigella": ("Nigella damascena", "Ranunculaceae"),
    "Borage": ("Borago officinalis", "Boraginaceae"),
    "Cornflower": ("Centaurea cyanus", "Asteraceae"),
    "Ammi majus": ("Ammi majus", "Apiaceae"),
    "Orlaya": ("Orlaya grandiflora", "Apiaceae"),
    "Celosia": ("Celosia argentea", "Amaranthaceae"),
    "Strawflower": ("Xerochrysum bracteatum", "Asteraceae"),
    "Scabiosa": ("Scabiosa atropurpurea", "Caprifoliaceae"),
    "Hellebores": ("Helleborus orientalis", "Ranunculaceae"),
    "Snowdrops": ("Galanthus nivalis", "Amaryllidaceae"),
    "Delphinium": ("Delphinium elatum", "Ranunculaceae"),
    "Salvia nemorosa": ("Salvia nemorosa", "Lamiaceae"),
    "Gaillardia": ("Gaillardia aristata", "Asteraceae"),
    "Asters": ("Symphyotrichum novi-belgii", "Asteraceae"),
    "Primula": ("Primula vulgaris", "Primulaceae"),
    "Wallflower": ("Erysimum cheiri", "Brassicaceae"),
    "Aubretia": ("Aubrieta deltoidea", "Brassicaceae"),
    "Iberis": ("Iberis sempervirens", "Brassicaceae"),
    "Hyacinths": ("Hyacinthus orientalis", "Asparagaceae"),
    "Muscari": ("Muscari armeniacum", "Asparagaceae"),
    "Gladiolus": ("Gladiolus × hortulanus", "Iridaceae"),
    "Anemone": ("Anemone coronaria", "Ranunculaceae"),
    "Camassia": ("Camassia quamash", "Asparagaceae"),
    "Witch Hazel": ("Hamamelis virginiana", "Hamamelidaceae"),
    "Buddleja": ("Buddleja davidii", "Scrophulariaceae"),
    "Deutzia": ("Deutzia gracilis", "Hydrangeaceae"),
    "Hydrangea paniculata": ("Hydrangea paniculata", "Hydrangeaceae"),
    "Roses": ("Rosa spp.", "Rosaceae"),
    "Forsythia": ("Forsythia × intermedia", "Oleaceae"),
    "Philadelphus": ("Philadelphus coronarius", "Hydrangeaceae"),
    "Pieris": ("Pieris japonica", "Ericaceae"),
    "Magnolia": ("Magnolia stellata", "Magnoliaceae"),
    "Camellia": ("Camellia japonica", "Theaceae"),
    "Rhododendron": ("Rhododendron spp.", "Ericaceae"),
    "Spiraea": ("Spiraea japonica", "Rosaceae"),
    "Azalea": ("Rhododendron spp.", "Ericaceae"),
    "Kerria": ("Kerria japonica", "Rosaceae"),
    "Garry Oak": ("Quercus garryana", "Fagaceae"),
    "Wisteria": ("Wisteria sinensis", "Fabaceae"),
    "Clematis Group 3": ("Clematis spp. (pruning Group 3)", "Ranunculaceae"),
    "Clematis montana": ("Clematis montana", "Ranunculaceae"),
    "Honeysuckle": ("Lonicera spp.", "Caprifoliaceae"),
    "Morning Glory": ("Ipomoea purpurea", "Convolvulaceae"),
    "Osoberry": ("Oemleria cerasiformis", "Rosaceae"),
    "Red-flowering Currant": ("Ribes sanguineum", "Grossulariaceae"),
    "Trillium": ("Trillium ovatum", "Melanthiaceae"),
    "Bleeding Heart": ("Dicentra formosa", "Papaveraceae"),
    "Camas": ("Camassia quamash", "Asparagaceae"),
    "Sword Fern": ("Polystichum munitum", "Dryopteridaceae"),
}


def bulk_culture_profile(row: dict[str, str]) -> dict[str, str]:
    category = row["category"]
    subcategory = row.get("subcategory", "")
    name = row["display_name"]
    latin, family = PLANT_TAXONOMY.get(name, ("", ""))

    perennial_herbs = {"Rosemary", "Thyme", "Oregano", "Chives", "Fennel"}
    biennial_herbs = {"Parsley"}
    if subcategory == "annual":
        life_cycle = "Annual"
    elif name in perennial_herbs or name in {"Asparagus", "Rhubarb", "Globe Artichoke"}:
        life_cycle = "Perennial"
    elif name in biennial_herbs:
        life_cycle = "Biennial, often grown as an annual"
    elif category in {"vegetable", "herb"}:
        life_cycle = "Annual" if name not in {"Asparagus", "Rhubarb", "Globe Artichoke"} else "Perennial"
    elif subcategory == "bulb":
        life_cycle = "Perennial; grown from a bulb, corm, or storage organ"
    elif subcategory == "perennial":
        life_cycle = "Perennial"
    elif category in {"shrub-tree", "native", "vine", "fruit"}:
        life_cycle = "Perennial"
    else:
        life_cycle = "Perennial or variable; species-level resolution required"

    if category == "vegetable":
        soil = "Well-drained, fertile soil with organic matter; adjust for the crop's root depth."
        water = "Keep moisture even during establishment and harvest formation; avoid prolonged waterlogging."
        light = "Full sun is usual; leafy cool-season crops tolerate more partial shade."
        spacing = "Use the calendar, seed packet, or mature crop size; do not rely on a registry-wide spacing value."
        maintenance = "Thin, weed, mulch, and monitor; support or stake as the crop requires."
        pests = "Monitor locally for aphids, slugs, caterpillars, fungal leaf spots, and soil-borne disease; identify before treatment."
    elif category == "ornamental":
        soil = "Choose a well-drained soil matched to the plant; the label and species can vary widely."
        water = "Water to establish, then match moisture to the specific ornamental's type."
        light = "Check the specific species; full sun, shade, and moisture labels may vary across genera."
        spacing = "Allow for mature clump or canopy width; label or cultivar may change the correct spacing."
        maintenance = "Remove damaged growth, divide where applicable, mulch carefully, and avoid overwatering."
        pests = "Monitor for slugs, aphids, mites, scale, and fungal leaf problems; use identification and prevention first."
    elif category == "native":
        soil = "Use a native-plant soil profile matching the species' natural moisture and exposure."
        water = "Provide supplemental water only during establishment unless the species is naturally moisture-demanding."
        light = "Match sun or shade to the species and local site."
        spacing = "Use mature native-plant size and avoid crowding at establishment."
        maintenance = "Protect soil and leaf litter where appropriate; avoid heavy fertilizer; prune only for structure or safety."
        pests = "Favor prevention and local beneficial organisms; treat only confirmed damage."
    else:
        soil = "Fertile, well-drained soil with organic matter unless the species has a known exceptional preference."
        water = "Provide even establishment moisture; then follow the species' drought, moisture, or wetness preference."
        light = "Sun requirement is species-specific; the common name alone is not a reliable light label."
        spacing = "Base spacing on mature height and spread, not just the common name."
        maintenance = "Mulch, deadhead or divide as appropriate, and monitor for structural or seasonal maintenance."
        pests = "Identify the pest or disease locally before control; favor sanitation, cultural prevention, and targeted action."

    if subcategory == "bulb":
        roots = "Basal plate and fibrous roots; bulb or corm storage organ."
        leaves = "Basal or sheathing leaves; strap, linear, or species-specific blades."
        flowers = "Species-specific flower or inflorescence; generally showy and arranged to attract pollinators."
        fruit = "Seed capsule or berry may follow flowering."
    elif category == "native":
        roots = "Species-specific perennial root or rhizome system; do not infer a single organ from the common name."
        leaves = "Leaves follow the characteristic genus or species; arrangement and shape require species-level verification."
        flowers = "Species-specific bloom structure; bloom timing in Errington remains calendar-dependent."
        fruit = "Fruit or seed structure follows the species; verify before illustration or propagation."
    elif category == "fruit":
        roots = "Woody perennial root system; grafted trees may include rootstock-specific traits."
        leaves = "Alternate or opposite foliage according to the exact genus; use species-level morphology."
        flowers = "Flowers arranged in species-specific racemes, clusters, umbels, or catkins."
        fruit = "Botanical fruit type is species-specific: pome, drupe, berry, aggregate fruit, or grape."
    elif category == "vine":
        roots = "Perennial or annual anchored root system; species-specific climbing or trailing habit."
        leaves = "Alternate or opposite leaves according to genus; vine support is an identifying feature."
        flowers = "Species-specific inflorescence or solitary bloom."
        fruit = "Pod, capsule, berry, or dry seed structure according to species."
    elif category == "ornamental":
        roots = "Fibrous, rhizomatous, clumping, or fleshy according to the species."
        leaves = "Species- or genus-specific leaf arrangement and shape; generic label needs disambiguation."
        flowers = "Species-specific flower form; local bloom timing comes from the Errington calendar if matched."
        fruit = "Seed capsule, achene, berry, or no conspicuous fruit according to species."
    else:
        roots = "Species-specific root, crown, or storage organ; verify the exact form before illustrating."
        leaves = "Species-specific arrangement and blade shape; verify exact genus and cultivar."
        flowers = "Species-specific inflorescence or flower structure."
        fruit = "Species-specific fruit, seed pod, achene, capsule, berry, or nut."

    if name in {"Ferns", "Ornamental Grasses", "Poppy", "Pansy", "Roses", "Rhododendron", "Azalea", "Honeysuckle", "Beans", "Melons", "Hostas", "Iris", "Peony", "Asters", "Garry Oak"}:
        verification = "taxonomy-requires-species-or-cultivar-resolution"
    else:
        verification = "bulk-taxonomy-populated"

    existing_notes = row.get("notes", "").strip()
    source_note = "Taxonomy profile synthesized from USDA PLANTS/GBIF taxon concepts and the supplied public-domain references; verify species-level cultivar details before use."
    notes = " ".join(piece for piece in (existing_notes, source_note) if piece)
    return {
        "latin_name": latin,
        "family": family,
        "life_cycle": life_cycle,
        "growth_habit": "Growth habit should be resolved to the exact species or cultivar; this entry provides a category-level source scaffold.",
        "root_or_storage_organ": roots,
        "leaf_arrangement_shape": leaves,
        "flower_structure": flowers,
        "fruit_seed_structure": fruit,
        "soil_notes": soil,
        "water_notes": water,
        "spacing_notes": spacing,
        "light_notes": light,
        "maintenance_notes": maintenance,
        "pests_diseases": pests,
        "verification_status": verification,
        "notes": notes,
    }


def enrich_registry(base_dir: Path) -> list[dict[str, str]]:
    registry_path = base_dir / "plant_registry.csv"
    entries_path = base_dir / "errington_calendar_entries.csv"
    registry_rows = load_registry_rows(registry_path)
    entries = load_calendar_entries(entries_path)
    entry_lookup = [(entry, entry_aliases(entry["plant_text"])) for entry in entries]

    enriched_rows: list[dict[str, str]] = []
    for row in registry_rows:
        aliases = registry_aliases(row)
        matched_entries: list[dict[str, str]] = []
        for entry, entry_alias_set in entry_lookup:
            if aliases & entry_alias_set:
                matched_entries.append(entry)

        months = []
        actions = []
        sections = []
        page_types = []
        for entry in matched_entries:
            if entry["month"] and entry["month"] not in months:
                months.append(entry["month"])
            action = f"{entry['month']}: {entry['row_text']}"
            if action not in actions:
                actions.append(action)
            if entry["section"] and entry["section"] not in sections:
                sections.append(entry["section"])
            if entry["page_type"] and entry["page_type"] not in page_types:
                page_types.append(entry["page_type"])

        enriched = dict(row)
        enriched["calendar_match_count"] = str(len(matched_entries))
        enriched["calendar_months"] = "; ".join(months)
        enriched["calendar_sections"] = "; ".join(sections)
        enriched["calendar_page_types"] = "; ".join(page_types)
        enriched["calendar_actions"] = " || ".join(actions)
        enriched["calendar_match_status"] = "matched" if matched_entries else "unmatched"
        enriched.update(bulk_culture_profile(enriched))
        enriched_rows.append(enriched)

    return enriched_rows


def write_enriched_registry(path: Path, rows: list[dict[str, str]]) -> None:
    if not rows:
        raise RuntimeError("No registry rows available to write.")
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    registry_rows = load_registry_rows(base_dir / "plant_registry.csv")
    populated_rows = []
    for row in registry_rows:
        populated = dict(row)
        populated.update(bulk_culture_profile(populated))
        populated_rows.append(populated)
    write_enriched_registry(base_dir / "plant_registry.csv", populated_rows)
    rows = enrich_registry(base_dir)
    write_enriched_registry(base_dir / "plant_registry_enriched.csv", rows)


if __name__ == "__main__":
    main()