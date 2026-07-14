"""Shared pytest fixtures.

`tmp_path` is pytest's built-in temporary-directory fixture; we build a small, realistic
project tree inside it so every test runs against fresh, isolated files.
"""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def sample_project(tmp_path: Path) -> Path:
    """A small project containing recognized files plus ignored directories."""
    root = tmp_path / "sample"
    root.mkdir()

    (root / "main.py").write_text("print('hello')\n")
    (root / "utils.py").write_text("def helper():\n    return 1\n")
    (root / "README.md").write_text("# Sample\n")
    (root / "package.json").write_text("{}\n")

    sub = root / "src"
    sub.mkdir()
    (sub / "app.ts").write_text("const x: number = 1;\n")
    (sub / "style.css").write_text("body { color: black; }\n")

    # Directories that must be skipped by default.
    ignored = root / "node_modules"
    ignored.mkdir()
    (ignored / "lib.js").write_text("// ignored dependency\n")

    vcs = root / ".git"
    vcs.mkdir()
    (vcs / "config").write_text("ignored vcs metadata\n")

    return root
