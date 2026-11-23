from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Sequence

from gardening.assets import audit_assets, pending_review
from gardening.config import find_repository_root
from gardening.research.gbif import collect_gbif_candidates, write_candidate_report
from gardening.verification.engine import (
    VerificationInputError,
    build_verification_report,
    write_verification_report,
)


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


def _run_verification_audit(
    repository: Path, output: Path | None, require_ready: bool
) -> int:
    try:
        report = build_verification_report(repository)
        if output is None:
            print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
        else:
            write_verification_report(report, output)
            print(
                f"Wrote {output}; release decision: "
                f"{report['readiness']['decision']}."
            )
    except (OSError, ValueError, VerificationInputError) as error:
        LOGGER.error("Verification audit failed: %s", error)
        return 2
    if report["readiness"]["errors"]:
        return 1
    if require_ready and report["readiness"]["decision"] != "READY":
        LOGGER.error("Release requirements remain unmet.")
        return 1
    return 0


def _run_gbif_taxonomy(
    repository: Path,
    output: Path,
    cache_directory: Path,
    plant_id: str | None,
    delay_seconds: float,
    timeout: float,
) -> int:
    try:
        report = collect_gbif_candidates(
            repository,
            cache_directory=cache_directory,
            plant_id=plant_id,
            delay_seconds=delay_seconds,
            timeout=timeout,
        )
        write_candidate_report(report, output)
    except (OSError, ValueError) as error:
        LOGGER.error("GBIF candidate collection failed: %s", error)
        return 2
    counts: dict[str, int] = {}
    for row in report["results"]:
        status = row["candidate"]["fetch_status"]
        counts[status] = counts.get(status, 0) + 1
    print(
        f"Wrote {output}; collected {len(report['results'])} GBIF name candidate(s) "
        f"using {report['network_requests']} network request(s); statuses={counts}. "
        "Candidates remain unverified and require human review."
    )
    unavailable = {
        "ACCESS_DENIED",
        "TEMPORARILY_UNAVAILABLE",
        "UNREACHABLE",
        "UNKNOWN",
    }
    return int(any(status in unavailable for status in counts))


def _repository_path(repository: Path, path: Path) -> Path:
    return path if path.is_absolute() else repository / path


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

    verify = commands.add_parser("verify", help="Run structured scientific and release audits")
    verify_commands = verify.add_subparsers(dest="verification_command", required=True)
    audit_verification = verify_commands.add_parser(
        "audit", help="Audit evidence, statuses, assets, sources, and publications"
    )
    audit_verification.add_argument(
        "--output", type=Path, help="Write the deterministic JSON report to this path"
    )
    audit_verification.add_argument(
        "--require-ready",
        action="store_true",
        help="Exit non-zero unless all release dimensions are complete",
    )
    audit_verification.set_defaults(
        handler=lambda args: _run_verification_audit(
            args.repo, args.output, args.require_ready
        )
    )

    research = commands.add_parser("research", help="Research evidence tools")
    research_commands = research.add_subparsers(dest="research_command", required=True)
    _external_command(
        research_commands.add_parser("validate", help="Check candidate research links"),
        ("check_research_links.py",),
        forward_args=True,
    )
    taxonomy = research_commands.add_parser(
        "taxonomy", help="Collect unverified name-match candidates from GBIF"
    )
    taxonomy.add_argument("--provider", choices=("gbif",), default="gbif")
    taxonomy.add_argument("--plant-id", help="Limit lookup to one stable plant ID")
    taxonomy.add_argument(
        "--output",
        type=Path,
        default=Path("build/research/gbif_taxonomy_candidates.json"),
    )
    taxonomy.add_argument(
        "--cache-directory",
        type=Path,
        default=Path("build/research/gbif-cache"),
    )
    taxonomy.add_argument("--delay-seconds", type=float, default=1.0)
    taxonomy.add_argument("--timeout", type=float, default=20.0)
    taxonomy.set_defaults(
        handler=lambda args: _run_gbif_taxonomy(
            args.repo,
            _repository_path(args.repo, args.output),
            _repository_path(args.repo, args.cache_directory),
            args.plant_id,
            args.delay_seconds,
            args.timeout,
        )
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
        (
            "-m",
            "gardening.cli",
            "verify",
            "audit",
            "--output",
            "reports/VERIFICATION_AUDIT.json",
        ),
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
