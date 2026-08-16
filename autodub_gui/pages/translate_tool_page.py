"""Trang Dịch thuật — cấu hình Gemini, OpenRouter, DeepSeek và VoxDub.

Tách phần Dịch thuật của trang Cài đặt ra thành trang riêng. Gồm chọn provider,
API Key, model và các tham số dịch (phong cách, xưng hô, thuật ngữ).
"""
from __future__ import annotations

from autodub_gui.pages import settings_fields as spec
from autodub_gui.pages.tool_page_base import ToolPage


class TranslateToolPage(ToolPage):
    """Cấu hình dịch thuật qua các dịch vụ AI."""

    TAB = spec.TAB_TRANSLATE
    TITLE = "Dịch thuật"
    SUBTITLE = ("Configure Gemini, OpenRouter, DeepSeek or VoxDub. API keys are masked; "
                "model and Base URL accept custom values.")
    EXPANDED = {"Provider", "Common parameters"}  # noqa: RUF012
    SAVE_LABEL = "Lưu cấu hình dịch"
    SAVED_TOAST = "Đã lưu cấu hình dịch."
