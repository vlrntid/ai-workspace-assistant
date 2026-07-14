"""Project-wide configuration: ignore rules and the extension -> language map.

Centralizing these here keeps the scanning/analysis logic free of magic values and
makes the behavior easy to extend or override from a single place.
"""

from __future__ import annotations

# Directory names that are skipped during a scan. These are matched exactly against
# directory names discovered while walking the tree (e.g. `node_modules`, `.git`).
DEFAULT_IGNORES: frozenset[str] = frozenset(
    {
        # Version control
        ".git",
        ".hg",
        ".svn",
        # Python environments / caches
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        ".tox",
        ".nox",
        # JavaScript / Node
        "node_modules",
        # Build artifacts
        "dist",
        "build",
        ".eggs",
        # Editor metadata
        ".idea",
        ".vscode",
    }
)

# Maps a lower-cased file extension to a human-readable language label.
# Unknown extensions are grouped under "Other" by the language analyzer.
EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".h": "C/C++ Header",
    ".cpp": "C++",
    ".cc": "C++",
    ".cxx": "C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".rb": "Ruby",
    ".php": "PHP",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".kts": "Kotlin",
    ".scala": "Scala",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "Sass",
    ".sass": "Sass",
    ".less": "Less",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".ini": "INI",
    ".cfg": "INI",
    ".md": "Markdown",
    ".rst": "reStructuredText",
    ".txt": "Text",
    ".xml": "XML",
    ".sql": "SQL",
    ".ipynb": "Jupyter Notebook",
    ".r": "R",
    ".pl": "Perl",
    ".lua": "Lua",
    ".dart": "Dart",
    ".vim": "Vim Script",
}

# Registry keys used to store analyzer output inside a ProjectReport. Kept here (rather
# than in the analyzer modules) to avoid an import cycle between models and analyzers.
EXTENSION_ANALYZER_NAME = "extensions"
LANGUAGE_ANALYZER_NAME = "languages"
TODO_ANALYZER_NAME = "todos"
