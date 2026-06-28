from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR


MONTHS = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
IGNORE_TEXT = {
    "ERRINGTON8BPLANTINGCALENDAR",
    "LASTEXPECTEDFROSTDATE",
    "FIRSTEXPECTEDFROSTDATE",
    "APRIL15",
    "OCTOER15",
    "OCTOBER15",
    "OCTOBERIS",
    "REDSTARTSEEDSINDOORS",
    "YELLOWTRANSPLANTOUTDOORS",
    "DIRECTSOWHARVEST",
    "DIRECTSOW",
    "BLOOM",
    "DORMANTDIVIDE",
    "EDIBLECROPS",
    "ANNUALS",
    "PERENNIALS",
    "BULBS",
    "ORNAMENTALS",
    "NOTES",
    *MONTHS,
}


@dataclass
class OcrItem:
    text: str
    norm: str
    x1: int
    y1: int
    x2: int
    y2: int


def normalize(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def parse_ocr(image_path: Path) -> list[OcrItem]:
    engine = RapidOCR()
    result, _ = engine(str(image_path))
    items: list[OcrItem] = []
    if not result:
        return items
    for box, text, _score in result:
        xs = [int(point[0]) for point in box]
        ys = [int(point[1]) for point in box]
        items.append(
            OcrItem(
                text=text,
                norm=normalize(text),
                x1=min(xs),
                y1=min(ys),
                x2=max(xs),
                y2=max(ys),
            )
        )
    return items


def find_month_items(items: list[OcrItem]) -> list[OcrItem]:
    month_map = {item.norm: item for item in items if item.norm in MONTHS}
    ordered = [month_map[m] for m in MONTHS if m in month_map]
    if len(ordered) == 12:
        return ordered

    if len(ordered) == 11:
        missing = [month for month in MONTHS if month not in month_map]
        if len(missing) == 1:
            gap_values = []
            widths = []
            for earlier, later in zip(ordered, ordered[1:]):
                earlier_center = int((earlier.x1 + earlier.x2) / 2)
                later_center = int((later.x1 + later.x2) / 2)
                gap_values.append(later_center - earlier_center)
                widths.append(earlier.x2 - earlier.x1)
            average_gap = int(sum(gap_values) / len(gap_values)) if gap_values else 80
            average_width = int(sum(widths) / len(widths)) if widths else 55
            missing_month = missing[0]
            month_index = MONTHS.index(missing_month)

            if month_index > 0 and MONTHS[month_index - 1] in month_map:
                previous = month_map[MONTHS[month_index - 1]]
                center = int((previous.x1 + previous.x2) / 2) + average_gap
                y1 = previous.y1
                y2 = previous.y2
            elif month_index + 1 < len(MONTHS) and MONTHS[month_index + 1] in month_map:
                following = month_map[MONTHS[month_index + 1]]
                center = int((following.x1 + following.x2) / 2) - average_gap
                y1 = following.y1
                y2 = following.y2
            else:
                center = 0
                y1 = 0
                y2 = 0

            synthetic = OcrItem(
                text=missing_month,
                norm=missing_month,
                x1=int(center - average_width / 2),
                y1=y1,
                x2=int(center + average_width / 2),
                y2=y2,
            )
            month_map[missing_month] = synthetic
            return [month_map[m] for m in MONTHS if m in month_map]

    return ordered


def month_bounds(month_items: list[OcrItem], image_width: int) -> list[tuple[str, int, int]]:
    centers = [int((item.x1 + item.x2) / 2) for item in month_items]
    bounds: list[tuple[str, int, int]] = []
    for index, item in enumerate(month_items):
        if index == 0:
            left = max(0, item.x1 - 20)
        else:
            left = int((centers[index - 1] + centers[index]) / 2)
        if index == len(month_items) - 1:
            right = min(image_width, item.x2 + 20)
        else:
            right = int((centers[index] + centers[index + 1]) / 2)
        bounds.append((item.norm, left, right))
    return bounds


def detect_rows(items: list[OcrItem], month_header_y: int) -> list[OcrItem]:
    rows = []
    for item in items:
        if item.x1 >= 260:
            continue
        if item.y1 <= month_header_y:
            continue
        if item.norm in IGNORE_TEXT:
            continue
        if item.norm.endswith("DAYS") or item.norm.endswith("MONTHS"):
            continue
        if len(item.norm) <= 2:
            continue
        rows.append(item)
    rows.sort(key=lambda item: (item.y1, item.x1))
    return rows


def color_counts(image: np.ndarray, y1: int, y2: int, x1: int, x2: int) -> dict[str, int]:
    cell = image[y1:y2, x1:x2]
    hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    sat = hsv[:, :, 1]
    val = hsv[:, :, 2]

    red = ((((hue < 10) | (hue > 170)) & (sat > 70) & (val > 70))).sum()
    yellow = (((hue > 15) & (hue < 42) & (sat > 70) & (val > 70))).sum()
    green = (((hue > 42) & (hue < 100) & (sat > 70) & (val > 70))).sum()
    blue = (((hue > 100) & (hue < 140) & (sat > 70) & (val > 70))).sum()
    gray = (((sat < 35) & (val > 90) & (val < 220))).sum()
    return {
        "red": int(red),
        "yellow": int(yellow),
        "green": int(green),
        "blue": int(blue),
        "gray": int(gray),
    }


def write_ocr_tsv(output_path: Path, items: list[OcrItem]) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["text", "normalized", "x1", "y1", "x2", "y2"])
        for item in sorted(items, key=lambda current: (current.y1, current.x1)):
            writer.writerow([item.text, item.norm, item.x1, item.y1, item.x2, item.y2])


