from __future__ import annotations

from pathlib import Path
import re
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle


TITLE = "Errington Gardening Encyclopedia"
SUBTITLE = "Errington-local growing calendar and plant catalog"
OUTPUT_PDF = "Errington_Gardening_Encyclopedia.pdf"
OUTPUT_MD = "Errington_Gardening_Encyclopedia_Compiled.md"
COVER_IMAGE = "cover.png"
PLANT_ILLUSTRATIONS_DIR = "plant_illustrations"
PLANT_ILLUSTRATION_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")
BOOK_PAGE_SIZE = (6.125 * inch, 9.25 * inch)
PAPER_COLOR = colors.HexColor("#f6f0e2")
INK_COLOR = colors.HexColor("#2d2a26")
ACCENT_COLOR = colors.HexColor("#51664e")
MUTED_COLOR = colors.HexColor("#7b756c")

SOURCE_FILES = [
    ("Core Handbook", "ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md", "Local climate notes, gardening foundations, and regional pollinator guidance with source limits."),
    ("Monthly Reference", "ERRINGTON_MONTHLY_REFERENCE.md", "Month-by-month scheduling aligned to the local planting calendar."),
    ("Plant Catalog", "ERRINGTON_PLANT_CATALOG.md", "Plant-by-plant notes grounded in the parsed Errington registry and calendar matches."),
    ("Illustration Briefs", "ERRINGTON_ILLUSTRATION_BRIEFS_AND_PROMPTS.md", "Per-plant botanical illustration briefs and matching hand-drawn plate prompts for the full plant registry."),
]

REPLACEMENTS = {
    "🌍": "[Indoor Sow]",
    "🌿": "[Direct Sow]",
    "🌾": "[Harvest]",
    "🌸": "[Bloom]",
    "❄": "[Frost Risk]",
    "✄": "[Prune/Deadhead]",
    "🍅": "[Plant Bulb/Tuber]",
    "🌲": "[Overwinter/Mulch]",
    "💡": "[Tips]",
    "📖": "[Guide]",
    "📌": "[Legend]",
    "🏞": "[Climate]",
    "✓": "-",
    "·": "-",
    "–": "-",
    "—": "-",
    "“": '"',
    "”": '"',
    "’": "'",
    " ": " ",
}


def register_font(font_name: str, regular_path: Path, bold_path: Path | None = None) -> tuple[str, str]:
    pdfmetrics.registerFont(TTFont(font_name, str(regular_path)))
    if bold_path and bold_path.exists():
        bold_name = f"{font_name}Bold"
        pdfmetrics.registerFont(TTFont(bold_name, str(bold_path)))
        return font_name, bold_name
    return font_name, font_name


def register_fonts() -> dict[str, str]:
    families = [
        ("BookDisplay", Path("C:/Windows/Fonts/pala.ttf"), Path("C:/Windows/Fonts/palab.ttf")),
        ("BookDisplay", Path("C:/Windows/Fonts/georgia.ttf"), Path("C:/Windows/Fonts/georgiab.ttf")),
        ("BookDisplay", Path("C:/Windows/Fonts/constan.ttf"), Path("C:/Windows/Fonts/constanb.ttf")),
        ("BookDisplay", Path("C:/Windows/Fonts/times.ttf"), Path("C:/Windows/Fonts/timesbd.ttf")),
    ]
    for family_name, regular_path, bold_path in families:
        if regular_path.exists():
            display_regular, display_bold = register_font(family_name, regular_path, bold_path)
            return {
                "display": display_regular,
                "display_bold": display_bold,
                "body": display_regular,
                "body_bold": display_bold,
            }
    return {
        "display": "Times-Roman",
        "display_bold": "Times-Bold",
        "body": "Times-Roman",
        "body_bold": "Times-Bold",
    }


