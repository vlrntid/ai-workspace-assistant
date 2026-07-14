"""Tests for the Markdown reporter."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from ai_workspace_assistant.models import (
    ExtensionCount,
    FileEntry,
    LanguageStat,
    ProjectReport,
    ScanResult,
)
from ai_workspace_assistant.reporters.markdown import MarkdownReporter, human_size


def _make_report() -> ProjectReport:
    scan = ScanResult(
        root=Path("/home/user/myproj"),
        files=[
            FileEntry(Path("a.py"), 100, ".py"),
            FileEntry(Path("b.ts"), 50, ".ts"),
        ],
        scanned_dirs=3,
    )
    analyses = {
        "extensions": [
            ExtensionCount(".py", 1, 100),
            ExtensionCount(".ts", 1, 50),
        ],
        "languages": [
            LanguageStat("Python", 1, 100),
            LanguageStat("TypeScript", 1, 50),
        ],
    }
    return ProjectReport(scan=scan, analyses=analyses, generated_at=datetime.now(UTC))


def test_markdown_contains_expected_sections() -> None:
    out = MarkdownReporter().render(_make_report())
    assert "# Project Report: myproj" in out
    assert "## Overview" in out
    assert "## Languages" in out
    assert "## Files by Extension" in out
    assert "Python" in out
    assert "TypeScript" in out


def test_markdown_lists_warnings_when_present() -> None:
    report = _make_report()
    report.scan.warnings.append("Skipped unreadable file x.py")
    out = MarkdownReporter().render(report)
    assert "## Warnings" in out
    assert "Skipped unreadable file x.py" in out


def test_human_size_formatting() -> None:
    assert human_size(0) == "0 B"
    assert human_size(512) == "512 B"
    assert human_size(1024) == "1.0 KB"
    assert human_size(1536) == "1.5 KB"
