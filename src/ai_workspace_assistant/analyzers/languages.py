"""Detects which programming languages are present, via the extension -> language map."""

from __future__ import annotations

from collections import defaultdict

from ai_workspace_assistant.config import EXTENSION_TO_LANGUAGE, LANGUAGE_ANALYZER_NAME
from ai_workspace_assistant.models import LanguageStat, ScanResult


class LanguageAnalyzer:
    """Groups files by the language inferred from their extension."""

    name = LANGUAGE_ANALYZER_NAME

    def analyze(self, scan: ScanResult) -> list[LanguageStat]:
        counts: dict[str, int] = defaultdict(int)
        sizes: dict[str, int] = defaultdict(int)
        for entry in scan.files:
            language = EXTENSION_TO_LANGUAGE.get(entry.extension.lower(), "Other")
            counts[language] += 1
            sizes[language] += entry.size

        return [
            LanguageStat(language=language, files=count, total_size=sizes[language])
            for language, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)
        ]
