"""Reporter registry.

A *reporter* turns a `ProjectReport` into a string in some format. To support a new
output (JSON, HTML, ...), implement the `Reporter` protocol and add an instance to
`REPORTERS`; the CLI exposes it automatically via `--format`.
"""

from __future__ import annotations

from ai_workspace_assistant.reporters.base import Reporter
from ai_workspace_assistant.reporters.markdown import MarkdownReporter

REPORTERS: list[Reporter] = [
    MarkdownReporter(),
]

__all__ = ["REPORTERS", "MarkdownReporter", "Reporter"]
