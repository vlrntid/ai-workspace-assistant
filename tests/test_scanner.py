"""Tests for the directory scanner."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from ai_workspace_assistant.errors import ScanError
from ai_workspace_assistant.scanner import resolve_root, scan_project


def test_resolve_root_missing(tmp_path: Path) -> None:
    with pytest.raises(ScanError):
        resolve_root(tmp_path / "does-not-exist")


def test_resolve_root_not_a_directory(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("x")
    with pytest.raises(ScanError):
        resolve_root(file_path)


def test_scan_ignores_default_dirs(sample_project: Path) -> None:
    result = scan_project(sample_project, ignores={".git", "node_modules"})
    extensions = {entry.extension for entry in result.files}
    assert ".js" not in extensions  # node_modules/lib.js must be skipped
    assert result.total_files == 6  # main, utils, README, package, app.ts, style.css


def test_scan_includes_everything_without_ignores(sample_project: Path) -> None:
    result = scan_project(sample_project, ignores=set())
    assert result.total_files == 8  # the two ignored files are now included


def test_scan_counts_extensions(sample_project: Path) -> None:
    result = scan_project(sample_project, ignores={".git", "node_modules"})
    py_files = [e for e in result.files if e.extension == ".py"]
    assert len(py_files) == 2


def test_scan_reports_unreadable_files(
    sample_project: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_stat = os.stat

    def fake_stat(path: object, *args: object, **kwargs: object) -> object:
        if Path(path).name == "main.py":  # type: ignore[arg-type]
            msg = "Permission denied"
            raise OSError(msg)
        return real_stat(path, *args, **kwargs)  # type: ignore[call-arg]

    monkeypatch.setattr(os, "stat", fake_stat)

    result = scan_project(sample_project, ignores={".git", "node_modules"})
    assert result.total_files == 5  # main.py was skipped
    assert any("main.py" in warning for warning in result.warnings)
