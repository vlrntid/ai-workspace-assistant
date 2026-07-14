"""Command-line interface and orchestration.

This module is the only place that touches `sys.argv` and process exit codes. It wires
together scanning, analysis, and reporting so the rest of the package stays testable
from plain Python.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from ai_workspace_assistant.analyzers import ANALYZERS, Analyzer
from ai_workspace_assistant.config import DEFAULT_IGNORES
from ai_workspace_assistant.errors import ScanError
from ai_workspace_assistant.models import ProjectReport, ScanResult, utcnow
from ai_workspace_assistant.progress import NullProgress, Progress, TtyProgress
from ai_workspace_assistant.reporters import REPORTERS, Reporter
from ai_workspace_assistant.scanner import scan_project

__version__ = "0.1.2"


def build_parser() -> argparse.ArgumentParser:
    """Construct the argument parser. Choices for ``--format`` come from the registry."""
    parser = argparse.ArgumentParser(
        prog="aiwa",
        description="Analyze a software project and generate a useful report.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Project directory to scan (default: current directory)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write the report to this file instead of stdout",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=[reporter.format for reporter in REPORTERS],
        default="markdown",
        help="Report format (default: markdown)",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress progress output",
    )
    parser.add_argument(
        "--ignore",
        nargs="*",
        default=[],
        metavar="DIR",
        help="Additional directory names to ignore",
    )
    parser.add_argument(
        "--no-gitignore",
        action="store_true",
        help="Do not honor the project's .gitignore / .git/info/exclude",
    )
    parser.add_argument(
        "--no-default-ignores",
        action="store_true",
        help="Disable the built-in ignore list",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def build_report(
    scan: ScanResult,
    analyzers: Sequence[Analyzer] | None = None,
) -> ProjectReport:
    """Run every analyzer over the scan and package the results into a report."""
    selected = list(analyzers) if analyzers is not None else list(ANALYZERS)
    analyses: dict[str, object] = {analyzer.name: analyzer.analyze(scan) for analyzer in selected}
    return ProjectReport(scan=scan, analyses=analyses, generated_at=utcnow())


def _select_reporter(fmt: str) -> Reporter:
    for reporter in REPORTERS:
        if reporter.format == fmt:
            return reporter
    raise ScanError(f"No reporter registered for format: {fmt}")


def _print_error(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)


def main(argv: Sequence[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code (0 = success, 2 = fatal error)."""
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.path)
    ignores = set() if args.no_default_ignores else set(DEFAULT_IGNORES)
    ignores.update(args.ignore)

    progress: Progress = (
        NullProgress() if (args.quiet or not sys.stdout.isatty()) else TtyProgress()
    )

    try:
        scan = scan_project(
            root, ignores=ignores, progress=progress, use_gitignore=not args.no_gitignore
        )
    except ScanError as exc:
        _print_error(str(exc))
        return 2

    report = build_report(scan)
    reporter = _select_reporter(args.format)
    rendered = reporter.render(report)

    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
