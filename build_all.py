"""Single reproducible build command for the Errington publication system."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


def run(command: list[str]) -> None:
    subprocess.run([sys.executable, *command], cwd=BASE_DIR, check=True)


def main() -> None:
    run(["validate_pipeline.py"])
    run(["parse_errington_calendar.py"])
    run(["enrich_plant_registry.py"])
    run(["build_project_reports.py"])
    run(["build_encyclopedia_outputs.py"])
    run(["build_final_encyclopedia_pdf.py"])
    run(["build_publications.py"])
    run(["validate_pipeline.py", "--publication"])


if __name__ == "__main__":
    main()
