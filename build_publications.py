"""Build the monthly guide and illustrated directory from authoritative source data."""

from __future__ import annotations

import csv
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
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
        style.fontName = "Times-Roman"
    for style_name in ("Title", "Heading1", "Heading2", "Heading3"):
        styles[style_name].fontName = FONT_NAME
    return styles


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def clean_source_pictograms(text: str) -> str:
    for marker in ("🌍", "🌿", "🌾", "🌸", "❄", "✄", "🍅", "🌲", "💡", "📖", "📌", "🏞", "✓"):
        text = text.replace(marker, " ")
    return " ".join(text.split())


def build_monthly_pdf(base_dir: Path) -> Path:
    entries = read_csv(base_dir / "errington_calendar_entries.csv")
    actions = read_csv(base_dir / "calendar_actions.csv")
    action_labels = {
        "indoor-sowing": "Indoor sowing",
        "direct-sowing": "Direct sowing",
        "transplanting": "Transplanting",
        "succession-sowing": "Succession sowing",
        "harvesting": "Harvesting",
        "flowering": "Flowering",
        "pruning": "Pruning",
        "dividing": "Dividing",
        "propagation": "Propagation",
        "planting": "Planting",
        "frost-risk": "Frost risk",
        "seasonal-maintenance": "Seasonal maintenance",
        "seasonal-observation": "Source observation",
        "unclassified": "Review required",
    }
    action_by_entry = {
        (row["month"], row["page_number"], row["plant_text"], row["source_transcription"]):
            " / ".join(
                action_labels.get(action.strip(), action.strip())
                for action in row["action_types"].split(";")
                if action.strip()
            )
        for row in actions
    }
    output = base_dir / "Errington_Monthly_Gardening_Guide.pdf"
    styles = publication_styles()
    cell_style = ParagraphStyle(
        "MonthlyCell",
        parent=styles["BodyText"],
        fontName="Times-Roman",
        fontSize=8,
        leading=9.5,
        spaceAfter=0,
    )
    header_style = ParagraphStyle(
        "MonthlyHeader",
        parent=cell_style,
        fontName="Times-Bold",
        textColor=colors.white,
    )
    doc = SimpleDocTemplate(str(output), pagesize=landscape(letter), title="Errington Monthly Gardening Guide",
                            author="Errington Gardening Encyclopedia Editorial Project",
                            subject="Unverified source transcription; not a planting recommendation")
    story = [Paragraph("Errington Monthly Gardening Guide", styles["Title"]),
             Paragraph(
                 "Working source transcription — not a reviewed planting recommendation. "
                 "Pictograms are omitted from display; original rows remain in the source CSV.",
                 styles["Normal"],
             ),
             Spacer(1, 12),
             PageBreak()]
    for month_index, month in enumerate(MONTHS):
        if month_index:
            story.append(PageBreak())
        month_rows = [row for row in entries if row["month"] == month]
        story.append(Paragraph(month.title(), styles["Heading1"]))
        if not month_rows:
            story.append(Paragraph("No documented tasks in the supplied source transcription.", styles["BodyText"]))
        else:
            data = [[
                Paragraph(label, header_style)
                for label in ("Plant/source text", "Timing/action", "Action label", "Source page", "Evidence state")
            ]]
            for row in month_rows:
                action_key = (
                    row["month"],
                    row.get("page_number", ""),
                    row["plant_text"],
                    row["row_text"],
                )
                data.append([
                    Paragraph(escape(clean_source_pictograms(row["plant_text"])), cell_style),
                    Paragraph(escape(clean_source_pictograms(row["row_text"])), cell_style),
                    Paragraph(escape(action_by_entry.get(action_key, "Review required")), cell_style),
                    Paragraph(escape(row.get("page_number", "")), cell_style),
                    Paragraph("Transcription; unverified", cell_style),
                ])
            table = Table(
                data,
                colWidths=[1.65 * inch, 3.1 * inch, 1.45 * inch, 0.65 * inch, 1.3 * inch],
                repeatRows=1,
            )
            table.setStyle(TableStyle([
                ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#51664e")),
                ("TEXTCOLOR",(0,0),(-1,0),colors.white),
                ("GRID",(0,0),(-1,-1),0.25,colors.HexColor("#9c9c92")),
                ("VALIGN",(0,0),(-1,-1),"TOP"),
                ("LEFTPADDING",(0,0),(-1,-1),4),
                ("RIGHTPADDING",(0,0),(-1,-1),4),
                ("TOPPADDING",(0,0),(-1,-1),3),
                ("BOTTOMPADDING",(0,0),(-1,-1),3),
            ]))
            story.append(table)
    doc.build(story)
    return output


