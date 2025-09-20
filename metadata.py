import subprocess
import os
import shutil
import stat
from typing import Optional, Dict, List
from config import METADATA_FIELDS


class MetadataWriter:
    def __init__(self):
        # 检查exiftool是否可用
        if not shutil.which('exiftool'):
            raise RuntimeError("exiftool 未安装。请运行: brew install exiftool")
        self._current_base_dir = None  # 用于显示相对路径
    
    def _get_display_path(self, image_path: str) -> str:
        """获取用于显示的路径（相对路径或文件名）"""
        if self._current_base_dir and os.path.commonpath([image_path, self._current_base_dir]):
            try:
                return os.path.relpath(image_path, self._current_base_dir)
            except ValueError:
                pass
        return os.path.basename(image_path)
    
    def extract_keywords_screenshot(self, description: str) -> List[str]:
        """从截图模式的结构化描述中提取关键词（专门优化文字搜索）"""
        keywords = set()
        
        try:
            lines = description.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 截图模式的特殊字段处理
                if line.startswith('文字内容：'):
                    # 这是最重要的部分，包含所有可见文字
                    text_content = line[5:].strip()
                    if text_content:
                        # 按空格分词，保留所有文字
                        words = text_content.split()
                        for word in words:
                            word = word.strip()
                            if len(word) >= 1:  # 截图模式保留更多短词
                                keywords.add(word)
                
                elif line.startswith('应用信息：'):
                    app_info = line[5:].strip()
                    if app_info:
                        keywords.update(word.strip() for word in app_info.split())
                
                elif line.startswith('界面元素：'):
                    ui_elements = line[5:].strip()
                    if ui_elements:
                        keywords.update(elem.strip() for elem in ui_elements.split())
                
                elif line.startswith('功能区域：'):
                    areas = line[5:].strip()
                    if areas:
                        keywords.update(area.strip() for area in areas.split())
                
                elif line.startswith('主要内容：'):
                    content = line[5:].strip()
                    if content:
                        # 从主要内容中提取关键词
                        content_words = content.replace('，', ' ').replace('。', ' ').split()
                        keywords.update(word.strip() for word in content_words if len(word.strip()) > 1)
                
                elif line.startswith('主题色彩：'):
                    colors = line[5:].strip()
                    if colors:
                        keywords.update(color.strip() for color in colors.split())
            
            # 截图模式不过滤短词，因为UI文字可能包含重要的短词汇
            filtered_keywords = [
                kw for kw in keywords 
                if len(kw) >= 1 and not all(c in '，。、！？：；' for c in kw)
            ]
            
            # 限制关键词数量，优先保留较长的关键词
            sorted_keywords = sorted(filtered_keywords, key=len, reverse=True)
            return sorted_keywords[:25]  # 截图模式可以有更多关键词
            
        except Exception as e:
            print(f"截图关键词提取出错，使用备用方案: {e}")
            # 备用方案：简单分词
            words = description.replace('，', ' ').replace('。', ' ').replace('：', ' ').split()
            return [word.strip() for word in words if len(word.strip()) >= 1][:20]

    def extract_keywords(self, description: str) -> List[str]:
        """从结构化描述中提取关键词"""
        keywords = set()  # 使用set避免重复
        
        try:
            # 解析结构化描述的各个部分
            lines = description.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # 提取各个分类的内容
                if line.startswith('对象：'):
                    objects = line[3:].strip()
                    if objects:
                        keywords.update(obj.strip() for obj in objects.split())
                        
                elif line.startswith('场景：'):
                    scene = line[3:].strip()
                    if scene:
                        keywords.update(word.strip() for word in scene.split())
                        
                elif line.startswith('颜色：'):
                    colors = line[3:].strip()
                    if colors:
                        keywords.update(color.strip() for color in colors.split())
                        
                elif line.startswith('风格：'):
                    style = line[3:].strip()
                    if style:
                        keywords.update(s.strip() for s in style.split())
                        
                elif line.startswith('文字：'):
                    text_content = line[3:].strip()
                    if text_content and text_content != '无':
                        # 对文字内容进行简单分词
                        words = text_content.replace('，', ' ').replace('。', ' ').split()
                        keywords.update(word.strip() for word in words if len(word.strip()) > 1)
                        
                elif line.startswith('情感：'):
                    emotions = line[3:].strip()
                    if emotions:
                        keywords.update(emotion.strip() for emotion in emotions.split())
                        
                elif line.startswith('主要内容：'):
                    content = line[5:].strip()
                    if content:
                        # 从主要内容中提取关键词
                        content_words = content.replace('，', ' ').replace('。', ' ').split()
                        keywords.update(word.strip() for word in content_words if len(word.strip()) > 1)
            
            # 过滤掉过短的词和标点符号
            filtered_keywords = [
                kw for kw in keywords 
                if len(kw) >= 2 and not all(c in '，。、！？：；' for c in kw)
            ]
            
            # 限制关键词数量，优先保留较长的关键词（通常更具描述性）
            sorted_keywords = sorted(filtered_keywords, key=len, reverse=True)
            return sorted_keywords[:15]  # 增加到15个关键词
            
        except Exception as e:
            print(f"关键词提取出错，使用备用方案: {e}")
            # 备用方案：简单分词
            words = description.replace('，', ' ').replace('。', ' ').replace('：', ' ').split()
            return [word.strip() for word in words if len(word.strip()) >= 2][:10]
    
    def parse_description_screenshot(self, description: str) -> Dict[str, str]:
        """解析截图模式的结构化描述，提取各个组件"""
        parsed = {}
        lines = description.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('主要内容：'):
                parsed['summary'] = line[5:].strip()
            elif line.startswith('文字内容：'):
                parsed['text_content'] = line[5:].strip()
            elif line.startswith('应用信息：'):
                parsed['app_info'] = line[5:].strip()
            elif line.startswith('界面元素：'):
                parsed['ui_elements'] = line[5:].strip()
            elif line.startswith('功能区域：'):
                parsed['function_areas'] = line[5:].strip()
            elif line.startswith('主题色彩：'):
                parsed['colors'] = line[5:].strip()
        
        return parsed

    def parse_description(self, description: str) -> Dict[str, str]:
        """解析结构化描述，提取各个组件"""
        parsed = {}
        lines = description.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('主要内容：'):
                parsed['summary'] = line[5:].strip()
            elif line.startswith('对象：'):
                parsed['objects'] = line[3:].strip()
            elif line.startswith('场景：'):
                parsed['scene'] = line[3:].strip()
            elif line.startswith('颜色：'):
                parsed['colors'] = line[3:].strip()
            elif line.startswith('风格：'):
                parsed['style'] = line[3:].strip()
            elif line.startswith('文字：'):
                parsed['text'] = line[3:].strip()
            elif line.startswith('情感：'):
                parsed['emotion'] = line[3:].strip()
        
        return parsed

    def write_metadata(self, image_path: str, description: str, screenshot_mode: bool = False) -> bool:
        """写入图片metadata并保留原始文件时间"""
        import tempfile
        import shutil
        
        try:
            # 1. 文件安全检查
            display_path = self._get_display_path(image_path)
            
            if not os.path.exists(image_path):
                print(f"  ⚠️  文件不存在，跳过: {display_path}")
                return False
            
            if not os.access(image_path, os.R_OK):
                print(f"  ⚠️  文件无读取权限，跳过: {display_path}")
                return False
            
            if not os.access(image_path, os.W_OK):
                print(f"  ⚠️  文件无写入权限，跳过: {display_path}")
                return False
            
            # 2. 文件完整性检查
            try:
                file_stat = os.stat(image_path)
                if file_stat.st_size == 0:
                    print(f"  ⚠️  文件为空，跳过: {display_path}")
                    return False
            except OSError as e:
                print(f"  ⚠️  文件状态异常，跳过: {display_path} - {e}")
                return False
            
            # 3. 创建备份文件（在临时目录）
            backup_fd, backup_path = tempfile.mkstemp(suffix='.backup', prefix='img_metadata_')
            try:
                with os.fdopen(backup_fd, 'wb') as backup_file:
                    with open(image_path, 'rb') as original_file:
                        shutil.copyfileobj(original_file, backup_file)
                print(f"  💾 已创建临时备份: {os.path.basename(backup_path)}")
            except Exception as e:
                os.close(backup_fd)
                if os.path.exists(backup_path):
                    os.unlink(backup_path)
                print(f"  ❌ 备份创建失败，跳过处理: {e}")
                return False
            
            # 保存原始文件的时间信息
            original_atime = file_stat.st_atime  # 访问时间
            original_mtime = file_stat.st_mtime  # 修改时间
            
            # 根据模式选择解析方法
            if screenshot_mode:
                parsed = self.parse_description_screenshot(description)
                keywords = self.extract_keywords_screenshot(description)
            else:
                parsed = self.parse_description(description)
                keywords = self.extract_keywords(description)
            keywords_str = ', '.join(keywords) if keywords else ''
            
            # 根据模式创建搜索优化的短描述
            search_description_parts = []
            if screenshot_mode:
                # 截图模式：优先文字内容和应用信息
                if 'summary' in parsed:
                    search_description_parts.append(parsed['summary'])
                if 'text_content' in parsed:
                    # 截取文字内容的前部分作为搜索描述
                    text_content = parsed['text_content']
                    if len(text_content) > 100:
                        text_content = text_content[:100] + "..."
                    search_description_parts.append(text_content)
                if 'app_info' in parsed:
                    search_description_parts.append(parsed['app_info'])
            else:
                # 普通模式：原有逻辑
                if 'summary' in parsed:
                    search_description_parts.append(parsed['summary'])
                if 'objects' in parsed:
                    search_description_parts.append(parsed['objects'])
                if 'scene' in parsed:
                    search_description_parts.append(parsed['scene'])
            
            search_description = ' '.join(search_description_parts)
            
            # 4. 构建安全的exiftool命令
            cmd = [
                'exiftool',
                '-charset', 'utf8',     # 支持中文
                '-codedcharacterset=utf8',  # 强制UTF-8编码
                '-preserve',  # 保留文件时间戳
                '-P',  # 保持原始文件修改时间
                '-quiet',  # 减少输出
                # 注意：不使用 -overwrite_original，让exiftool创建备份
            ]
            
            # 分层写入不同信息：
            # 1. Subject和Caption-Abstract：用搜索优化的短描述
            if search_description:
                cmd.extend([
                    f'-Subject={search_description}',
                    f'-Caption-Abstract={search_description}',
                ])
            
            # 2. ImageDescription和UserComment：用完整的结构化描述（便于人读）
            cmd.extend([
                f'-ImageDescription={description}',
                f'-UserComment={description}',
            ])
            
            # 3. XMP:Description：用搜索关键词（Spotlight优先搜索）
            if keywords_str:
                cmd.extend([
                    f'-XMP:Description={keywords_str}',
                ])
            
            # 4. Keywords和XMP:Subject：用提取的关键词
            if keywords_str:
                cmd.extend([
                    f'-Keywords={keywords_str}',
                    f'-XMP:Subject={keywords_str}',
                ])
                
            # 5. 根据模式处理文字内容存储
            if screenshot_mode:
                # 截图模式：文字内容存储到Title和Creator字段（更多搜索入口）
                if 'text_content' in parsed and parsed['text_content']:
                    cmd.extend([
                        f'-XMP:Title={parsed["text_content"]}',
                        f'-Creator={parsed["text_content"][:200]}',  # Creator字段限制长度
                    ])
                # 应用信息存储到Software字段
                if 'app_info' in parsed and parsed['app_info']:
                    cmd.extend([
                        f'-Software={parsed["app_info"]}',
                    ])
            else:
                # 普通模式：原有逻辑
                if 'text' in parsed and parsed['text'] and parsed['text'] != '无':
                    cmd.extend([
                        f'-XMP:Title={parsed["text"]}',
                    ])
            
            cmd.append(image_path)
            
            # 5. 执行exiftool命令
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30  # 30秒超时
            )
            
            if result.returncode == 0:
                # 6. 验证文件完整性
                try:
                    new_stat = os.stat(image_path)
                    if new_stat.st_size == 0:
                        # 文件被破坏，从备份恢复
                        print(f"  ⚠️  检测到文件损坏，正在从备份恢复...")
                        shutil.copy2(backup_path, image_path)
                        os.unlink(backup_path)
                        return False
                    
                    # 文件正常，清理exiftool创建的备份文件
                    exif_backup = image_path + '_original'
                    if os.path.exists(exif_backup):
                        os.unlink(exif_backup)
                    
                    # 恢复原始文件时间
                    os.utime(image_path, (original_atime, original_mtime))
                    print(f"  ✅ Metadata写入成功 ({len(keywords)}个关键词)")
                    
                    # 清理临时备份
                    os.unlink(backup_path)
                    return True
                    
                except Exception as e:
                    print(f"  ⚠️  文件验证失败，从备份恢复: {e}")
                    shutil.copy2(backup_path, image_path)
                    os.unlink(backup_path)
                    return False
            else:
                print(f"  ❌ Metadata写入失败: {result.stderr}")
                # 清理临时备份
                os.unlink(backup_path)
                return False
                
        except subprocess.TimeoutExpired:
            display_path = self._get_display_path(image_path)
            print(f"  ⚠️  操作超时，跳过: {display_path}")
            # 清理备份
            if 'backup_path' in locals() and os.path.exists(backup_path):
                os.unlink(backup_path)
            return False
        except Exception as e:
            display_path = self._get_display_path(image_path)
            print(f"  ❌ 意外错误，跳过: {display_path} - {str(e)}")
            # 清理备份
            if 'backup_path' in locals() and os.path.exists(backup_path):
                os.unlink(backup_path)
            return False
    
    def verify_metadata(self, image_path: str) -> Dict[str, str]:
        """验证metadata是否写入成功"""
        try:
            cmd = [
                'exiftool',
                '-ImageDescription',
                '-UserComment',
                '-Subject',
                '-Keywords',
                '-XMP:Description',
                '-XMP:Subject', 
                '-j',  # JSON输出
                image_path
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            
            if result.returncode == 0:
                import json
                data = json.loads(result.stdout)
                if data:
                    metadata = {k: v for k, v in data[0].items() if v and k != 'SourceFile'}
                    
                    # 检查是否只有默认的Screenshot标记，如果是则认为没有有效metadata
                    if metadata:
                        # 如果只有UserComment且值为"Screenshot"，认为没有有效metadata
                        if len(metadata) == 1 and metadata.get('UserComment') == 'Screenshot':
                            return {}
                        # 检查是否有实际的描述内容
                        has_description = any(
                            field in metadata and len(str(metadata[field]).strip()) > 10
                            for field in ['ImageDescription', 'XMP:Description', 'Subject', 'XMP:Subject']
                        )
                        if has_description:
                            return metadata
                    
            return {}
            
        except Exception as e:
            print(f"验证metadata时出错: {str(e)}")
            return {}
    
    def batch_write_metadata(self, descriptions: Dict[str, str], screenshot_mode: bool = False) -> Dict[str, bool]:
        """批量写入metadata
        
        Args:
            descriptions: 图片路径和描述的字典
            screenshot_mode: 是否使用截图模式
        """
        results = {}
        
        for i, (image_path, description) in enumerate(descriptions.items(), 1):
            print(f"[{i}/{len(descriptions)}] 写入metadata: {os.path.basename(image_path)}")
            success = self.write_metadata(image_path, description, screenshot_mode)
            results[image_path] = success
        
        return results
    
    def trigger_spotlight_reindex(self, directory: str):
        """触发Spotlight重新索引指定目录"""
        try:
            cmd = ['mdimport', '-r', directory]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"✅ 已触发Spotlight重新索引: {directory}")
        except subprocess.CalledProcessError:
            print("⚠️  触发Spotlight重新索引失败，但metadata已写入")