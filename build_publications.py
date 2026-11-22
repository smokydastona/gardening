"""Build the monthly guide and illustrated directory from authoritative source data."""

from __future__ import annotations

import csv
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

from build_final_encyclopedia_pdf import load_plant_illustrations

BASE_DIR = Path(__file__).resolve().parent
MONTHS = ("JANUARY","FEBRUARY","MARCH","APRIL","MAY","JUNE","JULY","AUGUST","SEPTEMBER","OCTOBER","NOVEMBER","DECEMBER")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_monthly_pdf(base_dir: Path) -> Path:
    entries = read_csv(base_dir / "errington_calendar_entries.csv")
    output = base_dir / "Errington_Monthly_Gardening_Guide.pdf"
    styles = getSampleStyleSheet()
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
    output = base_dir / "Errington_Illustrated_Plant_Directory.pdf"
    title = (
        "Errington Illustrated Plant Directory"
        if illustrations
        else "Errington Plant Directory — Illustrations Pending Review"
    )
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(output), pagesize=letter, title=title,
                            author="Errington Gardening Encyclopedia Editorial Project",
                            subject=f"Plant directory — {len(illustrations)} approved illustrations; "
                                    "botanical identities and profiles remain under review")
    story = [Paragraph(title, styles["Title"]),
             Paragraph(
                 f"{len(illustrations)} of {len(registry)} records have approved illustrations. "
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
        story.append(Spacer(1, 6))
    doc.build(story)
    return output


def main() -> None:
    from data_model import validate_authoritative_registry
    validate_authoritative_registry(BASE_DIR)
    print(build_monthly_pdf(BASE_DIR).name)
    print(build_directory_pdf(BASE_DIR).name)


if __name__ == "__main__":
    main()
