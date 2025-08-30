#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
from tqdm import tqdm

from vision import ImageAnalyzer
from metadata import MetadataWriter
from config import SUPPORTED_IMAGE_FORMATS


def find_images(directory: str, recursive: bool = True) -> list:
    """查找目录中的图片文件"""
    image_files = []
    path = Path(directory)
    
    if not path.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")
    
    if not path.is_dir():
        raise ValueError(f"路径不是目录: {directory}")
    
    # 根据是否递归选择搜索方式
    if recursive:
        pattern = "**/*"
        files = path.rglob(pattern)
    else:
        files = path.iterdir()
    
    for file in files:
        if file.is_file() and file.suffix.lower() in SUPPORTED_IMAGE_FORMATS:
            image_files.append(str(file))
    
    return sorted(image_files)


def main():
    parser = argparse.ArgumentParser(
        description="图片内容识别工具 - 将图片内容写入metadata以支持Spotlight搜索",
        epilog="""
使用示例:
  python main.py ~/Pictures                           # 处理Pictures目录
  python main.py ~/Pictures ~/Documents/Images        # 处理多个目录
  python main.py ~/Pictures --no-recursive            # 仅处理当前目录，不包括子目录
  python main.py ~/Pictures --dry-run                 # 预览模式，不实际写入
  python main.py ~/Pictures --verify                  # 验证已写入的metadata

注意: 首次使用前请先创建 .env 文件并设置 OPENAI_API_KEY
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'directories',
        nargs='+',
        help='要处理的图片目录路径（可以指定多个目录）'
    )
    
    parser.add_argument(
        '--no-recursive',
        action='store_true',
        help='不递归处理子目录'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='预览模式：只识别图片内容，不写入metadata'
    )
    
    parser.add_argument(
        '--verify',
        action='store_true',
        help='验证已存在的metadata（不重新识别）'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新处理已有metadata的图片'
    )
    
    parser.add_argument(
        '--safe-mode',
        action='store_true',
        help='安全模式：创建额外备份，更严格的文件检查'
    )
    
    args = parser.parse_args()
    
    try:
        # 查找图片文件
        print("🔍 正在扫描图片文件...")
        all_image_files = []
        for directory in args.directories:
            print(f"  📂 扫描目录: {directory}")
            dir_images = find_images(directory, not args.no_recursive)
            all_image_files.extend(dir_images)
            print(f"     找到 {len(dir_images)} 张图片")
        
        if not all_image_files:
            print("❌ 未找到支持的图片文件")
            print(f"支持的格式: {', '.join(SUPPORTED_IMAGE_FORMATS)}")
            return 1
        
        print(f"✅ 总共找到 {len(all_image_files)} 张图片")
        image_files = all_image_files
        
        # 初始化工具
        metadata_writer = MetadataWriter()
        
        if args.verify:
            # 验证模式
            print("\n🔍 正在验证metadata...")
            for image_file in tqdm(image_files, desc="验证进度"):
                metadata = metadata_writer.verify_metadata(image_file)
                # 找到图片文件属于哪个目录，用于计算相对路径
                relative_path = image_file
                for directory in args.directories:
                    if image_file.startswith(os.path.abspath(directory)):
                        relative_path = os.path.relpath(image_file, directory)
                        break
                
                if metadata:
                    print(f"✅ {relative_path}: 已有metadata")
                    for key, value in metadata.items():
                        if len(value) > 50:
                            value = value[:50] + "..."
                        print(f"    {key}: {value}")
                else:
                    print(f"❌ {relative_path}: 无metadata")
            return 0
        
        # 分析并写入图片内容
        print("\n🤖 正在逐张检查并处理图片...")
        success_count = 0
        analyzed_count = 0
        skipped_count = 0
        all_keywords = set()  # 收集所有提取的关键词
        analyzer = None  # 延迟初始化
        
        with tqdm(total=len(image_files), desc="处理进度", unit="张") as pbar:
            for i, image_file in enumerate(image_files, 1):
                # 显示相对路径，更清晰显示目录结构
                # 找到图片文件属于哪个目录，用于计算相对路径
                relative_path = image_file
                for directory in args.directories:
                    if image_file.startswith(os.path.abspath(directory)):
                        relative_path = os.path.relpath(image_file, directory)
                        break
                
                # 检查是否已有metadata（除非强制模式）
                # 在dry-run模式下也跳过检查，让用户预览所有图片的分析结果
                if not args.force and not args.dry_run:
                    existing_metadata = metadata_writer.verify_metadata(image_file)
                    if existing_metadata:
                        print(f"\n[{i}/{len(image_files)}] ⏭️  跳过（已有metadata）: {relative_path}")
                        skipped_count += 1
                        pbar.update(1)
                        continue
                
                # 延迟初始化图片分析器（只在需要分析时初始化）
                if analyzer is None:
                    try:
                        analyzer = ImageAnalyzer()
                    except ValueError as e:
                        print(f"❌ {e}")
                        print("请创建 .env 文件并设置你的 OPENAI_API_KEY")
                        return 1
                
                print(f"\n[{i}/{len(image_files)}] 正在分析: {relative_path}")
                description = analyzer.analyze_image(image_file)
                
                if description:
                    analyzed_count += 1
                    
                    # 解析结构化描述并显示要写入的metadata信息
                    parsed = metadata_writer.parse_description(description)
                    keywords = metadata_writer.extract_keywords(description)
                    keywords_str = ', '.join(keywords) if keywords else ''
                    
                    # 收集关键词用于最终示例
                    if keywords:
                        all_keywords.update(keywords[:5])  # 每张图片取前5个关键词
                    
                    # 构建搜索优化的短描述
                    search_description_parts = []
                    if 'summary' in parsed:
                        search_description_parts.append(parsed['summary'])
                    if 'objects' in parsed:
                        search_description_parts.append(parsed['objects'])
                    if 'scene' in parsed:
                        search_description_parts.append(parsed['scene'])
                    search_description = ' '.join(search_description_parts)
                    
                    print(f"  📝 将要写入的metadata字段:")
                    
                    # 显示实际的metadata字段和值（处理换行，保持缩进对齐）
                    def format_multiline_field(field_name, content, max_length=100):
                        """格式化多行字段，保持缩进对齐"""
                        if not content:
                            return
                        
                        lines = content.strip().split('\n')
                        if len(lines) == 1:
                            # 单行内容，检查长度
                            if len(content) > max_length:
                                content = content[:max_length-3] + "..."
                            print(f"    {field_name}: {content}")
                        else:
                            # 多行内容，保持缩进
                            print(f"    {field_name}: {lines[0]}")
                            indent = " " * (len(field_name) + 6)  # 对齐到冒号后面
                            for line in lines[1:]:
                                if line.strip():
                                    print(f"{indent}{line.strip()}")
                    
                    if search_description:
                        search_display = search_description.replace('\n', ' ').strip()
                        if len(search_display) > 80:
                            search_display = search_display[:77] + "..."
                        print(f"    Subject: {search_display}")
                        print(f"    Caption-Abstract: {search_display}")
                    
                    if description:
                        format_multiline_field("ImageDescription", description, 120)
                        format_multiline_field("UserComment", description, 120)
                    
                    if keywords_str:
                        # 限制关键词显示长度
                        if len(keywords_str) > 80:
                            keywords_display = keywords_str[:77] + "..."
                        else:
                            keywords_display = keywords_str
                        print(f"    XMP:Description: {keywords_display}")
                        print(f"    Keywords: {keywords_display}")
                        print(f"    XMP:Subject: {keywords_display}")
                    
                    if 'text' in parsed and parsed['text'] and parsed['text'] != '无':
                        format_multiline_field("XMP:Title", parsed['text'], 80)
                    
                    print(f"  ✅ 分析完成 (共{len(keywords)}个关键词)")
                    
                    # 预览模式：只显示，不写入
                    if args.dry_run:
                        print(f"  📋 预览模式：跳过metadata写入")
                        pbar.update(1)
                        continue
                    
                    # 立即写入metadata
                    print(f"  💾 正在写入metadata...")
                    # 临时设置当前处理目录，用于显示相对路径
                    current_base_dir = None
                    for directory in args.directories:
                        if image_file.startswith(os.path.abspath(directory)):
                            current_base_dir = directory
                            break
                    metadata_writer._current_base_dir = current_base_dir
                    if metadata_writer.write_metadata(image_file, description):
                        success_count += 1
                else:
                    print(f"  ❌ 分析失败")
                
                pbar.update(1)
        
        if analyzed_count == 0 and skipped_count == 0:
            print("❌ 没有成功处理的图片")
            return 1
        elif analyzed_count == 0 and skipped_count > 0:
            print(f"\n✅ 所有 {skipped_count} 张图片都已有metadata，无需重新处理")
            print("使用 --force 参数可强制重新处理")
            return 0
        
        print(f"\n✅ 成功识别 {analyzed_count} 张图片")
        
        # 预览模式总结
        if args.dry_run:
            print(f"✅ 预览完成。使用不带 --dry-run 参数的命令来实际写入metadata")
            return 0
        
        # 触发Spotlight重新索引
        print("\n🔄 触发Spotlight重新索引...")
        for directory in args.directories:
            metadata_writer.trigger_spotlight_reindex(directory)
        
        # 总结
        print(f"\n📊 处理完成!")
        print(f"   总计: {len(image_files)} 张图片")
        if skipped_count > 0:
            print(f"   跳过（已有metadata）: {skipped_count} 张")
        print(f"   识别成功: {analyzed_count} 张")
        print(f"   写入成功: {success_count} 张")
        
        if success_count > 0:
            print(f"\n✅ 现在可以在Mac的Spotlight中按内容搜索这些图片了!")
            if all_keywords:
                # 选择一些代表性的关键词作为示例
                example_keywords = list(all_keywords)[:6]  # 最多显示6个
                example_str = '\"、\"'.join(example_keywords)
                print(f"   比如搜索: \"{example_str}\" 等关键词")
            else:
                print(f"   比如搜索: \"人物\"、\"风景\"、\"建筑\" 等关键词")
        
        return 0 if success_count > 0 else 1
        
    except KeyboardInterrupt:
        print("\n\n⏹️  用户中断操作")
        return 130
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())