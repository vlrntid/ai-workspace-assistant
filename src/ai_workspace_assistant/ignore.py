"""Parse and match .gitignore-style ignore rules.

This implements a pragmatic subset of gitignore semantics so the scanner can honor a
project's own ignore file (plus `.git/info/exclude`) instead of only the built-in
list. Supported features:

* blank lines and `#` comments are ignored,
* `*` / `?` / `**` wildcards,
* a leading `/` anchors a pattern to the project root,
* a trailing `/` limits a pattern to directories only,
* a `!` prefix negates (re-includes) a previously ignored path.

Later rules override earlier ones, including negations — matching git's behavior.
Only the project-root `.gitignore` is read (nested `.gitignore` files are not).
"""

from __future__ import annotations

import re
from pathlib import Path
from re import Pattern


class GitignoreMatcher:
    """Decides whether a path (relative to the project root) should be ignored."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._rules: list[tuple[Pattern[str], bool, bool]] = []
        self._load(root / ".gitignore")
        self._load(root / ".git" / "info" / "exclude")

    def _load(self, path: Path) -> None:
        if not path.is_file():
            return
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            return
        for raw in text.splitlines():
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            negated = stripped.startswith("!")
            if negated:
                stripped = stripped[1:]
            dir_only = stripped.endswith("/")
            if dir_only:
                stripped = stripped[:-1]
            anchored = stripped.startswith("/")
            if anchored:
                stripped = stripped[1:]
            if not stripped:
                continue

            self._rules.append((self._compile(stripped, anchored), negated, dir_only))

    @staticmethod
    def _compile(pattern: str, anchored: bool) -> Pattern[str]:
        parts = pattern.split("/")
        out: list[str] = []
        for index, part in enumerate(parts):
            if part == "**":
                out.append("(?:.*/)?")
                continue
            escaped = re.escape(part).replace(r"\*", "[^/]*").replace(r"\?", "[^/]")
            out.append(escaped)
            if index < len(parts) - 1:
                out.append("/")
        body = "".join(out)
        if anchored:
            return re.compile("^" + body + "(?:/.*)?$")
        # Basename-style patterns match at any directory depth.
        return re.compile("^(?:.*/)?" + body + "(?:/.*)?$")

    def is_ignored(self, relative_path: Path, is_dir: bool = False) -> bool:
        rel = str(relative_path).replace("\\", "/")
        ignored = False
        for regex, negated, dir_only in self._rules:
            if dir_only and not is_dir:
                continue
            if regex.match(rel):
                ignored = not negated
        return ignored
