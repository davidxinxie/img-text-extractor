# Image Text Extraction with Spotlight Search

This tool automatically analyzes image content using OpenAI Vision API and writes descriptions to image metadata, enabling content-based search in macOS Spotlight.

## Features

- 🤖 Analyze image content using OpenAI Vision API
- 💾 Write results to image metadata (EXIF, IPTC, XMP formats)
- 🔍 Enable content-based search in macOS Spotlight
- 📁 Support batch processing and recursive directory scanning
- 📄 Process individual image files directly
- 📸 Professional screenshot mode with optimized text extraction
- 📊 Real-time progress display
- ✅ Intelligently skip already processed images
- 🔍 Preview and verification modes

## System Requirements

- macOS system
- Python 3.8+
- OpenAI API Key
- Homebrew (for installing exiftool)

## Installation

1. **Install dependencies**
   ```bash
   brew install exiftool
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure API Key**
   ```bash
   cp .env.example .env
   # Edit .env file and add your OpenAI API Key
   ```

## Usage

### Basic Usage
```bash
# Process all images in a directory
./main.py ~/Pictures

# Process a single image file
./main.py ~/Pictures/image.jpg

# Process mixed directories and files
./main.py ~/Pictures ~/Screenshots/screen.png

# Process current directory only (non-recursive)
./main.py ~/Pictures --no-recursive
```

### Screenshot Mode
```bash
# Screenshot mode - optimized for text and software recognition
./main.py ~/Screenshots --screenshot-mode

# Preview screenshot analysis
./main.py ~/Screenshots --screenshot-mode --dry-run

# Process single screenshot file
./main.py ~/Screenshots/screen.png --screenshot-mode
```

### Preview Mode
```bash
# Preview analysis results without writing metadata
./main.py ~/Pictures --dry-run
```

### Verification Mode
```bash
# Check which images already have metadata
./main.py ~/Pictures --verify
```

### Force Reprocessing
```bash
# Reprocess all images (including those with existing metadata)
./main.py ~/Pictures --force
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png) 
- WebP (.webp)
- GIF (.gif)
- HEIC/HEIF (.heic, .heif) - Apple formats

## How It Works

1. **Scan Images**: Recursively scan supported image formats in specified directories
2. **Content Analysis**: Analyze image content using OpenAI Vision API
3. **Keyword Extraction**: Automatically extract search keywords from descriptions
4. **Write Metadata**: Write descriptions and keywords to multiple metadata fields
5. **Trigger Reindexing**: Notify Spotlight to reindex files

## Metadata Fields

The tool writes recognition results to the following fields to ensure proper Spotlight indexing:

### Normal Mode
- `ImageDescription` - Image description
- `UserComment` - User comments  
- `Subject` - Subject
- `Caption-Abstract` - Caption abstract
- `Keywords` - Keywords
- `XMP:Title` - Text content (if any)

### Screenshot Mode (Additional Fields)
- `XMP:Title` - Extracted text content
- `Creator` - Text content (for search)
- `Software` - Identified application name

## Spotlight Search

After processing, you can search in Spotlight for:

- **Scene descriptions**: "beach", "forest", "city"
- **People**: "person", "child", "woman"  
- **Objects**: "car", "building", "food"
- **Emotions**: "happy", "peaceful", "lively"

## Important Notes

- ⚠️ Using OpenAI API incurs costs, recommend using --dry-run for preview
- 🔄 Processing large numbers of images may take considerable time
- 💾 Tool automatically skips already processed images
- 🔍 Spotlight index updates may take a few minutes

## Troubleshooting

### API Key Error
```
❌ Please set OPENAI_API_KEY in .env file
```
**Solution**: Check that .env file exists and contains a valid API Key

### exiftool Not Installed
```
❌ exiftool not installed. Please run: brew install exiftool
```
**Solution**: Run `brew install exiftool` to install the tool

### No Image Permissions
Ensure you have read/write permissions for the target directory

## License

MIT License

---

# 图片内容识别与Spotlight搜索工具

这个工具可以自动识别图片内容并将描述写入图片的metadata中，让你可以在Mac的Spotlight中按内容搜索图片。

