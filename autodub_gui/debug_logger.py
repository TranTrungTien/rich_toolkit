"""Global debugging logger for showing errors and tracebacks in a UI panel."""
from __future__ import annotations

import traceback

from PySide6.QtCore import QObject, Signal


class _DebugLogger(QObject):
    """Shared object to broadcast debug messages to the UI."""
    message_logged = Signal(str, str)  # level, message

    def log(self, level: str, message: str) -> None:
        self.message_logged.emit(level, message)

    def log_exception(self, label: str, exc: Exception) -> None:
        tb = traceback.format_exc()
        msg = f"<b>{label}</b>: {exc}<br/><pre style='font-size: 11px;'>{tb}</pre>"
        self.log("ERROR", msg)

    def info(self, message: str) -> None:
        self.log("INFO", message)

    def error(self, message: str) -> None:
        self.log("ERROR", message)

# Singleton instance
DEBUG_LOG = _DebugLogger()
