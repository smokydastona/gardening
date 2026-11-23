from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
INVENTORY_COLUMNS = (
    "ref",
    "path",
    "kind",
    "file_type",
    "size_bytes",
    "git_blob",
    "sha256",
    "last_modified_in_fetched_history",
    "classification",
    "duplicate_content_paths",
    "same_path_differs_between_refs",
)
MIGRATION_COLUMNS = (
    "path",
    "main_present",
    "illustration_branch_present",
    "main_sha256",
    "illustration_branch_sha256",
    "comparison",
    "proposed_destination",
    "disposition",
    "human_review_required",
)
MAIN_REF = "main"
ILLUSTRATION_REF = "origin/illustration-assets"
SOURCE_FILES = {
    "Errington BC Zone 8a Planting Calendar.pdf",
    "Planting Calander-Crops.png",
    "Planting Calander-Ornamentals.png",
}
REGISTRY_FILES = {
    "plant_registry.csv",
    "plant_registry_enriched.csv",
    "plant_verification_register.csv",
    "errington_calendar_entries.csv",
    "errington_calendar_entries.json",
    "calendar_actions.csv",
    "calendar_review.csv",
    "claims/CLAIM_SOURCES.csv",
}
MIGRATED_MODULES = {
    "build_encyclopedia_outputs.py": "src/gardening/publishing/content.py",
    "build_final_encyclopedia_pdf.py": "src/gardening/publishing/encyclopedia_pdf.py",
    "build_project_reports.py": "src/gardening/reporting/project_reports.py",
    "build_publications.py": "src/gardening/publishing/supporting_pdfs.py",
    "data_model.py": "src/gardening/validation/data_model.py",
    "enrich_plant_registry.py": "src/gardening/normalization/registry.py",
    "extract_calendar_data.py": "src/gardening/ingestion/calendar_ocr.py",
    "illustration_assets.py": "src/gardening/illustrations/publication_gate.py",
    "parse_errington_calendar.py": "src/gardening/parsing/calendar.py",
    "produce_publication_assets.py": "src/gardening/publishing/content_assets.py",
    "validate_pipeline.py": "src/gardening/validation/pipeline.py",
}
UNIT_TESTS = {
    "test_check_research_links.py",
    "test_enrich_plant_registry.py",
    "test_parse_errington_calendar.py",
}


def git(*args: str, text: bool = True) -> str | bytes:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=text,
    )
    return result.stdout.rstrip("\r\n") if text else result.stdout


def _file_classification(path: str) -> str:
    lower = path.casefold()
    suffix = Path(path).suffix.casefold()
    if "__pycache__" in lower or suffix in {".pyc", ".pyo"}:
        return "temporary-generated"
    if path in SOURCE_FILES or path == "cover.png":
        return "original-source-artifact"
    if lower.startswith(("plant_illustrations/", "educational_figures/")) and suffix in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".tif",
        ".tiff",
    }:
        return "unapproved-or-review-artwork"
    if path in REGISTRY_FILES or suffix in {".csv", ".json", ".tsv"}:
        return "structured-data-or-transcription"
    if suffix == ".pdf":
        return "generated-or-historical-publication"
    if suffix == ".py":
        return "software-or-test"
    if suffix in {".md", ".rst", ".txt"}:
        return "documentation-or-editorial-content"
    if lower.startswith("fonts/") or suffix in {".ttf", ".otf"}:
        return "design-resource"
    return "other-or-requires-manual-classification"


