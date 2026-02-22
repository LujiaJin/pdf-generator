#!/usr/bin/env python3
"""
PDF生成器命令行接口
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

from .core import PDFGenerator
from .config import PDFConfig, StyleConfig, load_config, save_config


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="专业的中文PDF文档生成工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s convert input.md output.pdf
  %(prog)s batch file_pairs.json
  %(prog)s dir ./markdown_files ./pdf_output
  %(prog)s config create my_config.json
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="子命令")
    
    # convert 命令
    convert_parser = subparsers.add_parser("convert", help="转换单个文件")
    convert_parser.add_argument("input_file", help="输入Markdown文件")
    convert_parser.add_argument("output_file", help="输出PDF文件")
    convert_parser.add_argument("--config", help="配置文件路径")
    convert_parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    # batch 命令
    batch_parser = subparsers.add_parser("batch", help="批量转换文件")
    batch_parser.add_argument("config_file", help="配置文件或文件对JSON")
    batch_parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    # dir 命令
    dir_parser = subparsers.add_parser("dir", help="转换目录中的所有文件")
    dir_parser.add_argument("input_dir", help="输入目录")
    dir_parser.add_argument("output_dir", help="输出目录")
    dir_parser.add_argument("--pattern", default="*.md", help="文件匹配模式")
    dir_parser.add_argument("--config", help="配置文件路径")
    dir_parser.add_argument("--recursive", action="store_true", help="递归处理子目录")
    dir_parser.add_argument("--debug", action="store_true", help="启用调试模式")
    
    # config 命令
    config_parser = subparsers.add_parser("config", help="配置管理")
    config_subparsers = config_parser.add_subparsers(dest="config_command", help="配置子命令")
    
    # 创建配置
    create_parser = config_subparsers.add_parser("create", help="创建默认配置")
    create_parser.add_argument("output_file", help="输出配置文件")
    
    # 验证配置
    validate_parser = config_subparsers.add_parser("validate", help="验证配置")
    validate_parser.add_argument("config_file", help="配置文件")
    
    # validate 命令
    validate_main_parser = subparsers.add_parser("validate", help="验证PDF文件")
    validate_main_parser.add_argument("pdf_file", help="PDF文件路径")
    
    # version 命令
    subparsers.add_parser("version", help="显示版本信息")
    
    # 如果没有提供命令，显示帮助
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    
    return parser.parse_args()


def convert_command(args):
    """处理convert命令"""
    print(f"转换文件: {args.input_file} -> {args.output_file}")
    
    # 加载配置
    if args.config and os.path.exists(args.config):
        config = load_config(args.config)
    else:
        config = None
    
    # 创建生成器并转换
    generator = PDFGenerator(config=config, debug=args.debug)
    
    # 检查依赖
    deps = generator.check_dependencies()
    if not deps.get("all_ok", False):
        print("错误: 缺少必要的依赖库")
        sys.exit(1)
    
    result = generator.convert_md_to_pdf(args.input_file, args.output_file)
    
    if result.get("success", False):
        print(f"✓ 转换成功: {result.get('message', '')}")
        return 0
    else:
        print(f"✗ 转换失败: {result.get('error', '未知错误')}")
        return 1


def batch_command(args):
    """处理batch命令"""
    if not os.path.exists(args.config_file):
        print(f"错误: 配置文件不存在: {args.config_file}")
        return 1
    
    try:
        with open(args.config_file, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
    except json.JSONDecodeError:
        print(f"错误: 配置文件不是有效的JSON: {args.config_file}")
        return 1
    
    # 检查配置格式
    if isinstance(config_data, dict) and "file_pairs" in config_data:
        # 完整配置格式
        file_pairs = config_data["file_pairs"]
        config = config_data.get("config")
    elif isinstance(config_data, list):
        # 简单文件对列表格式
        file_pairs = config_data
        config = None
    else:
        print("错误: 配置文件格式不正确")
        print("应为包含 'file_pairs' 的字典或文件对列表")
        return 1
    
    print(f"批量转换 {len(file_pairs)} 个文件...")
    
    # 创建生成器
    generator = PDFGenerator(config=config, debug=args.debug)
    
    # 检查依赖
    deps = generator.check_dependencies()
    if not deps.get("all_ok", False):
        print("错误: 缺少必要的依赖库")
        return 1
    
    # 执行批量转换
    results = generator.batch_convert(file_pairs)
    
    # 显示结果
    print(f"\n批量转换完成:")
    print(f"  总计: {results['total']}")
    print(f"  成功: {results['success']}")
    print(f"  失败: {results['failed']}")
    
    # 显示失败详情
    if results['failed'] > 0:
        print("\n失败的文件:")
        for result in results['results']:
            if not result.get("success", False):
                print(f"  - {result.get('input_file', '未知')}: {result.get('error', '未知错误')}")
    
    return 1 if results['failed'] > 0 else 0


def dir_command(args):
    """处理dir命令"""
    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    
    if not input_dir.exists():
        print(f"错误: 输入目录不存在: {input_dir}")
        return 1
    
    # 创建输出目录
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 查找文件
    if args.recursive:
        md_files = list(input_dir.rglob(args.pattern))
    else:
        md_files = list(input_dir.glob(args.pattern))
    
    if not md_files:
        print(f"在 {input_dir} 中未找到匹配 {args.pattern} 的文件")
        return 0
    
    print(f"在 {input_dir} 中找到 {len(md_files)} 个文件")
    
    # 准备文件对
    file_pairs = []
    for md_file in md_files:
        # 保持相对目录结构
        if args.recursive:
            rel_path = md_file.relative_to(input_dir)
        else:
            rel_path = Path(md_file.name)
        
        # 修改扩展名为.pdf
        pdf_file = output_dir / rel_path.with_suffix('.pdf')
        
        # 确保输出目录存在
        pdf_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_pairs.append((str(md_file), str(pdf_file)))
    
    # 加载配置
    if args.config and os.path.exists(args.config):
        config = load_config(args.config)
    else:
        config = None
    
    # 创建生成器
    generator = PDFGenerator(config=config, debug=args.debug)
    
    # 检查依赖
    deps = generator.check_dependencies()
    if not deps.get("all_ok", False):
        print("错误: 缺少必要的依赖库")
        return 1
    
    # 执行批量转换
    results = generator.batch_convert(file_pairs)
    
    # 显示结果
    print(f"\n目录转换完成:")
    print(f"  总计: {results['total']}")
    print(f"  成功: {results['success']}")
    print(f"  失败: {results['failed']}")
    
    return 1 if results['failed'] > 0 else 0


def config_command(args):
    """处理config命令"""
    if args.config_command == "create":
        # 创建默认配置
        config = PDFConfig()
        save_config(config, args.output_file)
        print(f"默认配置已保存到: {args.output_file}")
        return 0
        
    elif args.config_command == "validate":
        # 验证配置
        if not os.path.exists(args.config_file):
            print(f"错误: 配置文件不存在: {args.config_file}")
            return 1
        
        try:
            config = load_config(args.config_file)
            print(f"✓ 配置文件有效: {args.config_file}")
            print(f"  页面尺寸: {config.page_size}")
            print(f"  上边距: {config.margins.top}")
            print(f"  页眉启用: {config.header.enabled}")
            return 0
        except Exception as e:
            print(f"✗ 配置文件无效: {e}")
            return 1
    
    return 0


def validate_command(args):
    """处理validate命令"""
    if not os.path.exists(args.pdf_file):
        print(f"错误: 文件不存在: {args.pdf_file}")
        return 1
    
    generator = PDFGenerator()
    result = generator.validate_pdf(args.pdf_file)
    
    if result.get("valid", False):
        print(f"✓ PDF文件有效: {args.pdf_file}")
        print(f"  页数: {result['pages']}")
        print(f"  大小: {result['file_size_kb']:.1f} KB")
        print(f"  有内容: {result['has_content']}")
        return 0
    else:
        print(f"✗ PDF文件无效: {args.pdf_file}")
        print(f"  错误: {result.get('error', '未知错误')}")
        print(f"  是PDF格式: {result.get('is_pdf', '未知')}")
        return 1


def version_command():
    """显示版本信息"""
    try:
        from . import __version__
        version = __version__
    except:
        version = "未知"
    
    print(f"PDF生成器版本: {version}")
    print("基于优化的reportlab实现，支持中文和专业格式")
    return 0


def main():
    """主函数"""
    args = parse_args()
    
    try:
        if args.command == "convert":
            return convert_command(args)
        elif args.command == "batch":
            return batch_command(args)
        elif args.command == "dir":
            return dir_command(args)
        elif args.command == "config":
            return config_command(args)
        elif args.command == "validate":
            return validate_command(args)
        elif args.command == "version":
            return version_command()
        else:
            print(f"未知命令: {args.command}")
            return 1
    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 130
    except Exception as e:
        print(f"错误: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())