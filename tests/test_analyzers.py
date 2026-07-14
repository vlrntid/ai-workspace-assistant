"""Tests for the built-in analyzers."""

from __future__ import annotations

from pathlib import Path

from ai_workspace_assistant.analyzers.extensions import ExtensionAnalyzer
from ai_workspace_assistant.analyzers.languages import LanguageAnalyzer
from ai_workspace_assistant.analyzers.todos import TodoAnalyzer
from ai_workspace_assistant.models import FileEntry, ScanResult, TodoSummary


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


def test_language_detection_uses_shebang(tmp_path: Path) -> None:
    script = tmp_path / "run"
    script.write_text("#!/usr/bin/env python\nprint('hi')\n")
    scan = ScanResult(root=tmp_path, files=[FileEntry(Path("run"), 20, "")])
    assert LanguageAnalyzer().analyze(scan)[0].language == "Python"


def test_language_detection_disambiguates_cpp_header(tmp_path: Path) -> None:
    header = tmp_path / "widget.h"
    header.write_text("class Widget { public: int x; }; namespace ns {}\n")
    scan = ScanResult(root=tmp_path, files=[FileEntry(Path("widget.h"), 40, ".h")])
    assert LanguageAnalyzer().analyze(scan)[0].language == "C++"


def test_language_detection_keeps_plain_c_header(tmp_path: Path) -> None:
    header = tmp_path / "math.h"
    header.write_text("int add(int a, int b);\n")
    scan = ScanResult(root=tmp_path, files=[FileEntry(Path("math.h"), 30, ".h")])
    assert LanguageAnalyzer().analyze(scan)[0].language == "C"


def test_language_detection_leaves_unknown_extension_as_other(tmp_path: Path) -> None:
    mystery = tmp_path / "data.xyz"
    mystery.write_text("no clues here\n")
    scan = ScanResult(root=tmp_path, files=[FileEntry(Path("data.xyz"), 14, ".xyz")])
    assert LanguageAnalyzer().analyze(scan)[0].language == "Other"


def test_todo_analyzer_counts_markers(tmp_path: Path) -> None:
    code_file = tmp_path / "code.py"
    code_file.write_text("x = 1  # TODO: refactor this\ny = 2  # FIXME: off-by-one\n")
    scan = ScanResult(root=tmp_path, files=[FileEntry(Path("code.py"), 42, ".py")])
    result = TodoAnalyzer().analyze(scan)

    assert isinstance(result, TodoSummary)
    assert result.todos == 1
    assert result.fixmes == 1
    assert result.total == 2
    assert ("code.py", 2) in result.by_file


def test_todo_analyzer_skips_binary_files(tmp_path: Path) -> None:
    binary_file = tmp_path / "data.bin"
    binary_file.write_bytes(b"\xff\xfe\x00TODO\x80")  # invalid UTF-8 -> undecodable
    scan = ScanResult(root=tmp_path, files=[FileEntry(Path("data.bin"), 5, ".bin")])
    result = TodoAnalyzer().analyze(scan)
    assert result.total == 0