def _proposed_destination(path: str, old_branch: bool = False) -> str:
    lower = path.casefold()
    name = Path(path).name
    suffix = Path(path).suffix.casefold()
    if "__pycache__" in lower or suffix in {".pyc", ".pyo"}:
        return "exclude-from-repository"
    if path.startswith(".github/"):
        return path
    if old_branch and lower.startswith("plant_illustrations/") and suffix in {
        ".png",
        ".jpg",
        ".jpeg",
        ".webp",
        ".tif",
        ".tiff",
    }:
        return f"plant_illustrations/branch_candidates/{name}"
    if path in SOURCE_FILES:
        return f"sources/original/{name}"
    if path == "cover.png":
        return "assets/covers/cover.png"
    if path.startswith("plant_illustrations/"):
        return path.replace("plant_illustrations/", "assets/botanical/", 1)
    if path.startswith("educational_figures/"):
        return path.replace("educational_figures/", "assets/educational-figures/", 1)
    if path.startswith("reports/") or name.endswith("_REPORT.md"):
        return f"docs/reports/{name}"
    if path in REGISTRY_FILES or suffix in {".csv", ".json", ".tsv"}:
        return f"data/{'registries' if 'registry' in lower or 'claim' in lower else 'raw'}/{name}"
    if suffix == ".py":
        if name.startswith("test_"):
            suite = "unit" if name in UNIT_TESTS else "integration"
            return f"tests/{suite}/{name}"
        if name in MIGRATED_MODULES:
            return MIGRATED_MODULES[name]
        if name in {"build_all.py", "build_publications.py", "render_publication.py"}:
            return f"src/gardening/publishing/{name}"
        return f"src/gardening/{name}"
    if path.startswith("fonts/"):
        return path.replace("fonts/", "assets/fonts/", 1)
    if suffix == ".pdf" and path not in SOURCE_FILES:
        return f"outputs/{name}"
    if suffix == ".md":
        if "MANUSCRIPT" in name or "SUPPLEMENT" in name or "HANDBOOK" in name:
            return f"content/encyclopedia/{name}"
        return f"docs/{name}"
    return path


def _refs() -> list[str]:
    output = str(
        git(
            "for-each-ref",
            "--format=%(refname)",
            "refs/heads",
            "refs/remotes",
            "refs/tags",
        )
    )
    refs = []
    for ref in output.splitlines():
        if ref.startswith("refs/heads/"):
            ref = ref.removeprefix("refs/heads/")
        elif ref.startswith("refs/remotes/"):
            ref = ref.removeprefix("refs/remotes/")
            if ref == "origin/HEAD":
                continue
        elif ref.startswith("refs/tags/"):
            ref = ref.replace("refs/tags/", "tags/", 1)
        else:
            continue
        refs.append(ref)
    return sorted(refs)


def _tree(ref: str) -> dict[str, dict[str, str]]:
    output = str(git("ls-tree", "-r", "-l", "--full-tree", ref))
    result: dict[str, dict[str, str]] = {}
    for line in output.splitlines():
        metadata, path = line.split("\t", 1)
        mode, object_type, blob, size = metadata.split(" ", 3)
        if object_type != "blob":
            continue
        result[path] = {
            "mode": mode,
            "blob": blob,
            "size": size.strip(),
        }
    return result


def _modified_dates(ref: str) -> dict[str, str]:
    output = str(
        git(
            "log",
            "--format=COMMIT-DATE:%cI",
            "--name-only",
            "--no-renames",
            ref,
        )
    )
    dates: dict[str, str] = {}
    current_date = ""
    for line in output.splitlines():
        if line.startswith("COMMIT-DATE:"):
            current_date = line.removeprefix("COMMIT-DATE:")
        elif line and line not in dates:
            dates[line] = current_date
    return dates


