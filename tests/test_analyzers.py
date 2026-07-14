"""Tests for the built-in analyzers."""

from __future__ import annotations

from pathlib import Path

from ai_workspace_assistant.analyzers.extensions import ExtensionAnalyzer
from ai_workspace_assistant.analyzers.languages import LanguageAnalyzer
from ai_workspace_assistant.models import FileEntry, ScanResult


def _make_scan(entries: list[tuple[str, int, str]]) -> ScanResult:
    files = [
        FileEntry(path=Path(name), size=size, extension=extension)
        for name, size, extension in entries
    ]
    return ScanResult(root=Path("/tmp/x"), files=files)


def test_extension_analyzer_counts_and_sizes() -> None:
    scan = _make_scan([("a.py", 10, ".py"), ("b.py", 20, ".py"), ("c.md", 5, ".md")])
    result = ExtensionAnalyzer().analyze(scan)
    by_ext = {item.extension: item for item in result}

    assert by_ext[".py"].count == 2
    assert by_ext[".py"].total_size == 30
    assert by_ext[".md"].count == 1
    # Results are sorted by count, descending.
    assert result[0].count >= result[1].count


def test_language_analyzer_detects_and_groups() -> None:
    scan = _make_scan(
        [
            ("a.py", 10, ".py"),
            ("b.py", 20, ".py"),
            ("c.ts", 5, ".ts"),
            ("mystery.xyz", 1, ".xyz"),
        ]
    )
    result = LanguageAnalyzer().analyze(scan)
    by_language = {item.language: item.files for item in result}

    assert by_language["Python"] == 2
    assert by_language["TypeScript"] == 1
    assert by_language["Other"] == 1
