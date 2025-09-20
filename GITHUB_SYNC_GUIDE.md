# GitHub同步工具使用指南

这个工具可以让你通过命令行自动化更新GitHub仓库，替代手工网页操作，大大提高效率。

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置GitHub Token
```bash
./github_sync.py setup
```
这会引导你：
1. 访问 GitHub Settings -> Developer settings -> Personal access tokens
2. 创建新的token，选择 `repo` 权限
3. 将token保存到项目的 `.env` 文件中

### 3. 测试连接
```bash
./github_sync.py test
```

## 📖 使用方法

### 上传单个文件
```bash
# 上传本地文件到GitHub指定路径
./github_sync.py upload --file README.md --github-path README.md --message "Update README"

# 强制更新已存在的文件
./github_sync.py upload --file config.py --github-path config.py --message "Fix config" --force
```

### 批量同步整个项目
```bash
# 同步当前目录的所有文件到GitHub
./github_sync.py sync

# 自定义提交信息
./github_sync.py sync --message "Major update: add new features"
```

### 指定其他仓库
```bash
# 如果你有多个仓库
./github_sync.py upload --repo username/another-repo --file test.py --github-path test.py --message "Add test"
```

## 🔧 高级功能

### 环境变量配置
在 `.env` 文件中设置：
```bash
GITHUB_TOKEN=your_personal_access_token_here
```

### 批量操作示例
```python
# Python脚本中使用
from github_sync import GitHubSyncTool

github = GitHubSyncTool()

# 批量上传多个文件
file_mappings = [
    ('local_file1.py', 'src/file1.py'),
    ('local_file2.py', 'src/file2.py'),
    ('README.md', 'README.md')
]

github.batch_upload(file_mappings, "Batch update multiple files")
```

## 🎯 常见使用场景

### 1. 快速更新文档
```bash
# 编辑README后快速上传
./github_sync.py upload -f README.md -g README.md -m "Update documentation"
```

### 2. 代码文件更新
```bash
# 更新核心代码文件
./github_sync.py upload -f main.py -g main.py -m "Fix: improve image processing logic"
```

### 3. 项目全量同步
```bash
# 开发完成后同步所有更改
./github_sync.py sync -m "Release v1.2.0: Add screenshot mode and single file support"
```

### 4. 配置文件更新
```bash
# 更新配置文件
./github_sync.py upload -f config.py -g config.py -m "Update: enhance screenshot prompt accuracy"
```

## 🛡️ 安全说明

- Token会保存在本地 `.env` 文件中，已在 `.gitignore` 中排除
- 工具自动忽略敏感文件（`.env`, `.git`, `__pycache__` 等）
- Token只需要 `repo` 权限，不会访问其他数据

## 🔄 与传统方法对比

| 操作 | 传统网页方式 | GitHub同步工具 |
|------|-------------|----------------|
| 单文件更新 | 打开浏览器→找到文件→编辑→保存→填写提交信息 | `./github_sync.py upload -f file.py -g file.py -m "update"` |
| 多文件更新 | 重复上述步骤N次 | `./github_sync.py sync -m "batch update"` |
| 时间消耗 | 5-10分钟 | 10-30秒 |
| 出错概率 | 较高（手工操作） | 极低（自动化） |

## 🐛 故障排除

### Token权限问题
```bash
❌ 403 Forbidden
```
**解决**: 确保token有 `repo` 权限

### 文件已存在错误
```bash
⚠️ File already exists
```
**解决**: 使用 `--force` 参数强制更新

### 网络连接问题
```bash
❌ Connection error
```
**解决**: 检查网络连接，或稍后重试

## 💡 高效工作流建议

1. **开发阶段**: 使用 `--dry-run` 测试
2. **单文件更新**: 用 `upload` 命令
3. **批量更新**: 用 `sync` 命令  
4. **自动化**: 写脚本调用GitHub同步工具

这个工具让你从繁琐的网页操作中解放出来，专注于代码开发！