def _write_inventory(refs: list[str], output_path: Path) -> dict[str, dict[str, dict[str, str]]]:
    trees = {ref: _tree(ref) for ref in refs}
    dates = {ref: _modified_dates(ref) for ref in refs}
    hash_cache: dict[str, str] = {}
    records: list[dict[str, str]] = []
    hash_paths: dict[str, set[str]] = defaultdict(set)
    path_hashes: dict[str, set[str]] = defaultdict(set)
    record_refs: dict[tuple[str, str], str] = {}

    for ref, tree in trees.items():
        for path, data in tree.items():
            blob = data["blob"]
            if blob not in hash_cache:
                hash_cache[blob] = hashlib.sha256(
                    git("cat-file", "blob", blob, text=False)  # type: ignore[arg-type]
                ).hexdigest()
            digest = hash_cache[blob]
            hash_paths[digest].add(path)
            path_hashes[path].add(digest)
            record_refs[(ref, path)] = digest
            records.append(
                {
                    "ref": ref,
                    "path": path,
                    "kind": "file",
                    "file_type": Path(path).suffix.casefold() or "[no extension]",
                    "size_bytes": data["size"],
                    "git_blob": blob,
                    "sha256": digest,
                    "last_modified_in_fetched_history": dates[ref].get(path, ""),
                    "classification": _file_classification(path),
                    "duplicate_content_paths": "",
                    "same_path_differs_between_refs": "",
                }
            )

    for row in records:
        duplicates = sorted(hash_paths[row["sha256"]] - {row["path"]})
        row["duplicate_content_paths"] = "|".join(duplicates)
        row["same_path_differs_between_refs"] = (
            "yes" if len(path_hashes[row["path"]]) > 1 else "no"
        )

    for ref, tree in trees.items():
        directories: set[str] = set()
        for path in tree:
            parts = Path(path).parts
            for index in range(1, len(parts)):
                directories.add("/".join(parts[:index]))
        for path in sorted(directories):
            records.append(
                {
                    "ref": ref,
                    "path": path,
                    "kind": "directory",
                    "file_type": "directory",
                    "size_bytes": "",
                    "git_blob": "",
                    "sha256": "",
                    "last_modified_in_fetched_history": "",
                    "classification": "inferred-from-tracked-files",
                    "duplicate_content_paths": "",
                    "same_path_differs_between_refs": "",
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=INVENTORY_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(sorted(records, key=lambda row: (row["ref"], row["path"], row["kind"])))
    return trees


def _write_migration_manifest(
    trees: dict[str, dict[str, dict[str, str]]], output_path: Path
) -> None:
    main = trees.get(MAIN_REF, {})
    historical = trees.get(ILLUSTRATION_REF, {})
    all_paths = sorted(main.keys() | historical.keys())
    main_hash: dict[str, str] = {}
    historical_hash: dict[str, str] = {}
    for path in all_paths:
        if path in main:
            main_hash[path] = hashlib.sha256(
                git("cat-file", "blob", main[path]["blob"], text=False)  # type: ignore[arg-type]
            ).hexdigest()
        if path in historical:
            historical_hash[path] = hashlib.sha256(
                git("cat-file", "blob", historical[path]["blob"], text=False)  # type: ignore[arg-type]
            ).hexdigest()

    rows = []
    for path in all_paths:
        in_main = path in main
        in_old = path in historical
        if in_main and in_old:
            comparison = (
                "identical"
                if main_hash[path] == historical_hash[path]
                else "different-content-same-path"
            )
            disposition = "retain-main; inspect older branch changes before any migration"
        elif in_main:
            comparison = "main-only"
            disposition = "retain-main"
        else:
            comparison = "illustration-branch-only"
            if Path(path).suffix.casefold() == ".png" and path.startswith(
                "plant_illustrations/"
            ):
                disposition = (
                    "preserve-original-branch; candidate import deferred for "
                    "size, identity, and rights review"
                )
            else:
                disposition = "preserve-original-branch; assess historical value"
        proposed = _proposed_destination(path, old_branch=not in_main)
        rows.append(
            {
                "path": path,
                "main_present": str(in_main).lower(),
                "illustration_branch_present": str(in_old).lower(),
                "main_sha256": main_hash.get(path, ""),
                "illustration_branch_sha256": historical_hash.get(path, ""),
                "comparison": comparison,
                "proposed_destination": proposed,
                "disposition": disposition,
                "human_review_required": (
                    "yes"
                    if comparison != "identical"
                    or path.casefold().endswith((".png", ".jpg", ".jpeg", ".pdf"))
                    else "no"
                ),
            }
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=MIGRATION_COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _write_audit(refs: list[str], trees: dict[str, dict[str, dict[str, str]]]) -> None:
    main_head = str(git("rev-parse", MAIN_REF))
    illustration_head = str(git("rev-parse", ILLUSTRATION_REF))
    merge_base = str(git("merge-base", MAIN_REF, ILLUSTRATION_REF))
    left, right = str(
        git("rev-list", "--left-right", "--count", f"{MAIN_REF}...{ILLUSTRATION_REF}")
    ).split()
    branch_tree = trees[ILLUSTRATION_REF]
    plant_images = [
        path
        for path in branch_tree
        if path.startswith("plant_illustrations/")
        and Path(path).suffix.casefold() in {".png", ".jpg", ".jpeg", ".webp", ".tif", ".tiff"}
    ]
    image_hashes = {
        hashlib.sha256(
            git("cat-file", "blob", branch_tree[path]["blob"], text=False)  # type: ignore[arg-type]
        ).hexdigest()
        for path in plant_images
    }
    tags = [ref for ref in refs if ref.startswith("tags/")]
    similarity_path = ROOT / "reports" / "ILLUSTRATION_SIMILARITY_AUDIT.csv"
    near_pair_count = None
    if similarity_path.is_file():
        with similarity_path.open(encoding="utf-8", newline="") as stream:
            similarity_rows = list(csv.DictReader(stream))
        near_pair_count = sum(
            bool(row.get("near_duplicate_candidates_at_threshold", "").strip())
            for row in similarity_rows
        ) // 2
    report = [
        "# Repository restructuring baseline",
        "",
        f"- Main head: `{main_head}`.",
        f"- Illustration branch head: `{illustration_head}`.",
        f"- Merge base: `{merge_base}`.",
        f"- Main-only commits since merge base: {left}; illustration-branch-only commits: {right}.",
        f"- Available tags: {len(tags)} (`{', '.join(tags) if tags else 'none'}`).",
        "- Pull request audit: PR #1 was the only pre-existing pull request found; it is merged into `main`.",
        f"- Main tree: {len(trees[MAIN_REF])} tracked files; illustration branch tree: "
        f"{len(branch_tree)} tracked files.",
        f"- Historical plant-image branch: {len(plant_images)} image files, "
        f"{len(image_hashes)} distinct SHA-256 payloads.",
        "- The inventory includes inferred tracked directories, Git blob IDs, file sizes, "
        "SHA-256 hashes, duplicate-path candidates, and last modification dates visible "
        "in the locally fetched Git history. It excludes untracked files and ignored "
        "environments/build outputs.",
        *(
            [
                f"- Perceptual-hash screening found {near_pair_count} possible near-duplicate "
                "pairs at Hamming distance ≤5; these are not identity findings."
            ]
            if near_pair_count is not None
            else ["- Perceptual near-duplicate screening has not yet been generated."]
        ),
        "",
        "## Branch decision",
        "",
        "`main` is the canonical implementation and is materially newer. The older "
        "`illustration-assets` branch diverges from the common ancestor and lacks current "
        "validation, evidence, and publication safeguards. It is not safe to merge wholesale.",
        "Its 70 plant images remain on that branch. Existing per-image review records identify "
        "68 unique payloads, duplicate pairs, nine filename/registry mismatches, and "
        "cross-plant labels. Because the image set is approximately 249 MB and remains "
        "unapproved, binary import is deferred; the branch and checksummed migration manifest "
        "preserve access without bloating `main` or bypassing review.",
        "",
        "## Migration files",
        "",
        "- `reports/REPOSITORY_INVENTORY.csv` — file and inferred-directory inventory by ref.",
        "- `reports/REPOSITORY_MIGRATION_MANIFEST.csv` — per-path comparison, proposed "
        "destination, disposition, and human-review flag.",
        "- `reports/ILLUSTRATION_BRANCH_REVIEW.csv` — existing per-image review record.",
        "- `reports/ILLUSTRATION_SIMILARITY_AUDIT.csv` — per-image perceptual hash and "
        "near-duplicate candidates for human inspection.",
        "",
        "The local repository was unshallowed before computing ancestry. No branch or tag was "
        "deleted, rebased, force-pushed, or rewritten.",
        "",
    ]
    (ROOT / "reports" / "RESTRUCTURE_AUDIT.md").write_text(
        "\n".join(report), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Inventory tracked files across Git refs.")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "reports")
    args = parser.parse_args()
    refs = _refs()
    required_refs = {MAIN_REF, ILLUSTRATION_REF}
    if missing := required_refs - set(refs):
        parser.error(f"Required audit refs are missing: {', '.join(sorted(missing))}")
    trees = _write_inventory(refs, args.output_dir / "REPOSITORY_INVENTORY.csv")
    _write_migration_manifest(
        trees, args.output_dir / "REPOSITORY_MIGRATION_MANIFEST.csv"
    )
    _write_audit(refs, trees)
    print(f"Inventoried {len(refs)} refs in {args.output_dir}.")


if __name__ == "__main__":
    main()
