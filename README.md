# pdf-generator

<sub>💡 **Tip**: If you find this repository's structure or content difficult to understand, visit [deepwiki](https://deepwiki.com/LujiaJin/pdf-generator) for a comprehensive detailed explanation.</sub>

[![Build Status](https://img.shields.io/github/actions/workflow/status/LujiaJin/pdf-generator/test.yml?branch=main&logo=github)](https://github.com/LujiaJin/pdf-generator/actions/workflows/test.yml)
[![PyPI Version](https://img.shields.io/pypi/v/pdf-generator?logo=pypi)](https://pypi.org/project/pdf-generator/)
[![Python Version](https://img.shields.io/pypi/pyversions/pdf-generator?logo=python)](https://pypi.org/project/pdf-generator/)
[![License](https://img.shields.io/github/license/LujiaJin/pdf-generator?color=blue)](LICENSE)

> 🌟 **专业级中文 Markdown → PDF 生成器** — 基于 `reportlab`，完美支持微软雅黑、黑体等中文字体，解决乱码、重叠、失真等所有常见问题。

---

## ✨ 特性亮点

| 功能 | 说明 |
|------|------|
| ✅ 中文无忧 | 自动检测 Windows/macOS/Linux 系统中文字体（微软雅黑 / SimHei / Noto Sans CJK） |
| ✅ 专业排版 | 页眉/页脚/页码/目录/自定义边距（已修复 `topMargin=90` 避免重叠） |
| ✅ 完整兼容 | 标题、列表、表格、代码块、引用、加粗、斜体、链接全部保留 |
| ✅ 双接口 | CLI 命令行 + Python API，开箱即用 |
| ✅ 模块化 | `src/` 分层清晰，便于二次开发与定制 |

---

## 🚀 快速开始

### 安装

```bash
pip install git+https://github.com/LujiaJin/pdf-generator
# 或本地开发安装
pip install -e .
```

### CLI 使用（推荐）

```bash
# 转换单个文件
pdf-generator convert report.md report.pdf

# 批量转换整个目录
pdf-generator batch ./docs ./output

# 递归处理子目录（保留层级）
pdf-generator batch --recursive ./src ./dist
```

### Python API 使用

```python
from pdf_generator import PDFGenerator, PDFConfig

generator = PDFGenerator(PDFConfig(
    margins={"top": 90, "bottom": 72, "left": 72, "right": 72},
))

result = generator.convert_md_to_pdf("input.md", "output.pdf")
print(f"✅ 生成成功！{result['page_count']} 页，{result['file_size']} 字节")
```

---

## ️ 开发与贡献

```bash
# 克隆仓库
git clone https://github.com/LujiaJin/pdf-generator
cd pdf-generator

# 安装开发依赖
pip install -e ".[test]"

# 运行测试
pytest tests/

# 类型检查
mypy src/
```

欢迎提交 Issue 或 Pull Request！

---

## 📜 许可证

MIT License — 详见 [LICENSE](LICENSE)