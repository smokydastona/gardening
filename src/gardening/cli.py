from __future__ import annotations

import argparse
import logging
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from gardening.assets import audit_assets, pending_review
from gardening.config import find_repository_root


LOGGER = logging.getLogger("gardening")


def _run(repository: Path, *command: str) -> int:
    try:
        result = subprocess.run([sys.executable, *command], cwd=repository, check=False)
    except OSError as error:
        LOGGER.error("Unable to run %s: %s", command[0], error)
        return 2
    return result.returncode


def _pipeline(*commands: tuple[str, ...]) -> int:
    def run(args: argparse.Namespace) -> int:
        for command in commands:
            result = _run(args.repo, *command, *getattr(args, "extra", []))
            if result:
                return result
        return 0

    return run


def _external_command(
    parser: argparse.ArgumentParser,
    *commands: tuple[str, ...],
    forward_args: bool = False,
) -> None:
    if forward_args:
        parser.add_argument(
            "extra",
            nargs=argparse.REMAINDER,
            help="Additional arguments forwarded to the underlying command",
        )
    parser.set_defaults(handler=_pipeline(*commands))


def _show_asset_audit(repository: Path, kind: str) -> int:
    audit = audit_assets(repository, kind)
    print(
        f"{kind.title()} assets: {audit.record_count} records; "
        f"{audit.checked_files} checksummed files; {audit.approved_count} approved."
    )
    for warning in audit.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in audit.errors:
        print(f"ERROR: {error}", file=sys.stderr)
    return audit.exit_code


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gardening",
        description="Validate, review, build, and publish the Errington gardening reference.",
    )
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Repository checkout (defaults to the checkout containing this package)",
    )
    parser.add_argument("--verbose", action="store_true", help="Enable diagnostic logging")
    commands = parser.add_subparsers(dest="group", required=True)

    validate = commands.add_parser("validate", help="Validate sources and records")
    _external_command(validate, ("validate_pipeline.py",), forward_args=True)

    test = commands.add_parser("test", help="Run the repository test suite")
    _external_command(test, ("-m", "pytest"), forward_args=True)

    research = commands.add_parser("research", help="Research evidence tools")
    research_commands = research.add_subparsers(dest="research_command", required=True)
    _external_command(
        research_commands.add_parser("validate", help="Check candidate research links"),
        ("check_research_links.py",),
        forward_args=True,
    )

    calendar = commands.add_parser("calendar", help="Calendar validation")
    calendar_commands = calendar.add_subparsers(dest="calendar_command", required=True)
    _external_command(
        calendar_commands.add_parser("validate", help="Validate calendar source records"),
        ("validate_pipeline.py",),
        forward_args=True,
    )

    illustrations = commands.add_parser("illustrations", help="Illustration workflow")
    illustration_commands = illustrations.add_subparsers(
        dest="illustration_command", required=True
    )
    audit = illustration_commands.add_parser("audit", help="Audit candidate checksums and IDs")
    audit.set_defaults(handler=lambda args: _show_asset_audit(args.repo, "plant"))
    generate = illustration_commands.add_parser(
        "generate", help="Generate an unapproved illustration candidate"
    )
    _external_command(
        generate, ("generate_illustrations.py", "generate"), forward_args=True
    )
    review = illustration_commands.add_parser(
        "review", help="List illustration records that still need human review"
    )
    review.add_argument("--plant", help="Filter by stable plant ID")
    review.set_defaults(
        handler=lambda args: _review_illustrations(args.repo, args.plant)
    )

    figures = commands.add_parser("figures", help="Educational figure workflow")
    figure_commands = figures.add_subparsers(dest="figure_command", required=True)
    figure_audit = figure_commands.add_parser(
        "validate", help="Validate figure files, checksums, and source references"
    )
    figure_audit.set_defaults(handler=lambda args: _show_asset_audit(args.repo, "figure"))

    publish = commands.add_parser("publish", help="Build one or more publications")
    publish_commands = publish.add_subparsers(dest="publication", required=True)
    _external_command(
        publish_commands.add_parser("encyclopedia", help="Build the encyclopedia PDF"),
        ("build_encyclopedia_outputs.py",),
        ("build_final_encyclopedia_pdf.py",),
        ("validate_pipeline.py", "--publication"),
    )
    for name in ("monthly", "directory"):
        _external_command(
            publish_commands.add_parser(
                name,
                help=f"Build {name} publication (the legacy builder also refreshes related PDFs)",
            ),
            ("build_publications.py",),
        )
    _external_command(
        publish_commands.add_parser("all", help="Build every publication"),
        ("build_all.py",),
    )

    reports = commands.add_parser("reports", help="Generate project status reports")
    report_commands = reports.add_subparsers(dest="report_command", required=True)
    _external_command(
        report_commands.add_parser("generate", help="Regenerate all status reports"),
        ("build_project_reports.py",),
        ("generate_release_status.py",),
    )

    build = commands.add_parser("build", help="Build and validate project outputs")
    build_commands = build.add_subparsers(dest="build_command", required=True)
    _external_command(
        build_commands.add_parser("all", help="Run the complete reproducible build"),
        ("build_all.py",),
    )
    return parser


def _review_illustrations(repository: Path, plant_id: str | None) -> int:
    try:
        rows = pending_review(repository, plant_id)
    except (OSError, ValueError, KeyError) as error:
        LOGGER.error("Cannot load illustration review queue: %s", error)
        return 2
    if not rows:
        print("No illustration candidates match the requested review filter.")
        return 0
    for row in rows:
        print(
            f"{row.get('plant_id', '')}\t{row.get('display_name', '')}\t"
            f"{row.get('filename', '')}\t{row.get('review_status', '')}"
        )
    print(f"{len(rows)} candidate(s) require human review; none are approved by this command.")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s: %(message)s",
    )
    try:
        args.repo = (args.repo or find_repository_root()).resolve()
    except FileNotFoundError as error:
        parser.error(str(error))
    return args.handler(args)


if __name__ == "__main__":
    raise SystemExit(main())
