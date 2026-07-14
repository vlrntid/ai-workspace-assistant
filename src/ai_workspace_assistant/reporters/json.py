"""Renders a `ProjectReport` as JSON, for machine consumption / piping into other tools."""

from __future__ import annotations

import json
from dataclasses import asdict

from ai_workspace_assistant.config import TODO_ANALYZER_NAME
from ai_workspace_assistant.models import ProjectReport


class JsonReporter:
    """Produces a JSON document describing the scanned project."""

    format = "json"

    def render(self, report: ProjectReport) -> str:
        scan = report.scan
        payload = {
            "root": str(scan.root),
            "generated_at": report.generated_at.isoformat(),
            "summary": {
                "total_files": scan.total_files,
                "total_size": scan.total_size,
                "scanned_dirs": scan.scanned_dirs,
                "languages_detected": len(report.get_languages()),
            },
            "languages": [asdict(language) for language in report.get_languages()],
            "extensions": [asdict(extension) for extension in report.get_extensions()],
            "warnings": list(scan.warnings),
        }

        todos = report.analyses.get(TODO_ANALYZER_NAME)
        if todos is not None:
            payload["todos"] = asdict(todos)

        return json.dumps(payload, indent=2)
