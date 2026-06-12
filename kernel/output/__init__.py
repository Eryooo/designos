"""Output renderer dispatch."""

from __future__ import annotations

from .excel import ExcelStubRenderer
from .html import HTMLRenderer
from .markdown import MarkdownRenderer
from .renderer import OutputRenderer

__all__ = ["ExcelStubRenderer", "HTMLRenderer", "MarkdownRenderer", "OutputRenderer"]
