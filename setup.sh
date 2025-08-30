#!/bin/bash

echo "🚀 图片内容识别工具 - 安装脚本"
echo "=================================="

# 检查是否为macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此工具仅支持macOS系统"
    exit 1
fi

# 检查Homebrew
if ! command -v brew &> /dev/null; then
    echo "❌ 未检测到Homebrew，请先安装Homebrew:"
    echo "   /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
    exit 1
fi

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未检测到Python3，请先安装Python"
    exit 1
fi

# 安装exiftool
echo "📦 安装exiftool..."
if ! command -v exiftool &> /dev/null; then
    brew install exiftool
    if [ $? -eq 0 ]; then
        echo "✅ exiftool安装成功"
    else
        echo "❌ exiftool安装失败"
        exit 1
    fi
else
    echo "✅ exiftool已安装"
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Python依赖安装成功"
else
    echo "❌ Python依赖安装失败"
    exit 1
fi

# 创建.env文件
if [ ! -f ".env" ]; then
    echo "📝 创建配置文件..."
    cp .env.example .env
    echo "✅ 已创建.env文件"
    echo ""
    echo "⚠️  重要: 请编辑.env文件并设置你的OpenAI API Key:"
    echo "   OPENAI_API_KEY=your_api_key_here"
    echo ""
    echo "🔗 获取API Key: https://platform.openai.com/api-keys"
else
    echo "✅ .env文件已存在"
fi

# 使main.py可执行
chmod +x main.py

echo ""
echo "🎉 安装完成!"
echo ""
echo "📸 支持的图片格式:"
echo "   • 常规格式: JPG, JPEG, PNG, WebP, GIF"
echo "   • Apple格式: HEIC, HEIF (已自动安装pillow-heif支持)"
echo ""
echo "📖 使用方法:"
echo "   ./main.py ~/Pictures              # 处理图片目录"
echo "   ./main.py ~/Pictures --dry-run    # 预览模式"
echo "   ./main.py ~/Pictures --safe-mode  # 安全模式"
echo "   ./main.py --help                  # 查看所有选项"
echo ""
echo "💡 提示: 记得先在.env文件中设置OpenAI API Key!"