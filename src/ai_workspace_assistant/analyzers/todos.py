"""Counts TODO / FIXME markers across text files.

This is a worked example of the `Analyzer` extension point: it takes a `ScanResult`
and returns a structured `TodoSummary`. Because it reads file contents it only attempts
text files and swallows decode/permission errors so a single binary never aborts it.
"""

from __future__ import annotations

import re
from collections import defaultdict

from ai_workspace_assistant.config import TODO_ANALYZER_NAME
from ai_workspace_assistant.models import ScanResult, TodoSummary

_MARKER = re.compile(r"\b(TODO|FIXME)\b")


class TodoAnalyzer:
    """Aggregates TODO/FIXME markers found in the scanned text files."""

    name = TODO_ANALYZER_NAME

    def analyze(self, scan: ScanResult) -> TodoSummary:
        todos = 0
        fixmes = 0
        by_file: dict[str, int] = defaultdict(int)

        for entry in scan.files:
            try:
                text = (scan.root / entry.path).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue

            for match in _MARKER.finditer(text):
                if match.group(1) == "TODO":
                    todos += 1
                else:
                    fixmes += 1
                by_file[str(entry.path)] += 1

        return TodoSummary(
            todos=todos,
            fixmes=fixmes,
            total=todos + fixmes,
            by_file=sorted(by_file.items(), key=lambda item: item[1], reverse=True),
        )
