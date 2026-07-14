"""Progress reporting abstraction.

Scanning can touch many files, so the scanner accepts a `Progress` object it ticks as
it goes. The CLI plugs in a TTY-aware bar; tests and non-interactive runs use a no-op
implementation. Decoupling display from logic keeps both testable.
"""

from __future__ import annotations

import sys
from typing import IO, Protocol, runtime_checkable


@runtime_checkable
class Progress(Protocol):
    """Anything the scanner can tick while it works."""

    def update(self, n: int = 1) -> None: ...

    def finish(self) -> None: ...


class NullProgress:
    """A progress sink that does nothing. Used for quiet/non-TTY runs and tests."""

    def update(self, n: int = 1) -> None:
        return None

    def finish(self) -> None:
        return None


class TtyProgress:
    """A minimal single-line progress indicator written to stderr."""

    def __init__(self, stream: IO[str] = sys.stderr, width: int = 40) -> None:
        self._stream = stream
        self._width = width
        self._count = 0
        self._shown = False

    def update(self, n: int = 1) -> None:
        self._count += n
        self._stream.write(f"\rScanning… {self._count} files")
        self._stream.flush()
        self._shown = True

    def finish(self) -> None:
        if self._shown:
            self._stream.write(f"\rScanning… {self._count} files done.\n")
            self._stream.flush()
