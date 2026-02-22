# PDF Generator - 专业中文PDF文档生成工具

一个高性能、支持中文的Markdown转PDF文档生成器，专为解决中文PDF生成中的字体、编码和格式化问题而设计。

## 特性

- ✅ **完美中文支持**: 自动检测系统中文字体，支持TrueType字体嵌入
- ✅ **专业版式**: 包含页眉、页脚、目录、页码等专业元素
- ✅ **Markdown兼容**: 完整支持Markdown语法（标题、列表、代码块、表格等）
- ✅ **批量处理**: 支持批量转换和递归目录处理
- ✅ **高度可配置**: 灵活的样式和布局配置
- ✅ **命令行接口**: 易于集成的CLI工具
- ✅ **Python API**: 简洁的编程接口

## 安装

```bash
# 从源代码安装
cd skills/pdf-generation
pip install -e .

# 或安装依赖
pip install -r requirements.txt
```

## 快速开始

### 命令行使用

```bash
# 单个文件转换
pdf-generator convert input.md output.pdf

# 批量转换目录
pdf-generator batch input_directory output_directory

# 递归处理子目录
pdf-generator batch --recursive input_directory output_directory

# 使用自定义配置
pdf-generator convert --config my_config.json input.md output.pdf
```

### Python API使用

```python
from pdf_generator import PDFGenerator, PDFConfig

# 基本使用
config = PDFConfig()
generator = PDFGenerator(config)

# 转换单个文件
result = generator.convert_md_to_pdf("input.md", "output.pdf")
print(f"转换结果: {result}")

# 批量转换
file_pairs = [("file1.md", "file1.pdf"), ("file2.md", "file2.pdf")]
summary = generator.batch_convert(file_pairs)
print(f"批量转换完成: {summary['success']}/{summary['total']} 成功")
```

## 配置

### 配置文件示例

```json
{
  "page_size": "A4",
  "margins": {
    "top": 90,
    "bottom": 72,
    "left": 72,
    "right": 72
  },
  "header": {
    "enabled": true,
    "separator": true,
    "left_text": "文档",
    "right_text": "生成时间"
  },
  "footer": {
    "enabled": true,
    "page_number": true
  },
  "styles": {
    "heading1": {
      "font_size": 24,
      "font_name": "SimHei",
      "space_before": 24,
      "space_after": 12
    },
    "body": {
      "font_size": 12,
      "font_name": "Microsoft YaHei",
      "leading": 16
    }
  }
}
```

## 解决的核心问题

1. **中文乱码问题**: 自动检测并嵌入中文字体，避免PDF显示乱码
2. **字体缺失问题**: 支持Windows/Mac/Linux系统字体自动检测
3. **内容丢失问题**: 完整保留Markdown格式转换，无内容损失
4. **页眉重叠问题**: 智能调整页边距，避免内容重叠
5. **专业排版**: 提供符合印刷标准的文档排版

## 文档结构

```
pdf_generator/
├── core.py              # 核心生成逻辑
├── config.py           # 配置管理
├── fonts.py            # 字体管理
├── styles.py           # 样式管理
├── cli.py              # 命令行接口
└── __init__.py         # 模块导出
```

## 授权

MIT License