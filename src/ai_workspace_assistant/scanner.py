"""Directory walking and scan orchestration.

The scanner is intentionally filesystem-only: it resolves the target, applies ignore
rules, and emits a `ScanResult`. It never decides what the data *means* — that is the
job of analyzers.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

from ai_workspace_assistant.errors import ScanError
from ai_workspace_assistant.models import FileEntry, ScanResult
from ai_workspace_assistant.progress import NullProgress, Progress


def resolve_root(path: Path) -> Path:
    """Return an absolute, validated project root or raise `ScanError`."""
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise ScanError(f"Path does not exist: {resolved}")
    if not resolved.is_dir():
        raise ScanError(f"Not a directory: {resolved}")
    return resolved


def scan_project(
    root: Path,
    ignores: Iterable[str] = (),
    progress: Progress | None = None,
) -> ScanResult:
    """Walk `root`, skipping ignored directories, and return a `ScanResult`.

    Unreadable files are skipped and recorded as warnings rather than aborting the scan,
    so a single locked file never prevents a report from being produced.
    """
    progress = progress or NullProgress()
    base = resolve_root(root)
    ignore_set = frozenset(ignores)

    files: list[FileEntry] = []
    warnings: list[str] = []
    scanned_dirs = 0

    for dirpath, dirnames, filenames in os.walk(base):
        # Prune ignored directories in place so os.walk never descends into them.
        dirnames[:] = [name for name in dirnames if name not in ignore_set]
        scanned_dirs += 1

        for filename in filenames:
            file_path = Path(dirpath) / filename
            try:
                stat = os.stat(file_path)
            except OSError as exc:
                warnings.append(f"Skipped unreadable file {file_path}: {exc}")
                continue

            try:
                relative = file_path.relative_to(base)
            except ValueError:
                relative = file_path

            files.append(FileEntry(path=relative, size=stat.st_size, extension=file_path.suffix))
            progress.update(1)

    progress.finish()
    return ScanResult(root=base, files=files, scanned_dirs=scanned_dirs, warnings=warnings)
