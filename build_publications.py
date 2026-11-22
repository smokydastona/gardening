"""Build the monthly guide and illustrated directory from authoritative source data."""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

from build_final_encyclopedia_pdf import load_plant_illustrations

BASE_DIR = Path(__file__).resolve().parent
MONTHS = ("JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE","JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER")
FONT_NAME = "ReenieBeanie"
FONT_PATH = BASE_DIR / "fonts" / "ReenieBeanie.ttf"
pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))


def publication_styles():
    styles = getSampleStyleSheet()
    for style in styles.byName.values():
        style.fontName = FONT_NAME
    return styles


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def load_candidate_manifest(base_dir: Path) -> dict[str, Path]:
    manifest = base_dir / "plant_illustrations" / "concept_candidates" / "candidate_manifest.csv"
    if not manifest.is_file():
        return {}
    candidates: dict[str, Path] = {}
    for row in read_csv(manifest):
        path = manifest.parent / row["filename"]
        if path.is_file():
            candidates[row["plant_id"]] = path
    return candidates


def build_monthly_pdf(base_dir: Path) -> Path:
    entries = read_csv(base_dir / "errington_calendar_entries.csv")
    output = base_dir / "Errington_Monthly_Gardening_Guide.pdf"
    styles = publication_styles()
    doc = SimpleDocTemplate(str(output), pagesize=letter, title="Errington Monthly Gardening Guide",
                            author="Errington Gardening Encyclopedia Editorial Project",
                            subject="Unverified source transcription; not a planting recommendation")
    story = [Paragraph("Errington Monthly Gardening Guide", styles["Title"]),
             Paragraph("Working source-transcription guide — evidence not yet reviewed", styles["Normal"]),
             Spacer(1, 12)]
    for month in MONTHS:
        month_rows = [row for row in entries if row["month"] == month]
        story.append(Paragraph(month.title(), styles["Heading1"]))
        if not month_rows:
            story.append(Paragraph("No documented tasks in the supplied source transcription.", styles["BodyText"]))
        else:
            data = [["Plant/source text","Source timing/action","Evidence state"]]
            for row in month_rows:
                data.append([row["plant_text"], row["row_text"], "Source transcription; unverified"])
            table = Table(data, colWidths=[1.8*inch, 3.7*inch, 1.2*inch], repeatRows=1)
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#51664e")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#9c9c92")),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("FONTSIZE",(0,0),(-1,-1),7),
                ("LEADING",(0,0),(-1,-1),9),
            ]))
            story.append(table)
        story.append(Spacer(1, 8))
    doc.build(story)
    return output


def build_directory_pdf(base_dir: Path) -> Path:
    registry = read_csv(base_dir / "plant_registry.csv")
    verifications = {row["plant_id"]: row for row in read_csv(base_dir / "plant_verification_register.csv")}
    illustrations = load_plant_illustrations(base_dir)
    candidates = load_candidate_manifest(base_dir)
    output = base_dir / "Errington_Illustrated_Plant_Directory.pdf"
    title = (
        "Errington Illustrated Plant Directory"
        if illustrations
        else "Errington Plant Directory — Concept Candidates"
    )
    styles = publication_styles()
    doc = SimpleDocTemplate(str(output), pagesize=letter, title=title,
                            author="Errington Gardening Encyclopedia Editorial Project",
                            subject=f"Plant directory — {len(illustrations)} approved illustrations; "
                                    "botanical identities and profiles remain under review")
    story = [Paragraph(title, styles["Title"]),
             Paragraph(
                 f"{len(illustrations)} of {len(registry)} records have approved illustrations. "
                 f"{len(candidates)} of {len(registry)} records have generated concept candidates. "
                 "Botanical names and profiles remain unverified unless noted.",
                 styles["Normal"],
             ),
             Spacer(1, 12)]
    for row in sorted(registry, key=lambda item: item["display_name"].casefold()):
        plant_id = row["plant_id"]
        verification = verifications.get(plant_id, {})
        story.append(Paragraph(row["display_name"], styles["Heading2"]))
        story.append(Paragraph(
            f"Recorded botanical name: {row.get('latin_name','unknown')}<br/>"
            f"Family as recorded: {row.get('family','unknown')}<br/>"
            f"Taxonomy: {verification.get('taxonomy_status','unreviewed')}<br/>"
            f"Cultivar: {verification.get('cultivar_status','unreviewed')}<br/>"
            f"Illustration: {verification.get('illustration_status','pending-review')}",
            styles["BodyText"]))
        illustration = illustrations.get(plant_id)
        candidate = candidates.get(plant_id)
        displayed = illustration or candidate
        if displayed:
            reader = ImageReader(str(displayed))
            image_width, image_height = reader.getSize()
            scale = min(2.4 * inch / image_width, 3.6 * inch / image_height)
            image = Image(
                str(displayed),
                width=image_width * scale,
                height=image_height * scale,
            )
            image.hAlign = "CENTER"
            story.extend([Spacer(1, 6), image])
            if candidate and not illustration:
                story.append(Paragraph(
                    "Concept candidate — not botanically approved",
                    styles["Normal"],
                ))
        story.append(Spacer(1, 6))
    doc.build(story)
    return output


