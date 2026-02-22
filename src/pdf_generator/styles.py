#!/usr/bin/env python3
"""
样式管理模块
管理PDF文档的样式配置
"""

from typing import Dict, Any, Optional
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

from .config import StyleConfig


class StyleManager:
    """样式管理器"""
    
    def __init__(self, style_config: StyleConfig, debug: bool = False):
        self.style_config = style_config
        self.debug = debug
        self.styles_cache = {}
        
    def log(self, message: str):
        """日志记录"""
        if self.debug:
            print(f"[样式管理器] {message}")
    
    def _get_alignment(self, alignment_str: Optional[str]):
        """将对齐字符串转换为reportlab对齐方式"""
        if alignment_str is None:
            return TA_LEFT
        
        alignment_map = {
            "left": TA_LEFT,
            "center": TA_CENTER,
            "right": TA_RIGHT,
            "justify": TA_JUSTIFY,
        }
        
        return alignment_map.get(alignment_str.lower(), TA_LEFT)
    
    def _get_color(self, color_str: Optional[str]):
        """将颜色字符串转换为颜色对象"""
        if color_str is None:
            return colors.black
            
        if color_str.startswith('#'):
            # 十六进制颜色
            return colors.HexColor(color_str)
        else:
            # 命名的颜色
            try:
                return getattr(colors, color_str, colors.black)
            except:
                return colors.black
    
    def _apply_style_config(self, style: ParagraphStyle, config: Dict[str, Any], 
                           base_font: str, base_bold_font: str):
        """应用样式配置到ParagraphStyle"""
        if "font_size" in config:
            style.fontSize = config["font_size"]
            
        if "color" in config:
            style.textColor = self._get_color(config["color"])
            
        if "space_before" in config:
            style.spaceBefore = config["space_before"]
            
        if "space_after" in config:
            style.spaceAfter = config["space_after"]
            
        if "alignment" in config:
            style.alignment = self._get_alignment(config["alignment"])
            
        if "leading" in config:
            style.leading = config["leading"]
            
        if "font_name" in config:
            style.fontName = config["font_name"]
        elif "bold" in config and config.get("bold"):
            style.fontName = base_bold_font
        else:
            style.fontName = base_font
            
        # 其他可能属性
        for attr in ["leftIndent", "rightIndent", "firstLineIndent", "backColor"]:
            if attr in config:
                setattr(style, attr, config[attr])
    
    def create_styles(self, has_chinese_font: bool = False) -> Any:
        """
        创建样式表
        
        Args:
            has_chinese_font: 是否注册了中文字体
            
        Returns:
            样式表对象
        """
        self.log("创建样式表...")
        
        cache_key = f"chinese_{has_chinese_font}"
        if cache_key in self.styles_cache:
            self.log("使用缓存的样式表")
            return self.styles_cache[cache_key]
        
        # 获取基础样式表
        styles = getSampleStyleSheet()
        
        # 基础字体设置
        if has_chinese_font:
            base_font = "ChineseFont"
            base_bold_font = "ChineseFont"  # 中文字体通常没有单独的粗体
        else:
            base_font = "Helvetica"
            base_bold_font = "Helvetica-Bold"
        
        # 创建自定义样式
        
        # 标题样式
        title_style = ParagraphStyle(
            name='ChineseTitle',
            parent=styles['Title'],
            fontName=base_bold_font
        )
        self._apply_style_config(title_style, self.style_config.title, base_font, base_bold_font)
        styles.add(title_style)
        
        # 一级标题
        heading1_style = ParagraphStyle(
            name='ChineseHeading1',
            parent=styles['Heading1'],
            fontName=base_bold_font
        )
        self._apply_style_config(heading1_style, self.style_config.heading1, base_font, base_bold_font)
        styles.add(heading1_style)
        
        # 二级标题
        heading2_style = ParagraphStyle(
            name='ChineseHeading2',
            parent=styles['Heading2'],
            fontName=base_bold_font
        )
        self._apply_style_config(heading2_style, self.style_config.heading2, base_font, base_bold_font)
        styles.add(heading2_style)
        
        # 三级标题
        heading3_style = ParagraphStyle(
            name='ChineseHeading3',
            parent=styles['Heading3'],
            fontName=base_bold_font
        )
        self._apply_style_config(heading3_style, self.style_config.heading3, base_font, base_bold_font)
        styles.add(heading3_style)
        
        # 四级标题
        heading4_style = ParagraphStyle(
            name='ChineseHeading4',
            parent=styles['Heading4'],
            fontName=base_bold_font
        )
        self._apply_style_config(heading4_style, {
            "font_size": 12,
            "color": "#7986cb",
            "space_before": 8,
            "space_after": 6
        }, base_font, base_bold_font)
        styles.add(heading4_style)
        
        # 五级标题
        heading5_style = ParagraphStyle(
            name='ChineseHeading5',
            parent=styles['Heading5'],
            fontName=base_bold_font
        )
        self._apply_style_config(heading5_style, {
            "font_size": 11,
            "color": "#9fa8da",
            "space_before": 6,
            "space_after": 4
        }, base_font, base_bold_font)
        styles.add(heading5_style)
        
        # 正文样式
        body_style = ParagraphStyle(
            name='ChineseBodyText',
            parent=styles['Normal'],
            fontName=base_font
        )
        self._apply_style_config(body_style, self.style_config.body_text, base_font, base_bold_font)
        styles.add(body_style)
        
        # 强调文本样式
        emphasis_style = ParagraphStyle(
            name='ChineseEmphasis',
            parent=styles['Normal'],
            fontName=base_bold_font
        )
        self._apply_style_config(emphasis_style, self.style_config.emphasis, base_font, base_bold_font)
        styles.add(emphasis_style)
        
        # 引用样式
        quote_style = ParagraphStyle(
            name='ChineseQuote',
            parent=styles['Italic'],
            fontName=base_font
        )
        self._apply_style_config(quote_style, self.style_config.quote, base_font, base_bold_font)
        styles.add(quote_style)
        
        # 代码样式
        code_style = ParagraphStyle(
            name='ChineseCode',
            parent=styles['Code'],
            fontName='Courier',
            fontSize=10,
            textColor=colors.HexColor('#37474f'),
            backColor=colors.HexColor('#f5f5f5'),
            leftIndent=10,
            rightIndent=10,
            spaceBefore=8,
            spaceAfter=8
        )
        styles.add(code_style)
        
        # 缓存样式表
        self.styles_cache[cache_key] = styles
        self.log(f"样式表创建完成，包含 {len(styles.byName)} 个样式")
        
        return styles
    
    def update_style_config(self, style_type: str, config_updates: Dict[str, Any]):
        """
        更新样式配置
        
        Args:
            style_type: 样式类型，如 'title', 'heading1' 等
            config_updates: 配置更新字典
        """
        if hasattr(self.style_config, style_type):
            current_config = getattr(self.style_config, style_type)
            if isinstance(current_config, dict):
                current_config.update(config_updates)
                setattr(self.style_config, style_type, current_config)
                self.log(f"更新样式配置: {style_type}")
                
                # 清除缓存
                self.styles_cache.clear()
            else:
                self.log(f"样式配置 {style_type} 不是字典类型")
        else:
            self.log(f"未知的样式类型: {style_type}")
    
    def create_custom_style(self, name: str, base_style: str = "Normal", **kwargs) -> ParagraphStyle:
        """
        创建自定义样式
        
        Args:
            name: 样式名称
            base_style: 基础样式名称
            **kwargs: 样式属性
            
        Returns:
            创建的样式对象
        """
        styles = getSampleStyleSheet()
        
        if base_style in styles.byName:
            parent_style = styles[base_style]
        else:
            parent_style = styles['Normal']
            self.log(f"基础样式 {base_style} 不存在，使用 Normal")
        
        custom_style = ParagraphStyle(name=name, parent=parent_style)
        
        # 应用提供的属性
        for key, value in kwargs.items():
            if hasattr(custom_style, key):
                setattr(custom_style, key, value)
            else:
                self.log(f"样式属性 {key} 不存在，跳过")
        
        return custom_style
    
    def get_style_names(self) -> list:
        """获取所有样式名称"""
        styles = getSampleStyleSheet()
        return list(styles.byName.keys())