#!/bin/bash

# 测试脚本 - 确保每次修改后功能正常

echo "🧪 开始运行测试..."
echo "======================================="

# 运行单元测试
echo "📋 运行单元测试..."
python test_main.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有测试通过！"
    echo ""
    echo "🔍 测试覆盖的功能："
    echo "  - 图片文件查找（递归/非递归）"
    echo "  - 逐张处理逻辑"
    echo "  - metadata 检查和跳过逻辑"
    echo "  - 各种命令行参数（--dry-run, --force, --verify）"
    echo "  - 错误处理和边界情况"
    echo "  - 延迟初始化 ImageAnalyzer"
    echo ""
    echo "📝 主要改进："
    echo "  ✓ 从批量预检查改为逐张处理"
    echo "  ✓ 只在需要时才初始化 ImageAnalyzer"
    echo "  ✓ 更好的进度反馈和统计信息"
    echo "  ✓ 适合处理大目录的优化流程"
else
    echo ""
    echo "❌ 测试失败！请检查代码。"
    exit 1
fi

echo ""
echo "🎉 测试完成！代码可以安全使用。"