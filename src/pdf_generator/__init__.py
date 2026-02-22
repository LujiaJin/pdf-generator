"""
PDF生成器模块
专业的中文PDF文档生成工具
"""

from .core import PDFGenerator
from .config import PDFConfig, StyleConfig
from .fonts import FontManager
from .styles import StyleManager
from .cli import main as cli_main

__version__ = "1.0.0"
__all__ = [
    "PDFGenerator",
    "PDFConfig", 
    "StyleConfig",
    "FontManager",
    "StyleManager",
    "cli_main"
]