def sanitize(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraph_text(text: str) -> str:
    return escape(text, {'"': '&quot;'})


def normalize_key(text: str) -> str:
    return re.sub(r"[^A-Z0-9]+", "_", text.upper()).strip("_")


def load_sections(base_dir: Path) -> list[dict[str, str]]:
    sections: list[dict[str, str]] = []
    for title, file_name, deck in SOURCE_FILES:
        text = sanitize((base_dir / file_name).read_text(encoding="utf-8"))
        sections.append({"title": title, "file_name": file_name, "deck": deck, "text": text})
    return sections


def compile_markdown(base_dir: Path, sections: list[dict[str, str]]) -> str:
    blocks = [f"# {TITLE}", "", SUBTITLE, ""]
    for section in sections:
        blocks.extend([f"# {section['title']}", "", section["text"], ""])
    compiled = "\n".join(blocks).strip() + "\n"
    (base_dir / OUTPUT_MD).write_text(compiled, encoding="utf-8")
    return compiled


def build_styles(fonts: dict[str, str]) -> dict[str, ParagraphStyle]:
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            "CoverTitle",
            parent=styles["Title"],
            fontName=fonts["display_bold"],
            fontSize=23,
            leading=27,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#243126"),
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            "CoverSub",
            parent=styles["Normal"],
            fontName=fonts["body"],
            fontSize=10,
            leading=13,
            alignment=TA_CENTER,
            textColor=MUTED_COLOR,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            "FrontMatterHeading",
            parent=styles["Heading1"],
            fontName=fonts["display_bold"],
            fontSize=16,
            leading=20,
            alignment=TA_CENTER,
            textColor=ACCENT_COLOR,
            spaceAfter=10,
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionKicker",
            parent=styles["Normal"],
            fontName=fonts["body_bold"],
            fontSize=8.5,
            leading=10,
            alignment=TA_CENTER,
            textColor=MUTED_COLOR,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionTitle",
            parent=styles["Heading1"],
            fontName=fonts["display_bold"],
            fontSize=19,
            leading=23,
            alignment=TA_CENTER,
            textColor=colors.HexColor("#233628"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "SectionDeck",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=10,
            leading=14,
            alignment=TA_CENTER,
            textColor=MUTED_COLOR,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            "H1",
            parent=styles["Heading1"],
            fontName=fonts["display_bold"],
            fontSize=16,
            leading=20,
            spaceBefore=14,
            spaceAfter=6,
            textColor=colors.HexColor("#223528"),
        )
    )
    styles.add(
        ParagraphStyle(
            "H2",
            parent=styles["Heading2"],
            fontName=fonts["display_bold"],
            fontSize=12.5,
            leading=15,
            spaceBefore=11,
            spaceAfter=4,
            textColor=ACCENT_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            "H3",
            parent=styles["Heading3"],
            fontName=fonts["body_bold"],
            fontSize=10,
            leading=12.5,
            spaceBefore=8,
            spaceAfter=3,
            textColor=INK_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            "Lead",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=10.8,
            leading=15,
            alignment=TA_JUSTIFY,
            textColor=INK_COLOR,
            spaceAfter=7,
        )
    )
    styles.add(
        ParagraphStyle(
            "Body",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=9.2,
            leading=13.2,
            alignment=TA_JUSTIFY,
            textColor=INK_COLOR,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            "BulletItem",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=9.1,
            leading=12.7,
            leftIndent=14,
            firstLineIndent=-8,
            spaceAfter=2,
            textColor=INK_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            "Caption",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=8,
            leading=10,
            alignment=TA_CENTER,
            textColor=MUTED_COLOR,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            "TocEntry",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=10,
            leading=13,
            textColor=INK_COLOR,
            spaceAfter=4,
        )
    )
    return styles


def make_cover_image(image_path: Path, max_width: float, max_height: float) -> RLImage:
    cover = ImageReader(str(image_path))
    image_width, image_height = cover.getSize()
    scale = min(max_width / image_width, max_height / image_height)
    flowable = RLImage(str(image_path), width=image_width * scale, height=image_height * scale)
    flowable.hAlign = "CENTER"
    return flowable


def make_local_image(image_path: Path, max_width: float, max_height: float) -> RLImage:
    image_reader = ImageReader(str(image_path))
    image_width, image_height = image_reader.getSize()
    scale = min(max_width / image_width, max_height / image_height)
    flowable = RLImage(str(image_path), width=image_width * scale, height=image_height * scale)
    flowable.hAlign = "CENTER"
    return flowable


def load_plant_illustrations(base_dir: Path) -> dict[str, Path]:
    illustrations_dir = base_dir / PLANT_ILLUSTRATIONS_DIR
    if not illustrations_dir.exists():
        return {}

    illustration_map: dict[str, Path] = {}
    for path in illustrations_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in PLANT_ILLUSTRATION_EXTENSIONS:
            continue
        key = normalize_key(path.stem)
        if key and key not in illustration_map:
            illustration_map[key] = path
    return illustration_map


def add_cover(story: list, base_dir: Path, doc_width: float, doc_height: float) -> None:
    cover_path = base_dir / COVER_IMAGE
    if not cover_path.exists():
        raise FileNotFoundError(f"Missing required cover image: {cover_path}")
    story.append(make_cover_image(cover_path, doc_width, doc_height))
    story.append(PageBreak())


def add_front_matter(story: list, styles: dict[str, ParagraphStyle], sections: list[dict[str, str]]) -> None:
    story.append(Paragraph("Contents", styles["FrontMatterHeading"]))
    story.append(Paragraph("This original reference brings together Errington calendar evidence, an attributed regional pollinator summary, a plant catalog, and illustration briefs. Source scope and unresolved conflicts are identified in the handbook.", styles["Lead"]))
    for index, section in enumerate(sections, 1):
        story.append(Paragraph(f"{index}. {paragraph_text(section['title'])}", styles["TocEntry"]))
        story.append(Paragraph(paragraph_text(section["deck"]), styles["Caption"]))
    story.append(PageBreak())


