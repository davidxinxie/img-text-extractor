# 图片内容识别与Spotlight搜索工具

这个工具可以自动识别图片内容并将描述写入图片的metadata中，让你可以在Mac的Spotlight中按内容搜索图片。

## 功能特点

- 🤖 使用OpenAI Vision API识别图片内容
- 💾 将识别结果写入图片metadata（支持EXIF、IPTC等格式）
- 🔍 支持Mac Spotlight按内容搜索图片
- 📁 支持批量处理和递归目录扫描
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

# 仅处理当前目录，不包括子目录
./main.py ~/Pictures --no-recursive
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

## 工作原理

1. **扫描图片**: 递归扫描指定目录中的支持格式图片
2. **内容识别**: 使用OpenAI Vision API分析图片内容
3. **提取关键词**: 从描述中自动提取搜索关键词
4. **写入metadata**: 将描述和关键词写入多个metadata字段
5. **触发重新索引**: 通知Spotlight重新索引文件

## metadata字段

工具会将识别结果写入以下字段以确保Spotlight能正确索引：

- `ImageDescription` - 图片描述
- `UserComment` - 用户注释  
- `Subject` - 主题
- `Caption-Abstract` - 标题摘要
- `Keywords` - 关键词

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