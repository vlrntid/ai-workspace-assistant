"""Custom exceptions used across the package.

Defining explicit error types lets the CLI layer catch and report failures precisely
instead of swalling every `Exception`, and makes the public API intention-revealing.
"""

from __future__ import annotations


class ScanError(Exception):
    """Raised when a project cannot be scanned (missing path, not a directory, ...)."""


class ReportError(Exception):
    """Raised when a report cannot be built or rendered."""