def add_section_opener(
    story: list,
    styles: dict[str, ParagraphStyle],
    section: dict[str, str],
) -> None:
    story.append(Spacer(1, 0.55 * inch))
    story.append(Paragraph("Errington Encyclopedia", styles["SectionKicker"]))
    story.append(Paragraph(paragraph_text(section["title"]), styles["SectionTitle"]))
    story.append(Paragraph(paragraph_text(section["deck"]), styles["SectionDeck"]))
    story.append(PageBreak())


def add_plant_illustration(
    story: list,
    styles: dict[str, ParagraphStyle],
    image_path: Path,
    doc_width: float,
) -> None:
    story.append(Spacer(1, 0.1 * inch))
    story.append(make_local_image(image_path, doc_width * 0.82, 2.45 * inch))
    story.append(Spacer(1, 0.05 * inch))
    story.append(Paragraph(f"Scientific illustration asset: {paragraph_text(image_path.name)}", styles["Caption"]))


def add_markdown_lines(
    story: list,
    styles: dict[str, ParagraphStyle],
    section_title: str,
    text: str,
    plant_illustrations: dict[str, Path],
    doc_width: float,
) -> None:
    first_body = True
    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped:
            story.append(Spacer(1, 0.05 * inch))
            continue
        if stripped.startswith("# "):
            story.append(Paragraph(paragraph_text(stripped[2:].strip()), styles["H1"]))
            first_body = True
            continue
        if stripped.startswith("## "):
            story.append(Paragraph(paragraph_text(stripped[3:].strip()), styles["H2"]))
            first_body = True
            continue
        if stripped.startswith("### "):
            heading_text = stripped[4:].strip()
            story.append(Paragraph(paragraph_text(heading_text), styles["H3"]))
            if section_title == "Plant Catalog":
                image_path = plant_illustrations.get(normalize_key(heading_text))
                if image_path is not None:
                    add_plant_illustration(story, styles, image_path, doc_width)
            continue
        if stripped.startswith("#### "):
            story.append(Paragraph(paragraph_text(stripped[5:].strip()), styles["H3"]))
            continue
        if stripped.startswith("- "):
            story.append(Paragraph("• " + paragraph_text(stripped[2:].strip()), styles["BulletItem"]))
            continue
        if stripped.startswith("  - "):
            story.append(Paragraph("◦ " + paragraph_text(stripped[4:].strip()), styles["BulletItem"]))
            continue
        if re.match(r"^\d+\.\s", stripped):
            story.append(Paragraph(paragraph_text(stripped), styles["BulletItem"]))
            continue
        style_name = "Lead" if first_body else "Body"
        story.append(Paragraph(paragraph_text(stripped), styles[style_name]))
        first_body = False


def draw_cover(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(PAPER_COLOR)
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#927f61"))
    canvas.setLineWidth(1.2)
    canvas.rect(0.35 * inch, 0.35 * inch, doc.pagesize[0] - 0.7 * inch, doc.pagesize[1] - 0.7 * inch, fill=0, stroke=1)
    canvas.setLineWidth(0.4)
    canvas.rect(0.5 * inch, 0.5 * inch, doc.pagesize[0] - inch, doc.pagesize[1] - inch, fill=0, stroke=1)
    canvas.restoreState()


def draw_page_chrome(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(PAPER_COLOR)
    canvas.rect(0, 0, doc.pagesize[0], doc.pagesize[1], fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#cbb99b"))
    canvas.setLineWidth(0.5)
    canvas.line(doc.leftMargin, doc.pagesize[1] - 0.45 * inch, doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 0.45 * inch)
    canvas.line(doc.leftMargin, 0.48 * inch, doc.pagesize[0] - doc.rightMargin, 0.48 * inch)
    canvas.setFillColor(MUTED_COLOR)
    canvas.setFont("Times-Italic", 7.5)
    canvas.drawCentredString(doc.pagesize[0] / 2, doc.pagesize[1] - 0.35 * inch, "Errington Gardening Encyclopedia")
    canvas.setFillColor(INK_COLOR)
    canvas.setFont("Times-Roman", 8)
    canvas.drawCentredString(doc.pagesize[0] / 2, 0.31 * inch, str(canvas.getPageNumber()))
    canvas.restoreState()


def build_pdf(base_dir: Path) -> Path:
    fonts = register_fonts()
    styles = build_styles(fonts)
    sections = load_sections(base_dir)
    compile_markdown(base_dir, sections)
    plant_illustrations = load_plant_illustrations(base_dir)
    output_path = base_dir / OUTPUT_PDF
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=BOOK_PAGE_SIZE,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title=TITLE,
        author="GitHub Copilot",
    )
    doc_width = doc.width
    story: list = []
    add_cover(story, base_dir, doc.width, doc.height)
    add_front_matter(story, styles, sections)
    for index, section in enumerate(sections):
        add_section_opener(story, styles, section)
        add_markdown_lines(story, styles, section["title"], section["text"], plant_illustrations, doc_width)
        if index < len(sections) - 1:
            story.append(PageBreak())
    doc.build(story, onFirstPage=draw_cover, onLaterPages=draw_page_chrome)
    return output_path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_path = build_pdf(base_dir)
    print(output_path.name)


if __name__ == "__main__":
    main()