#!/usr/bin/env python3
"""
测试文件，用于验证 main.py 的主要功能
确保修改后的逐张处理逻辑正常工作
"""
import os
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
import shutil

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import find_images, main
from config import SUPPORTED_IMAGE_FORMATS


class TestFindImages(unittest.TestCase):
    """测试图片查找功能"""
    
    def setUp(self):
        """创建临时测试目录"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        
        # 创建测试文件
        self.test_files = [
            'image1.jpg',
            'image2.png', 
            'image3.jpeg',
            'not_image.txt',
            'subdir/image4.jpg',
            'subdir/image5.gif'
        ]
        
        for file_path in self.test_files:
            full_path = Path(self.test_dir) / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.touch()
    
    def test_find_images_recursive(self):
        """测试递归查找图片"""
        images = find_images(self.test_dir, recursive=True)
        
        # 应该找到所有支持的图片格式
        expected_images = [
            'image1.jpg',
            'image2.png',
            'image3.jpeg',
            'subdir/image4.jpg',
            'subdir/image5.gif'
        ]
        
        # 检查找到的文件数量
        self.assertEqual(len(images), len(expected_images))
        
        # 检查每个文件都被找到（使用相对路径比较）
        found_basenames = [os.path.relpath(img, self.test_dir) for img in images]
        for expected in expected_images:
            self.assertIn(expected, found_basenames)
    
    def test_find_images_non_recursive(self):
        """测试非递归查找图片"""
        images = find_images(self.test_dir, recursive=False)
        
        # 应该只找到根目录下的图片
        expected_count = 3  # image1.jpg, image2.png, image3.jpeg
        self.assertEqual(len(images), expected_count)
        
        # 确保没有子目录中的图片
        for img in images:
            self.assertNotIn('subdir', img)
    
    def test_find_images_nonexistent_directory(self):
        """测试不存在的目录"""
        with self.assertRaises(FileNotFoundError):
            find_images('/nonexistent/directory')
    
    def test_find_images_file_instead_of_directory(self):
        """测试传入文件而不是目录"""
        test_file = os.path.join(self.test_dir, 'test.txt')
        Path(test_file).touch()
        
        with self.assertRaises(ValueError):
            find_images(test_file)


class TestMainFunction(unittest.TestCase):
    """测试主函数的逐张处理逻辑"""
    
    def setUp(self):
        """设置测试环境"""
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        
        # 创建测试图片文件
        self.test_images = ['img1.jpg', 'img2.png', 'img3.jpeg']
        for img in self.test_images:
            (Path(self.test_dir) / img).touch()
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_dry_run_mode(self, mock_metadata_writer, mock_image_analyzer):
        """测试预览模式"""
        # 设置 mock
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        
        mock_analyzer_instance = Mock()
        mock_analyzer_instance.analyze_image.return_value = "测试描述"
        mock_image_analyzer.return_value = mock_analyzer_instance
        
        mock_writer_instance.parse_description.return_value = {'summary': '测试'}
        mock_writer_instance.extract_keywords.return_value = ['测试', '关键词']
        
        # 修改 sys.argv
        with patch('sys.argv', ['main.py', self.test_dir, '--dry-run']):
            result = main()
        
        self.assertEqual(result, 0)
        # 在预览模式下不应该调用写入方法
        mock_writer_instance.write_metadata.assert_not_called()
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_skip_existing_metadata(self, mock_metadata_writer, mock_image_analyzer):
        """测试跳过已有 metadata 的图片"""
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        
        mock_analyzer_instance = Mock()
        mock_image_analyzer.return_value = mock_analyzer_instance
        
        # 模拟第一张图片已有 metadata，第二张没有
        mock_writer_instance.verify_metadata.side_effect = [
            {'description': '已有描述'},  # img1.jpg 已有 metadata
            None,  # img2.png 没有 metadata
            None   # img3.jpeg 没有 metadata
        ]
        
        mock_analyzer_instance.analyze_image.return_value = "新描述"
        mock_writer_instance.parse_description.return_value = {'summary': '新描述'}
        mock_writer_instance.extract_keywords.return_value = ['关键词']
        mock_writer_instance.write_metadata.return_value = True
        mock_writer_instance.trigger_spotlight_reindex = Mock()
        
        with patch('sys.argv', ['main.py', self.test_dir]):
            result = main()
        
        self.assertEqual(result, 0)
        
        # 验证只有两张图片被分析（跳过了第一张）
        self.assertEqual(mock_analyzer_instance.analyze_image.call_count, 2)
        self.assertEqual(mock_writer_instance.write_metadata.call_count, 2)
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_force_mode_reprocess_all(self, mock_metadata_writer, mock_image_analyzer):
        """测试强制模式重新处理所有图片"""
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        
        mock_analyzer_instance = Mock()
        mock_image_analyzer.return_value = mock_analyzer_instance
        
        # 即使有 metadata 也应该重新处理
        mock_writer_instance.verify_metadata.return_value = {'description': '旧描述'}
        mock_analyzer_instance.analyze_image.return_value = "新描述"
        mock_writer_instance.parse_description.return_value = {'summary': '新描述'}
        mock_writer_instance.extract_keywords.return_value = ['关键词']
        mock_writer_instance.write_metadata.return_value = True
        mock_writer_instance.trigger_spotlight_reindex = Mock()
        
        with patch('sys.argv', ['main.py', self.test_dir, '--force']):
            result = main()
        
        self.assertEqual(result, 0)
        
        # 验证所有图片都被分析
        self.assertEqual(mock_analyzer_instance.analyze_image.call_count, 3)
        self.assertEqual(mock_writer_instance.write_metadata.call_count, 3)
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_verify_mode(self, mock_metadata_writer, mock_image_analyzer):
        """测试验证模式"""
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        
        # 模拟验证结果
        mock_writer_instance.verify_metadata.side_effect = [
            {'description': '描述1', 'keywords': '关键词1'},
            None,
            {'description': '描述3'}
        ]
        
        with patch('sys.argv', ['main.py', self.test_dir, '--verify']):
            result = main()
        
        self.assertEqual(result, 0)
        
        # 验证模式不应该初始化 ImageAnalyzer
        mock_image_analyzer.assert_not_called()
        
        # 应该调用 verify_metadata 检查每张图片
        self.assertEqual(mock_writer_instance.verify_metadata.call_count, 3)
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_all_images_have_metadata(self, mock_metadata_writer, mock_image_analyzer):
        """测试所有图片都有 metadata 的情况"""
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        
        # 所有图片都有 metadata
        mock_writer_instance.verify_metadata.return_value = {'description': '已有描述'}
        
        with patch('sys.argv', ['main.py', self.test_dir]):
            result = main()
        
        self.assertEqual(result, 0)
        
        # 不应该初始化 ImageAnalyzer
        mock_image_analyzer.assert_not_called()
        
        # 应该检查所有图片的 metadata
        self.assertEqual(mock_writer_instance.verify_metadata.call_count, 3)
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_analyzer_initialization_failure(self, mock_metadata_writer, mock_image_analyzer):
        """测试图片分析器初始化失败"""
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        mock_writer_instance.verify_metadata.return_value = None
        
        # 模拟初始化失败
        mock_image_analyzer.side_effect = ValueError("API key not found")
        
        with patch('sys.argv', ['main.py', self.test_dir]):
            result = main()
        
        self.assertEqual(result, 1)
    
    def test_no_images_found(self):
        """测试没有找到图片文件的情况"""
        empty_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, empty_dir)
        
        with patch('sys.argv', ['main.py', empty_dir]):
            result = main()
        
        self.assertEqual(result, 1)
    
    @patch('main.find_images')
    def test_keyboard_interrupt(self, mock_find_images):
        """测试用户中断"""
        mock_find_images.side_effect = KeyboardInterrupt()
        
        with patch('sys.argv', ['main.py', self.test_dir]):
            result = main()
        
        self.assertEqual(result, 130)


class TestMultipleDirectories(unittest.TestCase):
    """测试多目录处理功能"""
    
    def setUp(self):
        # 创建两个测试目录
        self.test_dir1 = tempfile.mkdtemp()
        self.test_dir2 = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir1)
        self.addCleanup(shutil.rmtree, self.test_dir2)
        
        # 目录1中创建2张图片
        for i in range(1, 3):
            (Path(self.test_dir1) / f'img{i}.jpg').touch()
        
        # 目录2中创建3张图片
        for i in range(3, 6):
            (Path(self.test_dir2) / f'img{i}.jpg').touch()
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_multiple_directories(self, mock_metadata_writer, mock_image_analyzer):
        """测试多目录处理"""
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        
        mock_analyzer_instance = Mock()
        mock_image_analyzer.return_value = mock_analyzer_instance
        
        # 所有图片都没有metadata
        mock_writer_instance.verify_metadata.return_value = None
        mock_analyzer_instance.analyze_image.return_value = "测试描述"
        mock_writer_instance.parse_description.return_value = {'summary': '测试'}
        mock_writer_instance.extract_keywords.return_value = ['关键词']
        mock_writer_instance.write_metadata.return_value = True
        mock_writer_instance.trigger_spotlight_reindex = Mock()
        
        with patch('sys.argv', ['main.py', self.test_dir1, self.test_dir2]):
            result = main()
        
        self.assertEqual(result, 0)
        
        # 验证处理了所有5张图片（2+3）
        self.assertEqual(mock_analyzer_instance.analyze_image.call_count, 5)
        self.assertEqual(mock_writer_instance.write_metadata.call_count, 5)
        
        # 验证两个目录都触发了Spotlight重新索引
        self.assertEqual(mock_writer_instance.trigger_spotlight_reindex.call_count, 2)
        mock_writer_instance.trigger_spotlight_reindex.assert_any_call(self.test_dir1)
        mock_writer_instance.trigger_spotlight_reindex.assert_any_call(self.test_dir2)


class TestProgressiveProcessing(unittest.TestCase):
    """测试逐张处理的逻辑"""
    
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.test_dir)
        
        # 创建5张测试图片
        for i in range(1, 6):
            (Path(self.test_dir) / f'img{i}.jpg').touch()
    
    @patch('main.ImageAnalyzer')
    @patch('main.MetadataWriter')
    def test_progressive_processing_order(self, mock_metadata_writer, mock_image_analyzer):
        """测试逐张处理的顺序"""
        mock_writer_instance = Mock()
        mock_metadata_writer.return_value = mock_writer_instance
        
        mock_analyzer_instance = Mock()
        mock_image_analyzer.return_value = mock_analyzer_instance
        
        # 模拟前两张有 metadata，后三张没有
        verify_results = [
            {'description': '描述1'},  # img1.jpg 有
            {'description': '描述2'},  # img2.jpg 有  
            None,  # img3.jpg 没有
            None,  # img4.jpg 没有
            None   # img5.jpg 没有
        ]
        mock_writer_instance.verify_metadata.side_effect = verify_results
        
        mock_analyzer_instance.analyze_image.return_value = "新描述"
        mock_writer_instance.parse_description.return_value = {'summary': '新描述'}
        mock_writer_instance.extract_keywords.return_value = ['关键词']
        mock_writer_instance.write_metadata.return_value = True
        mock_writer_instance.trigger_spotlight_reindex = Mock()
        
        with patch('sys.argv', ['main.py', self.test_dir]):
            result = main()
        
        self.assertEqual(result, 0)
        
        # 验证 verify_metadata 按顺序调用了所有图片
        self.assertEqual(mock_writer_instance.verify_metadata.call_count, 5)
        
        # 验证只处理了没有 metadata 的3张图片
        self.assertEqual(mock_analyzer_instance.analyze_image.call_count, 3)
        self.assertEqual(mock_writer_instance.write_metadata.call_count, 3)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)