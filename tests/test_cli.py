"""End-to-end tests for the CLI entry point."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ai_workspace_assistant.cli import build_parser, main


def test_parser_defaults() -> None:
    args = build_parser().parse_args([])
    assert args.path == "."
    assert args.format == "markdown"


def test_parser_lists_markdown_format() -> None:
    args = build_parser().parse_args(["--format", "markdown"])
    assert args.format == "markdown"


def test_parser_accepts_json_format() -> None:
    args = build_parser().parse_args(["--format", "json"])
    assert args.format == "json"


def test_main_json_output_is_valid(
    sample_project: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(sample_project), "--format", "json", "--quiet"])
    assert code == 0
    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["total_files"] == 6
    assert any(lang["language"] == "Python" for lang in data["languages"])
    assert data["todos"]["total"] >= 0


def test_main_reports_project(sample_project: Path, capsys: pytest.CaptureFixture[str]) -> None:
    code = main([str(sample_project)])
    assert code == 0
    captured = capsys.readouterr()
    assert "# Project Report:" in captured.out
    assert "Python" in captured.out


def test_main_returns_error_for_missing_path(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    code = main([str(tmp_path / "missing")])
    assert code == 2
    assert "error:" in capsys.readouterr().err


def test_main_writes_output_file(sample_project: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "report.md"
    code = main([str(sample_project), "--output", str(out_file)])
    assert code == 0
    assert out_file.exists()
    assert "# Project Report:" in out_file.read_text()
