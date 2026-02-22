#!/usr/bin/env python3
"""
PDF生成器核心模块
基于优化后的reportlab实现，支持中文和专业格式
"""

import os
import re
import datetime
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Union, Any
import markdown2

from reportlab.lib.pagesizes import A4, letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

from .config import PDFConfig, StyleConfig, DEFAULT_CONFIG, DEFAULT_STYLES
from .fonts import FontManager
from .styles import StyleManager


class PDFGenerator:
    """PDF生成器主类"""
    
    def __init__(self, config: Optional[Union[PDFConfig, Dict]] = None, 
                 styles: Optional[Union[StyleConfig, Dict]] = None,
                 debug: bool = False):
        """
        初始化PDF生成器
        
        Args:
            config: PDF配置，可以是PDFConfig对象或字典
            styles: 样式配置，可以是StyleConfig对象或字典
            debug: 是否启用调试模式
        """
        self.debug = debug
        self.logger = self._setup_logger()
        
        # 初始化配置
        if config is None:
            self.config = PDFConfig(**DEFAULT_CONFIG)
        elif isinstance(config, dict):
            self.config = PDFConfig(**config)
        else:
            self.config = config
            
        # 初始化样式
        if styles is None:
            self.styles_config = StyleConfig(**DEFAULT_STYLES)
        elif isinstance(styles, dict):
            self.styles_config = StyleConfig(**styles)
        else:
            self.styles_config = styles
        
        # 初始化管理器
        self.font_manager = FontManager(debug=debug)
        self.style_manager = StyleManager(self.styles_config, debug=debug)
        
        self.logger("PDF生成器初始化完成")
        
    def _setup_logger(self):
        """设置日志记录器"""
        if self.debug:
            def debug_logger(msg):
                print(f"[DEBUG] {msg}")
            return debug_logger
        else:
            def silent_logger(msg):
                pass
            return silent_logger
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        检查依赖库是否可用
        
        Returns:
            依赖检查结果字典
        """
        self.logger("检查依赖库...")
        
        dependencies = {
            "reportlab": False,
            "markdown2": False,
        }
        
        try:
            import reportlab
            dependencies["reportlab"] = True
            self.logger(f"reportlab版本: {reportlab.__version__}")
        except ImportError:
            self.logger("错误: reportlab库未安装")
            
        try:
            import markdown2
            dependencies["markdown2"] = True
            self.logger(f"markdown2版本: {markdown2.__version__}")
        except ImportError:
            self.logger("错误: markdown2库未安装")
            
        all_ok = all(dependencies.values())
        dependencies["all_ok"] = all_ok
        
        if all_ok:
            self.logger("所有依赖库检查通过")
        else:
            self.logger("警告: 部分依赖库缺失")
            
        return dependencies
    
    def convert_md_to_pdf(self, input_file: str, output_file: str, 
                          options: Optional[Dict] = None) -> Dict[str, Any]:
        """
        将Markdown文件转换为PDF
        
        Args:
            input_file: 输入Markdown文件路径
            output_file: 输出PDF文件路径
            options: 额外选项
            
        Returns:
            转换结果字典
        """
        self.logger(f"开始转换: {input_file} -> {output_file}")
        
        try:
            # 检查输入文件
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"输入文件不存在: {input_file}")
            
            # 读取Markdown内容
            with open(input_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # 注册字体
            has_chinese_font = self.font_manager.register_system_fonts()
            
            # 创建PDF文档
            page_size = self._get_page_size(self.config.page_size)
            doc = SimpleDocTemplate(
                output_file,
                pagesize=page_size,
                rightMargin=self.config.margins.right,
                leftMargin=self.config.margins.left,
                topMargin=self.config.margins.top,
                bottomMargin=self.config.margins.bottom
            )
            
            # 创建样式
            styles = self.style_manager.create_styles(has_chinese_font)
            
            # 解析Markdown并创建内容
            elements = self._parse_markdown(markdown_content, styles, input_file)
            
            # 构建PDF
            if self.config.header.enabled or self.config.footer.enabled:
                doc.build(elements, 
                         onFirstPage=self._add_header_footer,
                         onLaterPages=self._add_header_footer)
            else:
                doc.build(elements)
            
            # 验证生成的文件
            result = self._validate_result(input_file, output_file)
            
            self.logger(f"转换成功: {output_file}")
            return result
            
        except Exception as e:
            error_msg = f"转换失败: {str(e)}"
            self.logger(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "input_file": input_file,
                "output_file": output_file
            }
    
    def batch_convert(self, file_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
        """
        批量转换多个Markdown文件
        
        Args:
            file_pairs: 文件对列表，每个元素为(input_file, output_file)
            
        Returns:
            批量转换结果摘要
        """
        self.logger(f"开始批量转换 {len(file_pairs)} 个文件")
        
        results = []
        success_count = 0
        
        for input_file, output_file in file_pairs:
            result = self.convert_md_to_pdf(input_file, output_file)
            results.append(result)
            
            if result.get("success", False):
                success_count += 1
        
        self.logger(f"批量转换完成: {success_count}/{len(file_pairs)} 成功")
        
        summary = {
            "total": len(file_pairs),
            "success": success_count,
            "failed": len(file_pairs) - success_count,
            "results": results
        }
        
        return summary
    
    def _get_page_size(self, page_size_name: str) -> Tuple[float, float]:
        """获取页面尺寸"""
        page_sizes = {
            "A4": A4,
            "letter": letter,
        }
        
        if page_size_name in page_sizes:
            return page_sizes[page_size_name]
        else:
            self.logger(f"警告: 未知的页面尺寸 '{page_size_name}'，使用A4")
            return A4
    
    def _parse_markdown(self, markdown_text: str, styles: Any, filename: str) -> List:
        """
        解析Markdown文本为reportlab元素
        
        Args:
            markdown_text: Markdown文本
            styles: 样式对象
            filename: 文件名（用于上下文）
            
        Returns:
            reportlab元素列表
        """
        elements = []
        lines = markdown_text.split('\n')
        
        for i, line in enumerate(lines):
            line = line.rstrip()
            
            if not line:
                # 空行
                elements.append(Spacer(1, 12))
                continue
            
            # 检查标题
            if line.startswith('# '):
                title = line[2:].strip()
                elements.append(Paragraph(title, styles.get('ChineseTitle', styles['Title'])))
                elements.append(Spacer(1, 20))
                
            elif line.startswith('## '):
                title = line[3:].strip()
                elements.append(Paragraph(title, styles.get('ChineseHeading1', styles['Heading1'])))
                
            elif line.startswith('### '):
                title = line[4:].strip()
                elements.append(Paragraph(title, styles.get('ChineseHeading2', styles['Heading2'])))
                
            elif line.startswith('#### '):
                title = line[5:].strip()
                elements.append(Paragraph(title, styles.get('ChineseHeading3', styles['Heading3'])))
                
            elif line.startswith('##### '):
                title = line[6:].strip()
                elements.append(Paragraph(title, styles.get('ChineseHeading4', styles['Heading4'])))
                
            elif line.startswith('###### '):
                title = line[7:].strip()
                elements.append(Paragraph(title, styles.get('ChineseHeading5', styles['Heading5'])))
                
            elif line.startswith('---') or line.startswith('***'):
                # 水平线
                elements.append(Spacer(1, 20))
                
            elif line.startswith('**') and line.endswith('**'):
                # 加粗文本
                bold_text = line[2:-2].strip()
                elements.append(Paragraph(bold_text, styles.get('ChineseEmphasis', styles['Normal'])))
                
            elif line.startswith('- ') or line.startswith('* '):
                # 列表项
                list_item = '• ' + line[2:].strip()
                elements.append(Paragraph(list_item, styles.get('ChineseBodyText', styles['Normal'])))
                
            elif line.startswith('1. ') or re.match(r'^\d+\. ', line):
                # 数字列表
                list_item = line
                elements.append(Paragraph(list_item, styles.get('ChineseBodyText', styles['Normal'])))
                
            elif line.startswith('> '):
                # 引用
                quote_text = line[2:].strip()
                elements.append(Paragraph(quote_text, styles.get('ChineseQuote', styles['Italic'])))
                
            else:
                # 普通段落
                elements.append(Paragraph(line, styles.get('ChineseBodyText', styles['Normal'])))
        
        return elements
    
    def _add_header_footer(self, canvas_obj: canvas.Canvas, doc: SimpleDocTemplate):
        """添加页眉页脚"""
        canvas_obj.saveState()
        
        # 页眉
        if self.config.header.enabled:
            canvas_obj.setFont('Helvetica', self.config.header.font_size)
            canvas_obj.setFillColor(getattr(colors, self.config.header.color, colors.gray))
            
            header_y = doc.height + doc.topMargin - 15
            
            # 左侧信息
            page_num = canvas_obj.getPageNumber()
            header_text = f"{self.config.header.left_text} - 第 {page_num} 页"
            canvas_obj.drawString(doc.leftMargin, header_y, header_text)
            
            # 右侧信息
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
            right_text = f"{self.config.header.right_text}: {current_date}"
            canvas_obj.drawRightString(doc.width + doc.leftMargin, header_y, right_text)
            
            # 分隔线
            if self.config.header.separator:
                canvas_obj.setStrokeColor(colors.lightgrey)
                canvas_obj.setLineWidth(0.5)
                canvas_obj.line(doc.leftMargin, header_y - 5, 
                              doc.width + doc.leftMargin, header_y - 5)
        
        # 页脚
        if self.config.footer.enabled:
            canvas_obj.setFont('Helvetica', self.config.footer.font_size)
            canvas_obj.setFillColor(getattr(colors, self.config.footer.color, colors.darkgrey))
            
            footer_text = f"{self.config.footer.text} {canvas_obj.getPageNumber()}"
            canvas_obj.drawCentredString(doc.width/2 + doc.leftMargin, 
                                       self.config.footer.margin, 
                                       footer_text)
        
        canvas_obj.restoreState()
    
    def _validate_result(self, input_file: str, output_file: str) -> Dict[str, Any]:
        """验证转换结果"""
        if not os.path.exists(output_file):
            return {
                "success": False,
                "error": "输出文件未创建",
                "input_file": input_file,
                "output_file": output_file
            }
        
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(output_file)
            page_count = len(reader.pages)
            file_size = os.path.getsize(output_file)
            
            return {
                "success": True,
                "input_file": input_file,
                "output_file": output_file,
                "pages": page_count,
                "file_size": file_size,
                "file_size_kb": file_size / 1024,
                "message": f"转换成功: {page_count}页, {file_size:,}字节"
            }
            
        except Exception as e:
            # 即使无法读取PDF，如果文件已创建也算成功
            file_size = os.path.getsize(output_file)
            return {
                "success": True,
                "input_file": input_file,
                "output_file": output_file,
                "pages": 0,
                "file_size": file_size,
                "file_size_kb": file_size / 1024,
                "message": f"文件已创建但无法验证: {str(e)[:100]}"
            }
    
    def validate_pdf(self, pdf_file: str) -> Dict[str, Any]:
        """验证PDF文件"""
        if not os.path.exists(pdf_file):
            return {
                "valid": False,
                "error": "文件不存在",
                "file": pdf_file
            }
        
        try:
            from PyPDF2 import PdfReader
            
            file_size = os.path.getsize(pdf_file)
            reader = PdfReader(pdf_file)
            page_count = len(reader.pages)
            
            # 检查第一页是否有内容
            if page_count > 0:
                first_page = reader.pages[0]
                text = first_page.extract_text()
                has_text = len(text.strip()) > 0
            else:
                has_text = False
            
            return {
                "valid": True,
                "file": pdf_file,
                "pages": page_count,
                "file_size": file_size,
                "file_size_kb": file_size / 1024,
                "has_content": has_text,
                "is_pdf": True
            }
            
        except Exception as e:
            # 检查文件头是否为PDF
            try:
                with open(pdf_file, 'rb') as f:
                    header = f.read(5)
                    is_pdf = header == b'%PDF-'
            except:
                is_pdf = False
            
            return {
                "valid": False,
                "error": str(e),
                "file": pdf_file,
                "is_pdf": is_pdf
            }


# 简单API函数
def convert_file(input_file: str, output_file: str, **kwargs) -> Dict[str, Any]:
    """快速转换单个文件"""
    generator = PDFGenerator(**kwargs)
    return generator.convert_md_to_pdf(input_file, output_file)