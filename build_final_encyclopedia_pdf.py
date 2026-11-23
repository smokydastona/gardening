from __future__ import annotations

import html
from pathlib import Path
import re
from urllib.parse import urlsplit

import mistune
import reportlab
from reportlab import rl_config
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Image as RLImage
from reportlab.platypus import (
    HRFlowable,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.tableofcontents import TableOfContents

from illustration_assets import approved_assets, keyify


TITLE = "Errington Gardening Encyclopedia"
SUBTITLE = "Source transcriptions and working plant registry for Errington, BC"
VERSION = "0.2.0"
PUBLICATION_DATE = "2026-11-22"
OUTPUT_PDF = "Errington_Gardening_Encyclopedia.pdf"
OUTPUT_MD = "Errington_Gardening_Encyclopedia_Compiled.md"
COVER_IMAGE = "cover.png"
PLANT_ILLUSTRATIONS_DIR = "plant_illustrations"
PLANT_ILLUSTRATION_EXTENSIONS = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".webp")
MONTH_NAMES = frozenset(
    (
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    )
)
BOOK_PAGE_SIZE = (6.125 * inch, 9.25 * inch)
PAPER_COLOR = colors.HexColor("#f6f0e2")
INK_COLOR = colors.HexColor("#2d2a26")
ACCENT_COLOR = colors.HexColor("#51664e")
MUTED_COLOR = colors.HexColor("#7b756c")

SOURCE_FILES = [
    ("Core Handbook", "ERRINGTON_GARDENING_ENCYCLOPEDIA_MANUSCRIPT.md", "Gardening foundations, Errington context, and source limitations."),
    ("Monthly Reference", "ERRINGTON_MONTHLY_REFERENCE.md", "Source calendar transcriptions grouped by month and labeled for review."),
    ("Plant Registry", "ERRINGTON_PLANT_CATALOG.md", "Stable plant records and independent verification states."),
    ("Complete Supplement", "ERRINGTON_COMPLETE_SUPPLEMENT.md", "137 plant profile shells, 36 educational figures, and 18 worked examples."),
    ("Source and Verification Policy", "docs/SOURCE_POLICY.md", "Source hierarchy, evidence types, and publication status."),
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
    " ": " ",
}

MARKDOWN = mistune.create_markdown(
    renderer="ast",
    plugins=["table", "strikethrough", "url"],
)


def register_font(font_name: str, regular_path: Path, bold_path: Path | None = None) -> tuple[str, str]:
    pdfmetrics.registerFont(TTFont(font_name, str(regular_path)))
    if bold_path and bold_path.exists():
        bold_name = f"{font_name}Bold"
        pdfmetrics.registerFont(TTFont(bold_name, str(bold_path)))
        return font_name, bold_name
    return font_name, font_name


def register_fonts() -> dict[str, str]:
    font_dir = Path(__file__).resolve().parent / "fonts"
    regular = "ReenieBeanie"
    pdfmetrics.registerFont(TTFont(regular, str(font_dir / "ReenieBeanie.ttf")))
    pdfmetrics.registerFont(TTFont("BookText", str(font_dir / "ReenieBeanie.ttf")))
    pdfmetrics.registerFont(TTFont("BookItalic", str(font_dir / "ReenieBeanie.ttf")))
    pdfmetrics.registerFont(TTFont("BookBoldItalic", str(font_dir / "ReenieBeanie.ttf")))
    pdfmetrics.registerFontFamily(
        regular,
        normal=regular,
        bold=regular,
        italic=regular,
        boldItalic=regular,
    )
    return {
        "display": regular,
        "display_bold": regular,
        "body": "Times-Roman",
        "body_bold": "Times-Bold",
    }


