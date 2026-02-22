#!/usr/bin/env python3
"""
字体管理模块
处理中文字体的检测和注册
"""

import os
import platform
from typing import List, Dict, Optional, Tuple
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FontManager:
    """字体管理器"""
    
    def __init__(self, debug: bool = False):
        self.debug = debug
        self.registered_fonts = {}
        self.chinese_font_available = False
        
    def log(self, message: str):
        """日志记录"""
        if self.debug:
            print(f"[字体管理器] {message}")
    
    def get_system_font_paths(self) -> List[str]:
        """
        获取系统字体路径
        
        Returns:
            字体文件路径列表
        """
        system = platform.system()
        font_paths = []
        
        if system == "Windows":
            # Windows系统字体路径
            windows_fonts_dir = os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'Fonts')
            font_paths = [
                os.path.join(windows_fonts_dir, 'msyh.ttc'),      # 微软雅黑
                os.path.join(windows_fonts_dir, 'msyhl.ttc'),     # 微软雅黑 Light
                os.path.join(windows_fonts_dir, 'simhei.ttf'),    # 黑体
                os.path.join(windows_fonts_dir, 'simsun.ttc'),    # 宋体
                os.path.join(windows_fonts_dir, 'Deng.ttf'),      # 等线
                os.path.join(windows_fonts_dir, 'simfang.ttf'),   # 仿宋
                os.path.join(windows_fonts_dir, 'simkai.ttf'),    # 楷体
                os.path.join(windows_fonts_dir, 'msjh.ttc'),      # 微软正黑体
                os.path.join(windows_fonts_dir, 'msjhl.ttc'),     # 微软正黑体 Light
            ]
            
        elif system == "Darwin":  # macOS
            mac_fonts_dirs = [
                '/Library/Fonts',
                '/System/Library/Fonts',
                os.path.expanduser('~/Library/Fonts')
            ]
            
            # 常见的中文字体文件
            chinese_font_patterns = [
                'PingFang.ttc',      # 苹方
                'Hiragino Sans GB.ttc',  # 冬青黑体
                'STHeiti Light.ttc', # 华文黑体
                'STHeiti Medium.ttc',
                'STSong.ttf',        # 华文宋体
                'STKaiti.ttf',       # 华文楷体
            ]
            
            for fonts_dir in mac_fonts_dirs:
                if os.path.exists(fonts_dir):
                    for pattern in chinese_font_patterns:
                        font_path = os.path.join(fonts_dir, pattern)
                        if os.path.exists(font_path):
                            font_paths.append(font_path)
                            
        elif system == "Linux":
            linux_fonts_dirs = [
                '/usr/share/fonts',
                '/usr/local/share/fonts',
                os.path.expanduser('~/.fonts'),
                os.path.expanduser('~/.local/share/fonts')
            ]
            
            # Linux常见中文字体
            chinese_font_patterns = [
                'wqy-*.ttf',         # 文泉驿
                'noto-cjk-*.ttf',    # Noto CJK
                'droid-sans-fallback.ttf',
            ]
            
            import glob
            for fonts_dir in linux_fonts_dirs:
                if os.path.exists(fonts_dir):
                    for pattern in chinese_font_patterns:
                        matched = glob.glob(os.path.join(fonts_dir, '**', pattern), recursive=True)
                        font_paths.extend(matched)
        
        # 过滤掉不存在的路径
        existing_paths = [path for path in font_paths if os.path.exists(path)]
        
        self.log(f"发现 {len(existing_paths)} 个可能的中文字体文件")
        return existing_paths
    
    def register_font(self, font_path: str, font_name: str = "ChineseFont") -> bool:
        """
        注册单个字体
        
        Args:
            font_path: 字体文件路径
            font_name: 注册的字体名称
            
        Returns:
            是否注册成功
        """
        try:
            if font_path.endswith('.ttc'):
                # TrueType Collection文件，需要指定字体索引
                pdfmetrics.registerFont(TTFont(font_name, font_path, 0))
            else:
                # 普通的TTF或OTF文件
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            
            self.registered_fonts[font_name] = font_path
            self.log(f"成功注册字体: {font_name} -> {os.path.basename(font_path)}")
            return True
            
        except Exception as e:
            self.log(f"注册字体失败 {font_path}: {e}")
            return False
    
    def register_system_fonts(self) -> bool:
        """
        注册系统字体
        
        Returns:
            是否成功注册了中文字体
        """
        self.log("开始检测和注册系统字体...")
        
        font_paths = self.get_system_font_paths()
        
        if not font_paths:
            self.log("未找到系统字体，将使用默认字体")
            self.chinese_font_available = False
            return False
        
        # 尝试注册每个找到的字体
        success = False
        for font_path in font_paths:
            font_name = f"ChineseFont_{len(self.registered_fonts)}"
            if self.register_font(font_path, font_name):
                success = True
                self.chinese_font_available = True
                # 第一个成功就使用它
                break
        
        if success:
            self.log("中文字体注册成功")
        else:
            self.log("所有字体注册都失败，将使用默认字体")
            self.chinese_font_available = False
        
        return success
    
    def register_custom_font(self, font_path: str) -> bool:
        """
        注册自定义字体
        
        Args:
            font_path: 自定义字体文件路径
            
        Returns:
            是否注册成功
        """
        if not os.path.exists(font_path):
            self.log(f"自定义字体文件不存在: {font_path}")
            return False
        
        font_name = f"CustomFont_{len(self.registered_fonts)}"
        success = self.register_font(font_path, font_name)
        
        if success:
            self.chinese_font_available = True
            
        return success
    
    def get_registered_fonts(self) -> Dict[str, str]:
        """获取已注册的字体"""
        return self.registered_fonts.copy()
    
    def has_chinese_font(self) -> bool:
        """检查是否有可用的中文字体"""
        return self.chinese_font_available
    
    def get_primary_font_name(self) -> str:
        """获取主要字体名称"""
        if self.registered_fonts:
            return list(self.registered_fonts.keys())[0]
        else:
            return "Helvetica"  # 默认字体
    
    def cleanup(self):
        """清理资源"""
        self.registered_fonts.clear()
        self.chinese_font_available = False
        self.log("字体管理器已清理")