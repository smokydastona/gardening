from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

from gardening import cli


def test_validate_command_delegates_to_existing_source_validator(monkeypatch, tmp_path: Path) -> None:
    calls = []

    def fake_run(command, cwd, check):
        calls.append((command, cwd, check))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(cli.subprocess, "run", fake_run)

    assert cli.main(["--repo", str(tmp_path), "validate"]) == 0
    assert calls[0][0][1:] == ["validate_pipeline.py"]
    assert calls[0][1] == tmp_path


def test_failed_pipeline_command_preserves_child_exit_code(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr(
        cli.subprocess,
        "run",
        lambda *args, **kwargs: SimpleNamespace(returncode=7),
    )

    assert cli.main(["--repo", str(tmp_path), "build", "all"]) == 7


def test_reports_generate_audit_between_registers_and_release_status(monkeypatch, tmp_path):
    commands = []
    monkeypatch.setattr(
        cli,
        "_run",
        lambda repository, *command: commands.append(command) or 0,
    )

    assert cli.main(["--repo", str(tmp_path), "reports", "generate"]) == 0
    assert commands == [
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
    ]


def test_parser_exposes_requested_workflow_commands() -> None:
    parser = cli.build_parser()
    help_text = parser.format_help()

    assert "illustrations" in help_text
    assert "publish" in help_text
    assert "research" in help_text
    assert "verify" in help_text
