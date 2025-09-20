# GitHub Token 设置指南

## 当前状态
你现在在GitHub的身份验证页面，需要输入密码确认身份。

## 🔐 第1步：完成身份验证
1. 在浏览器中输入你的GitHub密码
2. 点击"Confirm"按钮

## 📝 第2步：创建Token（验证后自动跳转）
验证完成后，你会看到"New personal access token"页面，请按照以下设置：

### Token信息填写：
- **Note (描述)**: `img-text-tool-automation`
- **Expiration (过期时间)**: `No expiration` (或选择你需要的时长)

### 权限选择（重要）：
✅ **repo** - Full control of private repositories
   - 这是我们需要的唯一权限，用于上传和更新仓库文件

### 不需要选择的权限：
❌ 其他所有权限都不需要勾选

## 🎯 第3步：生成并复制Token
1. 滚动到页面底部
2. 点击绿色的"Generate token"按钮  
3. **重要**: 立即复制生成的token（只显示一次！）

## 💾 第4步：保存Token到项目
复制token后，在终端运行：
```bash
cd "/Users/xiexin/Library/Mobile Documents/com~apple~CloudDocs/Pictures/img-text"

# 方法1：使用我们的自动化工具
./github_sync.py setup
# 然后粘贴token

# 方法2：手动添加到.env文件
echo "GITHUB_TOKEN=你的token" >> .env
```

## ✅ 第5步：测试连接
```bash
./github_sync.py test
```
应该看到：`✅ Connected to GitHub as: davidxinxie`

## 🚀 完成！现在你可以使用自动化命令：
```bash
# 上传单个文件
./github_sync.py upload --file README.md --github-path README.md --message "Update docs"

# 同步整个项目  
./github_sync.py sync --message "Add automation tools"
```

---
## 🆘 如果遇到问题：
1. **Token权限错误**: 确保选择了`repo`权限
2. **Token过期**: 重新生成一个新的token
3. **验证失败**: 检查密码是否正确

**提示**: Token就像密码一样重要，请妥善保管！