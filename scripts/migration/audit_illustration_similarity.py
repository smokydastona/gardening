from __future__ import annotations

import argparse
import csv
import hashlib
import io
import math
import statistics
import subprocess
from collections import Counter
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
REF = "origin/illustration-assets"
OUTPUT = ROOT / "reports" / "ILLUSTRATION_SIMILARITY_AUDIT.csv"
FIELDS = (
    "source_ref",
    "source_commit",
    "source_path",
    "git_blob",
    "sha256",
    "width",
    "height",
    "perceptual_hash",
    "nearest_candidate",
    "nearest_hamming_distance",
    "near_duplicate_candidates_at_threshold",
    "approval_status",
)


def _git(*args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    return result.stdout.rstrip("\r\n") if text else result.stdout


def _dct_basis() -> list[list[float]]:
    size = 32
    basis = []
    for frequency in range(size):
        scale = math.sqrt((1.0 if frequency == 0 else 2.0) / size)
        basis.append(
            [
                scale
                * math.cos(
                    math.pi * (2 * position + 1) * frequency / (2 * size)
                )
                for position in range(size)
            ]
        )
    return basis


def _phash(image_bytes: bytes) -> tuple[int, int, int]:
    with Image.open(io.BytesIO(image_bytes)) as source:
        width, height = source.size
        pixels = list(
            source.convert("L")
            .resize((32, 32), Image.Resampling.LANCZOS)
            .get_flattened_data()
        )
    basis = _dct_basis()
    row_transform = [
        [
            sum(pixels[y * 32 + x] * basis[frequency][x] for x in range(32))
            for frequency in range(8)
        ]
        for y in range(32)
    ]
    coefficients = [
        [
            sum(
                row_transform[y][x_frequency] * basis[y_frequency][y]
                for y in range(32)
            )
            for x_frequency in range(8)
        ]
        for y_frequency in range(8)
    ]
    flattened = [value for row in coefficients for value in row]
    median = statistics.median(flattened[1:])
    value = 0
    for coefficient in flattened:
        value = (value << 1) | int(coefficient > median)
    return value, width, height


def _distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def audit(ref: str, threshold: int) -> tuple[list[dict[str, str]], int, int]:
    commit = str(_git("rev-parse", ref))
    tree = str(_git("ls-tree", "-r", "-l", "--full-tree", ref))
    assets = []
    for line in tree.splitlines():
        metadata, path = line.split("\t", 1)
        mode, object_type, blob, _size = metadata.split(" ", 3)
        if (
            object_type != "blob"
            or not path.startswith("plant_illustrations/")
            or Path(path).suffix.casefold() not in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
        ):
            continue
        image_bytes = _git("cat-file", "blob", blob, text=False)
        assert isinstance(image_bytes, bytes)
        phash, width, height = _phash(image_bytes)
        assets.append(
            {
                "source_ref": ref,
                "source_commit": commit,
                "source_path": path,
                "git_blob": blob,
                "sha256": hashlib.sha256(image_bytes).hexdigest(),
                "width": str(width),
                "height": str(height),
                "perceptual_hash_value": phash,
            }
        )

    hashes = Counter(row["sha256"] for row in assets)
    rows = []
    near_pair_count = 0
    for index, asset in enumerate(assets):
        distances = [
            (_distance(asset["perceptual_hash_value"], other["perceptual_hash_value"]), other["source_path"])
            for other_index, other in enumerate(assets)
            if other_index != index and other["sha256"] != asset["sha256"]
        ]
        nearest_distance, nearest_path = min(distances, default=("", ""))
        near_paths = sorted(
            path
            for distance, path in distances
            if distance <= threshold
        )
        near_pair_count += len(near_paths)
        rows.append(
            {
                "source_ref": ref,
                "source_commit": commit,
                "source_path": asset["source_path"],
                "git_blob": asset["git_blob"],
                "sha256": asset["sha256"],
                "width": asset["width"],
                "height": asset["height"],
                "perceptual_hash": f"{asset['perceptual_hash_value']:016x}",
                "nearest_candidate": nearest_path,
                "nearest_hamming_distance": str(nearest_distance),
                "near_duplicate_candidates_at_threshold": "|".join(near_paths),
                "approval_status": "not-approved; similarity is not identity review",
            }
        )
    exact_duplicate_groups = sum(count > 1 for count in hashes.values())
    return rows, exact_duplicate_groups, near_pair_count // 2


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Find visual-similarity candidates in an illustration branch."
    )
    parser.add_argument("--ref", default=REF)
    parser.add_argument("--threshold", type=int, default=5)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    if not 0 <= args.threshold <= 64:
        parser.error("--threshold must be between 0 and 64")
    rows, exact_groups, near_pairs = audit(args.ref, args.threshold)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(
        f"Audited {len(rows)} candidates; {exact_groups} exact-duplicate groups; "
        f"{near_pairs} possible near-duplicate pairs at Hamming distance "
        f"≤{args.threshold}. Results are candidates for human inspection only."
    )
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
