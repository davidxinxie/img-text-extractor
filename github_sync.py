#!/usr/bin/env python3
"""
GitHub Sync Tool - 自动化GitHub仓库更新
支持文件上传、更新、提交等操作，替代手工网页操作

作者: Claude Code Assistant
用法: ./github_sync.py [命令] [选项]
"""

import os
import sys
import json
import base64
import argparse
import subprocess
from pathlib import Path
from typing import Optional, Dict, List, Tuple
import requests
from datetime import datetime
from dotenv import load_dotenv

# 加载.env文件
load_dotenv()


class GitHubSyncTool:
    """GitHub同步工具类"""
    
    def __init__(self, token: Optional[str] = None, repo_owner: str = "", repo_name: str = ""):
        """
        初始化GitHub同步工具
        
        Args:
            token: GitHub Personal Access Token
            repo_owner: 仓库所有者用户名
            repo_name: 仓库名称
        """
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.repo_owner = repo_owner or self._get_repo_info()[0]
        self.repo_name = repo_name or self._get_repo_info()[1]
        
        if not self.token:
            raise ValueError("GitHub token is required. Set GITHUB_TOKEN environment variable or pass token parameter.")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.github.com'
    
    def _get_repo_info(self) -> Tuple[str, str]:
        """从git remote获取仓库信息"""
        try:
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, check=True)
            remote_url = result.stdout.strip()
            
            # 解析不同格式的remote URL
            if 'github.com' in remote_url:
                if remote_url.startswith('git@'):
                    # SSH格式: git@github.com:owner/repo.git
                    parts = remote_url.split(':')[1].replace('.git', '').split('/')
                elif remote_url.startswith('https://'):
                    # HTTPS格式: https://github.com/owner/repo.git
                    parts = remote_url.replace('https://github.com/', '').replace('.git', '').split('/')
                else:
                    return "", ""
                
                if len(parts) >= 2:
                    return parts[0], parts[1]
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return "", ""
    
    def test_connection(self) -> bool:
        """测试GitHub API连接"""
        try:
            response = requests.get(f'{self.base_url}/user', headers=self.headers)
            if response.status_code == 200:
                user_info = response.json()
                print(f"✅ Connected to GitHub as: {user_info.get('login', 'Unknown')}")
                return True
            else:
                print(f"❌ GitHub API connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Connection error: {e}")
            return False
    
    def get_file_sha(self, file_path: str, branch: str = 'main') -> Optional[str]:
        """获取文件的SHA值（用于更新文件）"""
        url = f'{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{file_path}'
        params = {'ref': branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            if response.status_code == 200:
                return response.json().get('sha')
            return None
        except Exception:
            return None
    
    def upload_file(self, local_path: str, github_path: str, 
                   commit_message: str, branch: str = 'main',
                   update_if_exists: bool = True) -> bool:
        """
        上传或更新文件到GitHub
        
        Args:
            local_path: 本地文件路径
            github_path: GitHub中的文件路径
            commit_message: 提交信息
            branch: 目标分支
            update_if_exists: 如果文件已存在是否更新
        """
        if not os.path.exists(local_path):
            print(f"❌ Local file not found: {local_path}")
            return False
        
        # 读取文件内容并编码
        try:
            with open(local_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            print(f"❌ Failed to read file {local_path}: {e}")
            return False
        
        # 检查文件是否已存在
        existing_sha = self.get_file_sha(github_path, branch)
        
        # 构建API请求
        url = f'{self.base_url}/repos/{self.repo_owner}/{self.repo_name}/contents/{github_path}'
        data = {
            'message': commit_message,
            'content': content,
            'branch': branch
        }
        
        # 如果文件已存在，添加SHA用于更新
        if existing_sha:
            if not update_if_exists:
                print(f"⚠️  File {github_path} already exists. Use --force to update.")
                return False
            data['sha'] = existing_sha
            action = "Updated"
        else:
            action = "Created"
        
        try:
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                commit_url = result['commit']['html_url']
                print(f"✅ {action} {github_path}")
                print(f"   Commit: {commit_url}")
                return True
            else:
                print(f"❌ Failed to upload {github_path}: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Upload error: {e}")
            return False
    
    def batch_upload(self, file_mappings: List[Tuple[str, str]], 
                    commit_message: str, branch: str = 'main') -> bool:
        """
        批量上传文件
        
        Args:
            file_mappings: [(local_path, github_path), ...] 文件映射列表
            commit_message: 提交信息
            branch: 目标分支
        """
        success_count = 0
        total_count = len(file_mappings)
        
        print(f"📤 Starting batch upload of {total_count} files...")
        
        for i, (local_path, github_path) in enumerate(file_mappings, 1):
            print(f"\n[{i}/{total_count}] Uploading {github_path}...")
            
            if self.upload_file(local_path, github_path, 
                              f"{commit_message} ({i}/{total_count})", branch):
                success_count += 1
        
        print(f"\n📊 Upload Summary:")
        print(f"   ✅ Successful: {success_count}/{total_count}")
        print(f"   ❌ Failed: {total_count - success_count}/{total_count}")
        
        return success_count == total_count
    
    def sync_repository(self, local_dir: str = ".", 
                       ignore_patterns: List[str] = None,
                       commit_message: str = None) -> bool:
        """
        同步整个仓库到GitHub
        
        Args:
            local_dir: 本地目录路径
            ignore_patterns: 忽略的文件模式列表
            commit_message: 提交信息
        """
        if ignore_patterns is None:
            ignore_patterns = ['.git', '.env', '__pycache__', '*.pyc', '.DS_Store']
        
        if commit_message is None:
            commit_message = f"Auto-sync repository - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        local_path = Path(local_dir).resolve()
        file_mappings = []
        
        # 扫描本地文件
        for file_path in local_path.rglob('*'):
            if file_path.is_file():
                relative_path = file_path.relative_to(local_path)
                
                # 检查是否应该忽略
                should_ignore = False
                for pattern in ignore_patterns:
                    if pattern in str(relative_path):
                        should_ignore = True
                        break
                
                if not should_ignore:
                    github_path = str(relative_path).replace('\\', '/')
                    file_mappings.append((str(file_path), github_path))
        
        print(f"🔍 Found {len(file_mappings)} files to sync")
        return self.batch_upload(file_mappings, commit_message)


def setup_github_token():
    """配置GitHub Token的交互式设置"""
    print("🔑 GitHub Personal Access Token Setup")
    print("=" * 50)
    print("1. 访问: https://github.com/settings/tokens")
    print("2. 点击 'Generate new token (classic)'")
    print("3. 选择权限: repo (Full control of private repositories)")
    print("4. 生成并复制token")
    print()
    
    token = input("请输入你的GitHub Personal Access Token: ").strip()
    
    if token:
        # 保存到.env文件
        env_path = Path('.env')
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                content = f.read()
            
            # 更新或添加GITHUB_TOKEN
            lines = content.split('\n')
            updated = False
            for i, line in enumerate(lines):
                if line.startswith('GITHUB_TOKEN='):
                    lines[i] = f'GITHUB_TOKEN={token}'
                    updated = True
                    break
            
            if not updated:
                lines.append(f'GITHUB_TOKEN={token}')
            
            with open(env_path, 'w') as f:
                f.write('\n'.join(lines))
        else:
            with open(env_path, 'w') as f:
                f.write(f'GITHUB_TOKEN={token}\n')
        
        print(f"✅ Token saved to {env_path}")
        return token
    else:
        print("❌ No token provided")
        return None


def main():
    parser = argparse.ArgumentParser(description='GitHub同步工具 - 自动化GitHub仓库更新')
    parser.add_argument('command', choices=['setup', 'test', 'upload', 'sync'], 
                       help='执行的命令')
    parser.add_argument('--file', '-f', help='要上传的本地文件路径')
    parser.add_argument('--github-path', '-g', help='GitHub中的目标路径')
    parser.add_argument('--message', '-m', help='提交信息')
    parser.add_argument('--branch', '-b', default='main', help='目标分支 (默认: main)')
    parser.add_argument('--force', action='store_true', help='强制更新已存在的文件')
    parser.add_argument('--repo', help='仓库格式: owner/repo')
    parser.add_argument('--token', help='GitHub Personal Access Token')
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup_github_token()
        return
    
    # 解析仓库信息
    repo_owner, repo_name = "", ""
    if args.repo:
        parts = args.repo.split('/')
        if len(parts) == 2:
            repo_owner, repo_name = parts
    
    try:
        # 初始化GitHub同步工具
        github = GitHubSyncTool(token=args.token, 
                               repo_owner=repo_owner, 
                               repo_name=repo_name)
        
        if args.command == 'test':
            github.test_connection()
        
        elif args.command == 'upload':
            if not args.file or not args.github_path:
                print("❌ --file and --github-path are required for upload command")
                return
            
            commit_msg = args.message or f"Upload {args.github_path}"
            github.upload_file(args.file, args.github_path, commit_msg, 
                             args.branch, args.force)
        
        elif args.command == 'sync':
            commit_msg = args.message or f"Auto-sync - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            github.sync_repository(commit_message=commit_msg)
    
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("💡 Run './github_sync.py setup' to configure GitHub token")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == '__main__':
    main()