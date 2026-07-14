"""The reporter protocol — the extension point for new output formats."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from ai_workspace_assistant.models import ProjectReport


@runtime_checkable
class Reporter(Protocol):
    """Renders a `ProjectReport` to a string in a particular format."""

    format: str

    def render(self, report: ProjectReport) -> str: ...
