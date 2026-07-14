"""Analyzer registry.

An *analyzer* turns a `ScanResult` into a statistic. To add a new metric (e.g. a TODO
counter or a license detector), implement the `Analyzer` protocol and append an
instance to `ANALYZERS` — nothing else in the app needs to change.
"""

from __future__ import annotations

from ai_workspace_assistant.analyzers.base import Analyzer
from ai_workspace_assistant.analyzers.extensions import ExtensionAnalyzer
from ai_workspace_assistant.analyzers.languages import LanguageAnalyzer

ANALYZERS: list[Analyzer] = [
    ExtensionAnalyzer(),
    LanguageAnalyzer(),
]

__all__ = ["ANALYZERS", "Analyzer", "ExtensionAnalyzer", "LanguageAnalyzer"]