def build_directory_pdf(base_dir: Path) -> Path:
    registry = read_csv(base_dir / "plant_registry.csv")
    verifications = {row["plant_id"]: row for row in read_csv(base_dir / "plant_verification_register.csv")}
    illustrations = load_plant_illustrations(base_dir)
    output = base_dir / "Errington_Illustrated_Plant_Directory.pdf"
    title = (
        "Errington Illustrated Plant Directory"
        if illustrations
        else "Errington Plant Directory — Verified Illustrations Pending"
    )
    styles = publication_styles()
    doc = SimpleDocTemplate(str(output), pagesize=letter, title=title,
                            author="Errington Gardening Encyclopedia Editorial Project",
                            subject=f"Plant directory — {len(illustrations)} approved illustrations; "
                                    "botanical identities and profiles remain under review")
    story = [Paragraph(title, styles["Title"]),
             Paragraph(
                 f"{len(illustrations)} of {len(registry)} records have approved illustrations. "
                 "Unapproved concept art is withheld. Botanical names and profiles remain "
                 "unverified unless noted.",
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
        if illustration:
            reader = ImageReader(str(illustration))
            image_width, image_height = reader.getSize()
            scale = min(2.4 * inch / image_width, 3.6 * inch / image_height)
            image = Image(
                str(illustration),
                width=image_width * scale,
                height=image_height * scale,
            )
            image.hAlign = "CENTER"
            story.extend([Spacer(1, 6), image])
        else:
            story.append(Paragraph(
                "No illustration included; awaiting independent botanical and rights review.",
                styles["Normal"],
            ))
        story.append(Spacer(1, 6))
    doc.build(story)
    return output


def build_botanical_collection_pdf(base_dir: Path) -> Path:
    registry = read_csv(base_dir / "plant_registry.csv")
    illustrations = load_plant_illustrations(base_dir)
    output = base_dir / "Errington_Botanical_Illustration_Collection.pdf"
    styles = publication_styles()
    doc = SimpleDocTemplate(
        str(output),
        pagesize=letter,
        title="Errington Botanical Illustration Review Register",
        author="Errington Gardening Encyclopedia Editorial Project",
        subject=f"{len(illustrations)} approved illustrations; unapproved artwork is withheld",
    )
    story = [
        Paragraph("Errington Botanical Illustration Review Register", styles["Title"]),
        Paragraph(
            f"{len(illustrations)} approved illustrations for {len(registry)} registry records. "
            "Unapproved generated or branch artwork is withheld from this publication.",
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
        illustration = illustrations.get(row["plant_id"])
        if illustration:
            reader = ImageReader(str(illustration))
            iw, ih = reader.getSize()
            scale = min(5.5 * inch / iw, 7.0 * inch / ih)
            image = Image(str(illustration), width=iw * scale, height=ih * scale)
            image.hAlign = "CENTER"
            story.extend([Spacer(1, 8), image])
            story.append(Paragraph("Approved botanical illustration.", styles["Normal"]))
        else:
            story.append(Paragraph(
                "No illustration included; awaiting independent botanical and rights review.",
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
        story.extend([
            PageBreak(),
            Paragraph(row["title"], styles["Heading1"]),
            Paragraph(row["caption"], styles["Normal"]),
        ])
        story.extend([
            Paragraph(f"Accessibility text: {row['accessibility_text']}", styles["Normal"]),
            Paragraph(
                f"Figure ID: {row['figure_id']}; {row['approval_status']}. "
                "Artwork withheld pending source verification and expert review.",
                styles["Normal"],
            ),
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