def write_row_colors(output_path: Path, rows: list[OcrItem], month_spans: list[tuple[str, int, int]], image: np.ndarray) -> None:
    with output_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow([
            "row_text",
            "row_normalized",
            "y1",
            "y2",
            "month",
            "x1",
            "x2",
            "red_count",
            "yellow_count",
            "green_count",
            "blue_count",
            "gray_count",
        ])

        for index, row in enumerate(rows):
            top = max(0, row.y1 - 4)
            bottom = min(image.shape[0], (rows[index + 1].y1 - 2) if index + 1 < len(rows) else row.y2 + 24)
            for month, left, right in month_spans:
                counts = color_counts(image, top, bottom, left, right)
                writer.writerow([
                    row.text,
                    row.norm,
                    top,
                    bottom,
                    month,
                    left,
                    right,
                    counts["red"],
                    counts["yellow"],
                    counts["green"],
                    counts["blue"],
                    counts["gray"],
                ])


def write_summary(output_path: Path, rows: list[OcrItem], month_spans: list[tuple[str, int, int]]) -> None:
    summary = {
        "months": [month for month, _left, _right in month_spans],
        "rows": [
            {
                "text": row.text,
                "normalized": row.norm,
                "x1": row.x1,
                "y1": row.y1,
                "x2": row.x2,
                "y2": row.y2,
            }
            for row in rows
        ],
    }
    output_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def process_chart(base_dir: Path, image_name: str, prefix: str) -> None:
    image_path = base_dir / image_name
    items = parse_ocr(image_path)
    image = cv2.imread(str(image_path))
    month_items = find_month_items(items)
    if len(month_items) != 12:
        raise RuntimeError(f"Expected 12 month headers in {image_name}, found {len(month_items)}")

    month_header_y = max(item.y2 for item in month_items)
    rows = detect_rows(items, month_header_y)
    spans = month_bounds(month_items, image.shape[1])

    write_ocr_tsv(base_dir / f"{prefix}_ocr.tsv", items)
    write_row_colors(base_dir / f"{prefix}_row_colors.csv", rows, spans, image)
    write_summary(base_dir / f"{prefix}_summary.json", rows, spans)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    process_chart(base_dir, "Planting Calander-Crops.png", "crop_calendar")
    process_chart(base_dir, "Planting Calander-Ornamentals.png", "ornamental_calendar")


if __name__ == "__main__":
    main()