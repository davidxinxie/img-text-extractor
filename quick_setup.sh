#!/bin/bash
# GitHub Token 快速设置脚本

echo "🔑 GitHub Token 快速设置"
echo "=========================="
echo ""
echo "请按照以下步骤操作："
echo ""
echo "1. 在浏览器中完成密码验证"
echo "2. 在Token创建页面："
echo "   - Note: img-text-tool-automation"
echo "   - 选择权限: ✅ repo"
echo "   - 点击 Generate token"
echo "3. 复制生成的token"
echo ""

# 提示用户输入token
read -s -p "请粘贴你的GitHub token: " TOKEN
echo ""

if [ -z "$TOKEN" ]; then
    echo "❌ Token不能为空"
    exit 1
fi

# 检查.env文件是否存在
if [ -f ".env" ]; then
    # 检查是否已有GITHUB_TOKEN
    if grep -q "GITHUB_TOKEN=" .env; then
        # 更新现有的token
        sed -i.bak "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$TOKEN/" .env
        echo "✅ 已更新.env文件中的GITHUB_TOKEN"
    else
        # 添加新的token
        echo "GITHUB_TOKEN=$TOKEN" >> .env
        echo "✅ 已添加GITHUB_TOKEN到.env文件"
    fi
else
    # 创建新的.env文件
    echo "GITHUB_TOKEN=$TOKEN" > .env
    echo "✅ 已创建.env文件并添加GITHUB_TOKEN"
fi

echo ""
echo "🧪 测试连接..."
if python github_sync.py test; then
    echo ""
    echo "🎉 设置成功！现在你可以使用自动化命令："
    echo "   ./github_sync.py upload --file README.md --github-path README.md --message \"Update\""
    echo "   ./github_sync.py sync --message \"Auto sync\""
else
    echo ""
    echo "❌ 测试失败，请检查token是否正确"
fi