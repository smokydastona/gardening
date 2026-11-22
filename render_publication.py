from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image, ImageDraw


THUMBNAIL_SIZE = (280, 420)
TILE_SIZE = (300, 450)
SHEET_COLUMNS = 4
PAGES_PER_SHEET = 28
RENDER_SCALE = 1.0


def render_publication(pdf_path: Path, output_dir: Path) -> tuple[int, list[Path]]:
    if not pdf_path.is_file():
        raise FileNotFoundError(f"Publication PDF is missing: {pdf_path}")

    digest = hashlib.sha256(pdf_path.read_bytes()).hexdigest()[:12]
    target_dir = output_dir / digest
    page_dir = target_dir / "rendered_pages"
    page_dir.mkdir(parents=True, exist_ok=True)
    document = pdfium.PdfDocument(str(pdf_path))
    if len(document) == 0:
        raise ValueError(f"Publication PDF has no pages: {pdf_path}")

    contact_tiles: list[Image.Image] = []
    for index in range(len(document)):
        page = document[index]
        rendered = page.render(scale=RENDER_SCALE).to_pil().convert("RGB")
        rendered.save(page_dir / f"page-{index + 1:03d}.png", format="PNG")

        thumbnail = rendered.copy()
        thumbnail.thumbnail(THUMBNAIL_SIZE)
        tile = Image.new("RGB", TILE_SIZE, "white")
        tile.paste(
            thumbnail,
            ((TILE_SIZE[0] - thumbnail.width) // 2, 22),
        )
        ImageDraw.Draw(tile).text((8, 4), f"Page {index + 1}", fill="black")
        contact_tiles.append(tile)

    contact_sheets: list[Path] = []
    for start in range(0, len(contact_tiles), PAGES_PER_SHEET):
        batch = contact_tiles[start : start + PAGES_PER_SHEET]
        row_count = (len(batch) + SHEET_COLUMNS - 1) // SHEET_COLUMNS
        sheet = Image.new(
            "RGB",
            (SHEET_COLUMNS * TILE_SIZE[0], row_count * TILE_SIZE[1]),
            "#d7d9d4",
        )
        for offset, tile in enumerate(batch):
            sheet.paste(
                tile,
                ((offset % SHEET_COLUMNS) * TILE_SIZE[0], (offset // SHEET_COLUMNS) * TILE_SIZE[1]),
            )
        sheet_path = target_dir / f"contact-{start + 1:03d}-{start + len(batch):03d}.jpg"
        sheet.save(sheet_path, format="JPEG", quality=90)
        contact_sheets.append(sheet_path)

    if len(list(page_dir.glob("page-*.png"))) != len(document):
        raise RuntimeError("Not every publication page was rendered.")
    return len(document), contact_sheets


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Render every publication page and make review contact sheets."
    )
    parser.add_argument(
        "--pdf",
        type=Path,
        default=Path(__file__).resolve().parent / "Errington_Gardening_Encyclopedia.pdf",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parent / "build" / "pdf_qa",
    )
    args = parser.parse_args()
    pages, sheets = render_publication(args.pdf, args.output_dir)
    print(f"Rendered all {pages} pages. Contact sheets:")
    for path in sheets:
        print(path)


if __name__ == "__main__":
    main()
