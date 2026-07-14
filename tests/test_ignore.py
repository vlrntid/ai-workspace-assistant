"""Tests for the .gitignore-style matcher."""

from __future__ import annotations

from pathlib import Path

from ai_workspace_assistant.ignore import GitignoreMatcher


def _make(tmp_path: Path, text: str) -> GitignoreMatcher:
    (tmp_path / ".gitignore").write_text(text)
    return GitignoreMatcher(tmp_path)


def test_comments_and_blanks_are_ignored(tmp_path: Path) -> None:
    matcher = _make(tmp_path, "# comment\n\n   \n*.log\n")
    assert matcher.is_ignored(Path("a/b.log"), is_dir=False)
    assert not matcher.is_ignored(Path("a/blog"), is_dir=False)


def test_basename_pattern_matches_any_depth(tmp_path: Path) -> None:
    matcher = _make(tmp_path, "*.pyc\n")
    assert matcher.is_ignored(Path("x.pyc"), is_dir=False)
    assert matcher.is_ignored(Path("a/b/x.pyc"), is_dir=False)
    assert not matcher.is_ignored(Path("x.py"), is_dir=False)


def test_trailing_slash_is_directory_only(tmp_path: Path) -> None:
    matcher = _make(tmp_path, "build/\n")
    assert matcher.is_ignored(Path("build"), is_dir=True)
    assert matcher.is_ignored(Path("a/build"), is_dir=True)
    assert not matcher.is_ignored(Path("build"), is_dir=False)  # a file named build
    assert not matcher.is_ignored(Path("abuild"), is_dir=True)


def test_leading_slash_is_anchored(tmp_path: Path) -> None:
    matcher = _make(tmp_path, "/dist\n")
    assert matcher.is_ignored(Path("dist"), is_dir=True)
    assert not matcher.is_ignored(Path("a/dist"), is_dir=True)


def test_negation_overrides_previous_rule(tmp_path: Path) -> None:
    matcher = _make(tmp_path, "*.log\n!important.log\n")
    assert matcher.is_ignored(Path("debug.log"), is_dir=False)
    assert not matcher.is_ignored(Path("important.log"), is_dir=False)


def test_globstar_matches_across_directories(tmp_path: Path) -> None:
    matcher = _make(tmp_path, "**/*.pyc\n")
    assert matcher.is_ignored(Path("b.pyc"), is_dir=False)
    assert matcher.is_ignored(Path("a/b.pyc"), is_dir=False)


def test_missing_gitignore_yields_empty_matcher(tmp_path: Path) -> None:
    matcher = GitignoreMatcher(tmp_path)
    assert not matcher.is_ignored(Path("anything"), is_dir=False)
