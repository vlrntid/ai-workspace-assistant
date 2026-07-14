# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-14

### Added
- CLI (`aiwa`) that scans a project directory and reports on it.
- Built-in ignore list (`.git`, `.venv`, `node_modules`, `__pycache__`, and more).
- File counting grouped by extension.
- Programming-language detection from file extensions.
- Markdown report generation, written to stdout or a file.
- Live scan progress on TTYs, suppressed with `--quiet`.
- Graceful handling of unreadable files (recorded as warnings).
- Pluggable analyzer and reporter registries for easy extension.
