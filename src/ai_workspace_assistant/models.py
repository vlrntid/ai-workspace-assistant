"""Typed data structures that form the contract between the scanner, analyzers, and
reporters.

Keeping these as plain dataclasses means each layer communicates through explicit,
self-documenting shapes rather than loose dicts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from ai_workspace_assistant.config import (
    EXTENSION_ANALYZER_NAME,
    LANGUAGE_ANALYZER_NAME,
)


@dataclass
class FileEntry:
    """A single file discovered during a scan, relative to the project root."""

    path: Path
    size: int
    extension: str


@dataclass
class ScanResult:
    """The complete, immutable result of walking a project directory."""

    root: Path
    files: list[FileEntry] = field(default_factory=list)
    scanned_dirs: int = 0
    warnings: list[str] = field(default_factory=list)

    @property
    def total_files(self) -> int:
        return len(self.files)

    @property
    def total_size(self) -> int:
        return sum(entry.size for entry in self.files)


@dataclass
class ExtensionCount:
    """Aggregated count and size for a single file extension."""

    extension: str
    count: int
    total_size: int


@dataclass
class LanguageStat:
    """Aggregated count and size for a single detected programming language."""

    language: str
    files: int
    total_size: int


@dataclass
class TodoSummary:
    """Aggregated TODO/FIXME markers found across the scanned text files."""

    todos: int
    fixmes: int
    total: int
    by_file: list[tuple[str, int]]


@dataclass
class ProjectReport:
    """The final report: a scan plus the output of every registered analyzer."""

    scan: ScanResult
    analyses: dict[str, object]
    generated_at: datetime

    def get_extensions(self) -> list[ExtensionCount]:
        return cast(list[ExtensionCount], self.analyses[EXTENSION_ANALYZER_NAME])

    def get_languages(self) -> list[LanguageStat]:
        return cast(list[LanguageStat], self.analyses[LANGUAGE_ANALYZER_NAME])


def utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(UTC)
