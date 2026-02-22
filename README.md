# pdf-generator

Professional Chinese Markdown-to-PDF generator using reportlab.

## Features

- ✅ Perfect Chinese support with automatic font detection (Microsoft YaHei, SimHei, etc.)
- ✅ Professional layout with headers, footers, page numbers, and proper margins
- ✅ Complete Markdown compatibility (headings, lists, tables, code blocks, quotes)
- ✅ Command-line interface for easy batch processing
- ✅ Python API for programmatic use
- ✅ Modular architecture for easy maintenance and extension

## Installation

```bash
pip install -e .
```

## Usage

### Command Line

```bash
# Convert single file
pdf-generator convert input.md output.pdf

# Batch convert directory
pdf-generator batch input_dir output_dir

# Recursive conversion
pdf-generator batch --recursive input_dir output_dir
```

### Python API

```python
from pdf_generator import PDFGenerator, PDFConfig

generator = PDFGenerator(PDFConfig())
result = generator.convert_md_to_pdf("input.md", "output.pdf")
```

## License

MIT