## 功能特点

- 🤖 使用OpenAI Vision API识别图片内容
- 💾 将识别结果写入图片metadata（支持EXIF、IPTC等格式）
- 🔍 支持Mac Spotlight按内容搜索图片
- 📁 支持批量处理和递归目录扫描
- 📄 支持单个图片文件直接处理
- 📸 专业截图模式，优化文字内容识别
- 📊 实时进度显示
- ✅ 智能跳过已处理的图片
- 🔍 预览和验证模式

## 系统要求

- macOS系统
- Python 3.8+
- OpenAI API Key
- Homebrew (用于安装exiftool)

## 安装步骤

1. **安装依赖工具**
   ```bash
   brew install exiftool
   ```

2. **安装Python依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置API Key**
   ```bash
   cp .env.example .env
   # 编辑.env文件，填入你的OpenAI API Key
   ```

## 使用方法

### 基本用法
```bash
# 处理指定目录下的所有图片
./main.py ~/Pictures

# 处理单个图片文件
./main.py ~/Pictures/image.jpg

# 混合处理目录和文件
./main.py ~/Pictures ~/Screenshots/screen.png

# 仅处理当前目录，不包括子目录
./main.py ~/Pictures --no-recursive
```

### 截图模式
```bash
# 截图模式 - 专门识别文字内容和软件名称
./main.py ~/Screenshots --screenshot-mode

# 预览截图识别效果
./main.py ~/Screenshots --screenshot-mode --dry-run

# 处理单个截图文件
./main.py ~/Screenshots/screen.png --screenshot-mode
```

### 预览模式
```bash
# 预览识别结果，不实际写入metadata
./main.py ~/Pictures --dry-run
```

### 验证模式
```bash
# 检查哪些图片已有metadata
./main.py ~/Pictures --verify
```

### 强制重新处理
```bash
# 重新处理所有图片（包括已有metadata的）
./main.py ~/Pictures --force
```

## 支持的图片格式

- JPEG (.jpg, .jpeg)
- PNG (.png) 
- WebP (.webp)
- GIF (.gif)
- HEIC/HEIF (.heic, .heif) - Apple格式

## 工作原理

1. **扫描图片**: 递归扫描指定目录中的支持格式图片
2. **内容识别**: 使用OpenAI Vision API分析图片内容
3. **提取关键词**: 从描述中自动提取搜索关键词
4. **写入metadata**: 将描述和关键词写入多个metadata字段
5. **触发重新索引**: 通知Spotlight重新索引文件

## metadata字段

工具会将识别结果写入以下字段以确保Spotlight能正确索引：

### 普通模式
- `ImageDescription` - 图片描述
- `UserComment` - 用户注释  
- `Subject` - 主题
- `Caption-Abstract` - 标题摘要
- `Keywords` - 关键词
- `XMP:Title` - 文字内容（如有）

### 截图模式（额外字段）
- `XMP:Title` - 提取的文字内容
- `Creator` - 文字内容（用于搜索）
- `Software` - 识别的应用程序名称

## Spotlight搜索

处理完成后，你可以在Spotlight中搜索：

- **场景描述**: "海滩"、"森林"、"城市"
- **人物**: "人物"、"儿童"、"女性"  
- **物体**: "汽车"、"建筑"、"食物"
- **情感**: "快乐"、"宁静"、"热闹"

## 注意事项

- ⚠️ 使用OpenAI API会产生费用，建议先用--dry-run预览
- 🔄 处理大量图片可能需要较长时间
- 💾 工具会自动跳过已处理的图片
- 🔍 Spotlight索引更新可能需要几分钟时间

## 故障排除

### API Key错误
```
❌ 请在 .env 文件中设置 OPENAI_API_KEY
```
解决: 检查.env文件是否存在且包含有效的API Key

### exiftool未安装
```
❌ exiftool 未安装。请运行: brew install exiftool  
```
解决: 运行 `brew install exiftool` 安装工具

### 无图片权限
确保对目标目录有读写权限

## 许可证

MIT License