def sanitize(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def paragraph_text(text: str) -> str:
    return html.escape(text, quote=True)


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
            keepWithNext=True,
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
            keepWithNext=True,
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
            keepWithNext=True,
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
            "TocLead",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=9,
            leading=11,
            textColor=INK_COLOR,
            spaceAfter=6,
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
            fontSize=8.5,
            leading=10,
            textColor=INK_COLOR,
            spaceAfter=1,
        )
    )
    styles.add(
        ParagraphStyle(
            "TocSubEntry",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=7.8,
            leading=9,
            leftIndent=16,
            textColor=MUTED_COLOR,
            spaceAfter=0,
        )
    )
    styles.add(
        ParagraphStyle(
            "TableHeader",
            parent=styles["BodyText"],
            fontName=fonts["body_bold"],
            fontSize=7.8,
            leading=9.6,
            textColor=ACCENT_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            "TableCell",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=7.7,
            leading=9.5,
            textColor=INK_COLOR,
        )
    )
    styles.add(
        ParagraphStyle(
            "Quote",
            parent=styles["BodyText"],
            fontName=fonts["body"],
            fontSize=9,
            leading=12,
            leftIndent=16,
            rightIndent=12,
            textColor=ACCENT_COLOR,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            "CodeBlock",
            parent=styles["BodyText"],
            fontName="Courier",
            fontSize=7.5,
            leading=9,
            leftIndent=10,
            backColor=colors.HexColor("#f0eee7"),
            spaceAfter=5,
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
    manifest_path = illustrations_dir / "illustration_manifest.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Required illustration manifest is missing: {manifest_path}")
    import csv

    reviewed_assets = approved_assets(illustrations_dir)
    illustration_map: dict[str, Path] = {}
    seen_plant_ids: set[str] = set()
    with manifest_path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("approval_status") != "approved":
                continue
            plant_id = row.get("plant_id", "").strip()
            if not plant_id or plant_id in seen_plant_ids:
                raise ValueError(f"Missing or duplicate approved illustration plant ID: {plant_id!r}")
            seen_plant_ids.add(plant_id)
            filename = row.get("filename", "")
            image_name = Path(filename)
            if image_name.name != filename or image_name.suffix.lower() not in PLANT_ILLUSTRATION_EXTENSIONS:
                raise ValueError(f"Invalid approved illustration filename: {filename!r}")
            image_path = illustrations_dir / image_name
            if not image_path.is_file():
                raise FileNotFoundError(
                    f"Approved illustration for {plant_id} is missing: {image_path}"
                )
            if reviewed_assets.get(keyify(image_name.stem)) != image_path:
                raise ValueError(
                    f"Approved illustration for {plant_id} lacks valid matching evidence "
                    "and human-review sidecar."
                )
            expected_id = f"plant-{keyify(image_name.stem).lower().replace('_', '-')}"
            if plant_id != expected_id:
                raise ValueError(
                    f"Approved illustration {filename} does not match plant ID {plant_id}."
                )
            illustration_map[plant_id] = image_path
    return illustration_map


def add_cover(story: list, base_dir: Path, doc_width: float, doc_height: float) -> None:
    cover_path = base_dir / COVER_IMAGE
    if not cover_path.exists():
        raise FileNotFoundError(f"Missing required cover image: {cover_path}")
    story.append(make_cover_image(cover_path, doc_width, doc_height))
    story.append(PageBreak())


def add_front_matter(story: list, styles: dict[str, ParagraphStyle]) -> None:
    story.append(
        Paragraph(
            f"Version {VERSION} · {PUBLICATION_DATE} · Errington Gardening Encyclopedia project",
            styles["Caption"],
        )
    )
    story.append(
        Paragraph(
            "Working reference, not approved for publication. Calendar entries are source "
            "transcriptions; taxonomy, profiles, and local timing remain unverified unless noted.",
            styles["TocLead"],
        )
    )
    story.append(Paragraph("Contents", styles["FrontMatterHeading"]))
    toc = TableOfContents()
    toc.levelStyles = [
        styles["TocEntry"],
        styles["TocSubEntry"],
    ]
    toc.dotsMinLevel = 0
    story.append(toc)
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
    story.append(make_local_image(image_path, doc_width * 0.95, 5.5 * inch))
    story.append(Spacer(1, 0.05 * inch))
    story.append(Paragraph(f"Scientific illustration asset: {paragraph_text(image_path.name)}", styles["Caption"]))


def add_markdown_lines(
    story: list,
    styles: dict[str, ParagraphStyle],
    section_title: str,
    text: str,
    plant_illustrations: dict[str, Path],
    doc_width: float,
    base_dir: Path,
) -> None:
    def markdown_image(node: dict) -> tuple[RLImage, str]:
        image_url = node.get("attrs", {}).get("url", "")
        image_parts = urlsplit(image_url)
        if image_parts.scheme or image_parts.netloc:
            raise ValueError(f"External Markdown images are not supported in publications: {image_url}")
        image_path = (base_dir / image_parts.path).resolve()
        if not image_path.is_relative_to(base_dir.resolve()):
            raise ValueError(f"Markdown image path escapes the publication root: {image_url}")
        if not image_path.is_file():
            raise FileNotFoundError(f"Markdown image is missing: {image_path}")
        if "educational_figures" in image_path.parts:
            max_width, max_height = doc_width * 0.9, 3.5 * inch
        else:
            max_width, max_height = doc_width * 0.72, 4.2 * inch
        return make_local_image(image_path, max_width, max_height), inline(node.get("children", []))

    def inline(nodes: list[dict]) -> str:
        output = []
        for node in nodes:
            kind = node["type"]
            if kind in {"text", "inline_html"}:
                output.append(paragraph_text(node.get("raw", "")))
            elif kind in {"softbreak", "linebreak"}:
                output.append("<br/>")
            elif kind == "strong":
                output.append(f"<b>{inline(node.get('children', []))}</b>")
            elif kind == "emphasis":
                output.append(f"<i>{inline(node.get('children', []))}</i>")
            elif kind == "strikethrough":
                output.append(f"<strike>{inline(node.get('children', []))}</strike>")
            elif kind == "codespan":
                output.append(
                    f'<font name="Courier">{paragraph_text(node.get("raw", ""))}</font>'
                )
            elif kind == "link":
                target = paragraph_text(node.get("attrs", {}).get("url", ""))
                label = inline(node.get("children", []))
                if urlsplit(target).scheme in {"http", "https", "mailto"}:
                    output.append(f'<link href="{target}">{label}</link>')
                else:
                    output.append(label)
            elif kind == "image":
                output.append(inline(node.get("children", [])))
            else:
                output.append(inline(node.get("children", [])))
        return "".join(output)

    def paragraph(nodes: list[dict], style_name: str) -> Paragraph:
        return Paragraph(inline(nodes), styles[style_name])

    def paragraph_content(nodes: list[dict]) -> None:
        text_nodes: list[dict] = []
        for node in nodes:
            if node["type"] != "image":
                text_nodes.append(node)
                continue
            if text_nodes and inline(text_nodes).strip():
                story.append(paragraph(text_nodes, "Body"))
            text_nodes = []
            image, alt_text = markdown_image(node)
            story.append(Spacer(1, 0.04 * inch))
            story.append(image)
            if alt_text.strip():
                story.append(Paragraph(paragraph_text(alt_text), styles["Caption"]))
            story.append(Spacer(1, 0.06 * inch))
        if text_nodes and inline(text_nodes).strip():
            story.append(paragraph(text_nodes, "Body"))

    def list_flowable(token: dict, depth: int = 0) -> ListFlowable:
        ordered = token.get("attrs", {}).get("ordered", False)
        items = []
        for item in token.get("children", []):
            child_flowables = []
            for child in item.get("children", []):
                if child["type"] in {"block_text", "paragraph"}:
                    child_flowables.append(paragraph(child.get("children", []), "BulletItem"))
                elif child["type"] == "list":
                    child_flowables.append(list_flowable(child, depth + 1))
                elif child["type"] == "block_code":
                    child_flowables.append(
                        Preformatted(child.get("raw", ""), styles["CodeBlock"])
                    )
            items.append(ListItem(child_flowables or [Spacer(1, 1)]))
        return ListFlowable(
            items,
            bulletType="1" if ordered else "bullet",
            leftIndent=16 + depth * 12,
            bulletFontName=styles["BulletItem"].fontName,
            bulletFontSize=8,
            bulletColor=ACCENT_COLOR,
            spaceAfter=5,
        )

    ast = MARKDOWN(text)
    for token in ast:
        kind = token["type"]
        if kind == "blank_line":
            continue
        if kind == "heading":
            level = token.get("attrs", {}).get("level", 1)
            style_name = "H1" if level == 1 else "H2" if level == 2 else "H3"
            heading_text = inline(token.get("children", []))
            heading = Paragraph(heading_text, styles[style_name])
            if (
                level == 2
                and section_title == "Monthly Reference"
                and heading_text in MONTH_NAMES
            ):
                heading._toc_level = 1
            story.append(heading)
            if level == 3 and section_title == "Plant Registry":
                plant_key = f"plant-{normalize_key(heading.getPlainText()).lower().replace('_', '-')}"
                image_path = plant_illustrations.get(plant_key)
                if image_path is not None:
                    add_plant_illustration(story, styles, image_path, doc_width)
        elif kind == "paragraph":
            paragraph_content(token.get("children", []))
        elif kind == "block_text":
            story.append(paragraph(token.get("children", []), "Body"))
        elif kind == "list":
            story.append(list_flowable(token))
        elif kind == "table":
            table_rows = []
            for row in token.get("children", []):
                if row["type"] not in {"table_head", "table_body"}:
                    continue
                for table_row in row.get("children", []):
                    table_rows.append(
                        [
                            paragraph(cell.get("children", []), "TableHeader" if cell.get("attrs", {}).get("head") else "TableCell")
                            for cell in table_row.get("children", [])
                        ]
                    )
            if table_rows:
                column_count = max(len(row) for row in table_rows)
                table = Table(
                    table_rows,
                    colWidths=[doc_width / column_count] * column_count,
                    repeatRows=1,
                    hAlign="LEFT",
                )
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e7eadf")),
                            ("TEXTCOLOR", (0, 0), (-1, 0), ACCENT_COLOR),
                            ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#cbb99b")),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                            ("LEFTPADDING", (0, 0), (-1, -1), 5),
                            ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                            ("TOPPADDING", (0, 0), (-1, -1), 4),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                        ]
                    )
                )
                story.append(table)
                story.append(Spacer(1, 0.08 * inch))
        elif kind == "block_quote":
            for child in token.get("children", []):
                if child["type"] == "paragraph":
                    story.append(paragraph(child.get("children", []), "Quote"))
        elif kind == "block_code":
            story.append(Preformatted(token.get("raw", ""), styles["CodeBlock"]))
        elif kind == "thematic_break":
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#cbb99b")))


