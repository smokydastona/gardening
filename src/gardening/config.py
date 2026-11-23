from __future__ import annotations

from pathlib import Path


def find_repository_root(start: Path | str | None = None) -> Path:
    path = Path(start or __file__).resolve()
    for candidate in (path, *path.parents):
        if (candidate / "build_all.py").is_file() and (
            candidate / "plant_registry.csv"
        ).is_file():
            return candidate
    raise FileNotFoundError(
        "Could not locate the gardening repository. Run this command from a "
        "repository checkout or pass --repo."
    )
