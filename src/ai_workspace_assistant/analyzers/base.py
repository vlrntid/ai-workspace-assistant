"""The analyzer protocol — the extension point for new project metrics."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from ai_workspace_assistant.models import ScanResult


@runtime_checkable
class Analyzer(Protocol):
    """Produces a statistic from a completed scan.

    Implementations expose a `name` (used as the key in `ProjectReport.analyses`) and
    an `analyze` method that returns the computed result. The return type is intentionally
    left open so analyzers can emit any structured value.
    """

    name: str

    def analyze(self, scan: ScanResult) -> Any: ...
