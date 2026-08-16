"""A small, dockable or overlay console for debugging."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from autodub_gui import tokens
from autodub_gui.debug_logger import DEBUG_LOG


class DebugConsole(QWidget):
    """Floating debug console that listens to DEBUG_LOG signals."""

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowStaysOnTopHint)
        self.setWindowTitle("VoxDub Debug Console")
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet(f"background: {tokens.BG_SIDEBAR}; border-bottom: 1px solid {tokens.BORDER_SUBTLE};")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(12, 4, 12, 4)
        
        title = QLabel("System Debug Log")
        title.setStyleSheet(f"color: {tokens.TEXT_PRIMARY}; font-weight: bold;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        clear_btn = QPushButton("Clear")
        clear_btn.setFlat(True)
        clear_btn.setStyleSheet(f"color: {tokens.TEXT_MUTED};")
        clear_btn.clicked.connect(self.clear)
        header_layout.addWidget(clear_btn)
        
        layout.addWidget(header)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setStyleSheet(f"background: {tokens.BG_APP}; color: {tokens.TEXT_SECONDARY}; font-family: monospace; border: none;")
        layout.addWidget(self.text)

        DEBUG_LOG.message_logged.connect(self.append_message)

    def append_message(self, level: str, message: str) -> None:
        color = tokens.PRIMARY if level == "INFO" else tokens.DANGER
        self.text.append(f"<span style='color: {color}; font-weight: bold;'>[{level}]</span> {message}")
        # Scroll to bottom
        sb = self.text.verticalScrollBar()
        sb.setValue(sb.maximum())

    def clear(self) -> None:
        self.text.clear()

    def show_toggle(self) -> None:
        if self.isVisible():
            self.hide()
        else:
            self.show()
            self.raise_()
            self.activateWindow()