class EncyclopediaDocument(SimpleDocTemplate):
    def afterFlowable(self, flowable) -> None:
        level = getattr(flowable, "_toc_level", None)
        if level is None or not isinstance(flowable, Paragraph):
            return
        title = flowable.getPlainText().strip()
        if not title:
            return
        key = getattr(flowable, "_bookmark_key", None)
        if key:
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=level, closed=level > 0)
            self.notify("TOCEntry", (level, title, self.page, key))


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
    canvas.setFont("BookItalic", 7.5)
    canvas.drawCentredString(doc.pagesize[0] / 2, doc.pagesize[1] - 0.35 * inch, "Errington Gardening Encyclopedia")
    canvas.setFillColor(INK_COLOR)
    canvas.setFont("BookText", 8)
    canvas.drawCentredString(doc.pagesize[0] / 2, 0.31 * inch, str(canvas.getPageNumber()))
    canvas.restoreState()


def build_pdf(base_dir: Path) -> Path:
    rl_config.invariant = 1
    fonts = register_fonts()
    styles = build_styles(fonts)
    sections = load_sections(base_dir)
    compile_markdown(base_dir, sections)
    plant_illustrations = load_plant_illustrations(base_dir)
    output_path = base_dir / OUTPUT_PDF
    doc = EncyclopediaDocument(
        str(output_path),
        pagesize=BOOK_PAGE_SIZE,
        rightMargin=0.62 * inch,
        leftMargin=0.62 * inch,
        topMargin=0.72 * inch,
        bottomMargin=0.72 * inch,
        title=TITLE,
        author="Errington Gardening Encyclopedia Editorial Project",
        subject="Working gardening reference for Errington, British Columbia",
        keywords="Errington, Vancouver Island, gardening, source-transcribed calendar",
    )
    doc_width = doc.width
    story: list = []
    add_cover(story, base_dir, doc.width, doc.height)
    add_front_matter(story, styles)
    heading_index = 0
    for index, section in enumerate(sections):
        section_heading = Paragraph(paragraph_text(section["title"]), styles["SectionTitle"])
        section_heading._toc_level = 0
        section_heading._bookmark_key = f"section-{index + 1}"
        add_section_opener(story, styles, section)
        story[-3] = section_heading
        add_markdown_lines(
            story,
            styles,
            section["title"],
            section["text"],
            plant_illustrations,
            doc_width,
            base_dir,
        )
        for flowable in story:
            if (
                isinstance(flowable, Paragraph)
                and hasattr(flowable, "_toc_level")
                and not hasattr(flowable, "_bookmark_key")
            ):
                heading_index += 1
                flowable._bookmark_key = f"heading-{heading_index}"
        if index < len(sections) - 1:
            story.append(PageBreak())
    doc.multiBuild(story, onFirstPage=draw_cover, onLaterPages=draw_page_chrome)
    return output_path


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    output_path = build_pdf(base_dir)
    print(output_path.name)


if __name__ == "__main__":
    main()