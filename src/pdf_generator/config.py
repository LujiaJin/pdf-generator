#!/usr/bin/env python3
"""
PDF生成配置模块
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional


@dataclass
class MarginConfig:
    """边距配置"""
    top: int = 90
    bottom: int = 72
    left: int = 72
    right: int = 72


@dataclass
class HeaderConfig:
    """页眉配置"""
    enabled: bool = True
    font_size: int = 8
    color: str = "gray"
    separator: bool = True
    left_text: str = "文档"
    right_text: str = "生成时间"


@dataclass
class FooterConfig:
    """页脚配置"""
    enabled: bool = True
    font_size: int = 9
    color: str = "darkgrey"
    text: str = "页"
    margin: int = 40


@dataclass
class StyleItemConfig:
    """单个样式项配置"""
    font_size: Optional[int] = None
    color: Optional[str] = None
    space_before: Optional[int] = None
    space_after: Optional[int] = None
    alignment: Optional[str] = None
    leading: Optional[int] = None
    font_name: Optional[str] = None


@dataclass
class StyleConfig:
    """样式配置"""
    title: Dict[str, Any] = field(default_factory=lambda: {
        "font_size": 24,
        "color": "#1a237e",
        "space_before": 40,
        "space_after": 30,
        "alignment": "center"
    })
    
    heading1: Dict[str, Any] = field(default_factory=lambda: {
        "font_size": 18,
        "color": "#283593",
        "space_before": 25,
        "space_after": 15
    })
    
    heading2: Dict[str, Any] = field(default_factory=lambda: {
        "font_size": 16,
        "color": "#3949ab",
        "space_before": 15,
        "space_after": 10
    })
    
    heading3: Dict[str, Any] = field(default_factory=lambda: {
        "font_size": 14,
        "color": "#5c6bc0",
        "space_before": 10,
        "space_after": 8
    })
    
    body_text: Dict[str, Any] = field(default_factory=lambda: {
        "font_size": 12,
        "leading": 18,
        "space_after": 6
    })
    
    emphasis: Dict[str, Any] = field(default_factory=lambda: {
        "font_size": 12,
        "color": "#33691e",
        "space_after": 8
    })
    
    quote: Dict[str, Any] = field(default_factory=lambda: {
        "font_size": 11,
        "color": "#795548",
        "space_before": 10,
        "space_after": 10,
        "leftIndent": 20
    })


@dataclass
class PDFConfig:
    """PDF生成配置"""
    page_size: str = "A4"
    margins: MarginConfig = field(default_factory=MarginConfig)
    header: HeaderConfig = field(default_factory=HeaderConfig)
    footer: FooterConfig = field(default_factory=FooterConfig)


# 默认配置
DEFAULT_CONFIG = {
    "page_size": "A4",
    "margins": {
        "top": 90,
        "bottom": 72,
        "left": 72,
        "right": 72
    },
    "header": {
        "enabled": True,
        "font_size": 8,
        "color": "gray",
        "separator": True,
        "left_text": "文档",
        "right_text": "生成时间"
    },
    "footer": {
        "enabled": True,
        "font_size": 9,
        "color": "darkgrey",
        "text": "页",
        "margin": 40
    }
}

DEFAULT_STYLES = {
    "title": {
        "font_size": 24,
        "color": "#1a237e",
        "space_before": 40,
        "space_after": 30,
        "alignment": "center"
    },
    "heading1": {
        "font_size": 18,
        "color": "#283593",
        "space_before": 25,
        "space_after": 15
    },
    "heading2": {
        "font_size": 16,
        "color": "#3949ab",
        "space_before": 15,
        "space_after": 10
    },
    "heading3": {
        "font_size": 14,
        "color": "#5c6bc0",
        "space_before": 10,
        "space_after": 8
    },
    "body_text": {
        "font_size": 12,
        "leading": 18,
        "space_after": 6
    },
    "emphasis": {
        "font_size": 12,
        "color": "#33691e",
        "space_after": 8
    },
    "quote": {
        "font_size": 11,
        "color": "#795548",
        "space_before": 10,
        "space_after": 10,
        "leftIndent": 20
    }
}


def load_config(config_file: str) -> PDFConfig:
    """从JSON文件加载配置"""
    import json
    with open(config_file, 'r', encoding='utf-8') as f:
        config_data = json.load(f)
    return PDFConfig(**config_data)


def save_config(config: PDFConfig, config_file: str):
    """保存配置到JSON文件"""
    import json
    
    def dataclass_to_dict(obj):
        if isinstance(obj, (MarginConfig, HeaderConfig, FooterConfig)):
            return {k: v for k, v in obj.__dict__.items() if not k.startswith('_')}
        elif isinstance(obj, PDFConfig):
            result = {}
            for k, v in obj.__dict__.items():
                if not k.startswith('_'):
                    if hasattr(v, '__dict__'):
                        result[k] = dataclass_to_dict(v)
                    else:
                        result[k] = v
            return result
        return obj
    
    config_dict = dataclass_to_dict(config)
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)