def build_botanical_collection_pdf(base_dir: Path) -> Path:
    registry = read_csv(base_dir / "plant_registry.csv")
    candidates = load_candidate_manifest(base_dir)
    output = base_dir / "Errington_Botanical_Illustration_Collection.pdf"
    styles = publication_styles()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        title="Errington Botanical Illustration Collection",
        author="Errington Gardening Encyclopedia Editorial Project",
        subject="137 concept candidates; no image is approved for botanical publication",
    )
    story = [
        Paragraph("Errington Botanical Illustration Collection", styles["Title"]),
        Paragraph(
            f"{len(candidates)} concept candidates for {len(registry)} registry records. "
            "Every plate is explicitly unapproved and may require species identity, anatomy "
            "and rights review. Concept silhouettes are not botanical evidence.",
            styles["Normal"],
        ),
    ]
    for row in sorted(registry, key=lambda item: item["display_name"].casefold()):
        story.extend([
            PageBreak(),
            Paragraph(row["display_name"], styles["Heading1"]),
            Paragraph(
                f"Stable ID: {row['plant_id']}<br/>"
                f"Recorded name: {row['latin_name'] or 'Unresolved'}<br/>"
                f"Family: {row['family'] or 'Unresolved'}",
                styles["Normal"],
            ),
        ])
        candidate = candidates.get(row["plant_id"])
        if candidate:
            reader = ImageReader(str(candidate))
            iw, ih = reader.getSize()
            scale = min(5.5 * inch / iw, 7.0 * inch / ih)
            image = Image(str(candidate), width=iw * scale, height=ih * scale)
            image.hAlign = "CENTER"
            story.extend([Spacer(1, 8), image])
        story.append(Paragraph(
            "CONCEPT CANDIDATE - NOT BOTANICALLY APPROVED",
            styles["Normal"],
        ))
    doc.build(story)
    return output


def build_figure_collection_pdf(base_dir: Path) -> Path:
    manifest = base_dir / "educational_figures" / "figure_manifest.csv"
    figures = read_csv(manifest)
    output = base_dir / "Errington_Educational_Figure_Collection.pdf"
    styles = publication_styles()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        title="Errington Educational Figure Collection",
        author="Errington Gardening Encyclopedia Editorial Project",
        subject="36 educational concept figures pending source and human review",
    )
    story = [
        Paragraph("Errington Educational Figure Collection", styles["Title"]),
        Paragraph(
            f"{len(figures)} stable educational figures. Captions and accessibility text are "
            "included; source references and final human review remain pending.",
            styles["Normal"],
        ),
    ]
    for row in figures:
        path = base_dir / "educational_figures" / row["filename"]
        story.extend([
            PageBreak(),
            Paragraph(row["title"], styles["Heading1"]),
            Paragraph(row["caption"], styles["Normal"]),
        ])
        if path.is_file():
            reader = ImageReader(str(path))
            iw, ih = reader.getSize()
            scale = min(7.1 * inch / iw, 7.5 * inch / ih)
            image = Image(str(path), width=iw * scale, height=ih * scale)
            image.hAlign = "CENTER"
            story.extend([Spacer(1, 8), image])
        story.extend([
            Paragraph(f"Accessibility text: {row['accessibility_text']}", styles["Normal"]),
            Paragraph(f"Figure ID: {row['figure_id']}; {row['approval_status']}", styles["Normal"]),
        ])
    doc.build(story)
    return output


def main() -> None:
    from data_model import validate_authoritative_registry
    validate_authoritative_registry(BASE_DIR)
    print(build_monthly_pdf(BASE_DIR).name)
    print(build_directory_pdf(BASE_DIR).name)
    print(build_botanical_collection_pdf(BASE_DIR).name)
    print(build_figure_collection_pdf(BASE_DIR).name)


if __name__ == "__main__":
    main()
