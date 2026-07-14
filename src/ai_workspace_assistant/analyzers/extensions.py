"""Counts files grouped by their extension."""

from __future__ import annotations

from collections import defaultdict

from ai_workspace_assistant.config import EXTENSION_ANALYZER_NAME
from ai_workspace_assistant.models import ExtensionCount, ScanResult


class ExtensionAnalyzer:
    """Aggregates how many files (and how much space) each extension occupies."""

    name = EXTENSION_ANALYZER_NAME

    def analyze(self, scan: ScanResult) -> list[ExtensionCount]:
        counts: dict[str, int] = defaultdict(int)
        sizes: dict[str, int] = defaultdict(int)
        for entry in scan.files:
            extension = entry.extension or ""
            counts[extension] += 1
            sizes[extension] += entry.size

        return [
            ExtensionCount(extension=extension, count=count, total_size=sizes[extension])
            for extension, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)
        ]
