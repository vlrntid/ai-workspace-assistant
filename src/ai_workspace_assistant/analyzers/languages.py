"""Detects which programming languages are present.

The base guess comes from the extension -> language map. For the few cases the
extension can't decide — extensionless scripts and C/C++ headers — we peek at the
file's start (shebang line, or C++ markers) to refine the guess. Sniffing is limited
to those ambiguous extensions, so clearly-typed files (`.py`, `.js`, ...) never touch
disk during analysis.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from ai_workspace_assistant.config import EXTENSION_TO_LANGUAGE, LANGUAGE_ANALYZER_NAME
from ai_workspace_assistant.models import LanguageStat, ScanResult

# Extensions whose language can't be decided from the name alone, so we sniff content.
CONTENT_SNIFF_EXTENSIONS = frozenset({"", ".h"})

# Substrings that strongly indicate C++ rather than C, when scanning a `.h` file.
CPP_MARKERS = (
    "class ",
    "template",
    "namespace",
    "std::",
    "nullptr",
    "cout",
    "public:",
    "private:",
    "virtual ",
    "::",
)


def language_from_shebang(shebang: str) -> str | None:
    """Map a `#!` line to a language label, or None if it can't be determined."""
    lowered = shebang.lower()
    if "python" in lowered:
        return "Python"
    if "ruby" in lowered:
        return "Ruby"
    if "perl" in lowered:
        return "Perl"
    if "php" in lowered:
        return "PHP"
    if "node" in lowered:
        return "JavaScript"
    if any(shell in lowered for shell in ("bash", "sh", "zsh", "ksh", "fish")):
        return "Shell"
    return None


def refine_language(path: Path, extension: str) -> str | None:
    """Inspect a file's start to improve an ambiguous language guess.

    Returns a refined language, or None if content sniffing is inconclusive.
    """
    try:
        with path.open("r", encoding="utf-8", errors="strict") as handle:
            head = handle.read(4096)
    except (OSError, UnicodeDecodeError, ValueError):
        return None

    first_line = head.splitlines()[0] if head else ""
    if first_line.startswith("#!"):
        shebang_language = language_from_shebang(first_line)
        if shebang_language is not None:
            return shebang_language

    if extension == ".h":
        return "C++" if any(marker in head for marker in CPP_MARKERS) else "C"

    return None


class LanguageAnalyzer:
    """Groups files by the language inferred from their extension and content."""

    name = LANGUAGE_ANALYZER_NAME

    def analyze(self, scan: ScanResult) -> list[LanguageStat]:
        counts: dict[str, int] = defaultdict(int)
        sizes: dict[str, int] = defaultdict(int)
        for entry in scan.files:
            language = EXTENSION_TO_LANGUAGE.get(entry.extension.lower(), "Other")
            if entry.extension.lower() in CONTENT_SNIFF_EXTENSIONS:
                refined = refine_language(scan.root / entry.path, entry.extension.lower())
                if refined is not None:
                    language = refined
            counts[language] += 1
            sizes[language] += entry.size

        return [
            LanguageStat(language=language, files=count, total_size=sizes[language])
            for language, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)
        ]
