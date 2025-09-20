import base64
import os
from typing import Optional
from PIL import Image
from openai import OpenAI
from config import OPENAI_API_KEY, VISION_PROMPT, SCREENSHOT_VISION_PROMPT, SUPPORTED_IMAGE_FORMATS

# 启用HEIC/HEIF支持
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
    HEIC_SUPPORTED = True
except ImportError:
    HEIC_SUPPORTED = False
    print("⚠️  pillow-heif未安装，HEIC格式将被跳过")


class ImageAnalyzer:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("请在 .env 文件中设置 OPENAI_API_KEY")
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    def is_supported_format(self, file_path: str) -> bool:
        """检查文件格式是否支持"""
        ext = os.path.splitext(file_path.lower())[1]
        
        # 检查HEIC/HEIF格式
        if ext in {'.heic', '.heif'}:
            if not HEIC_SUPPORTED:
                print(f"  ⚠️  HEIC格式需要pillow-heif支持，跳过: {os.path.basename(file_path)}")
                return False
            return True
        
        return ext in SUPPORTED_IMAGE_FORMATS
    
    def encode_image(self, image_path: str) -> str:
        """将图片编码为base64"""
        try:
            # 使用PIL优化图片大小以减少API调用成本
            with Image.open(image_path) as img:
                # 如果图片太大，调整大小
                max_size = (1024, 1024)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # 转换为RGB格式（如果需要）
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                
                # 保存到内存并编码
                import io
                buffer = io.BytesIO()
                format_name = 'PNG' if img.mode == 'RGBA' else 'JPEG'
                img.save(buffer, format=format_name, quality=85)
                return base64.b64encode(buffer.getvalue()).decode('utf-8')
                
        except Exception as e:
            raise ValueError(f"无法读取图片 {image_path}: {str(e)}")
    
    def analyze_image(self, image_path: str, screenshot_mode: bool = False) -> Optional[str]:
        """分析单张图片并返回描述
        
        Args:
            image_path: 图片路径
            screenshot_mode: 是否使用截图模式（专门优化文字识别）
        """
        if not self.is_supported_format(image_path):
            print(f"跳过不支持的格式: {image_path}")
            return None
            
        try:
            # 编码图片
            base64_image = self.encode_image(image_path)
            
            # 根据模式选择提示词和token限制
            if screenshot_mode:
                prompt = SCREENSHOT_VISION_PROMPT
                max_tokens = 500  # 截图模式需要更多token来描述文字内容
                mode_text = "截图模式"
            else:
                prompt = VISION_PROMPT
                max_tokens = 300
                mode_text = "普通模式"
            
            # 调用OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 使用cost-effective的模型
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=max_tokens
            )
            
            description = response.choices[0].message.content.strip()
            print(f"✅ 已分析（{mode_text}）: {os.path.basename(image_path)}")
            return description
            
        except Exception as e:
            print(f"❌ 分析失败 {image_path}: {str(e)}")
            return None
    
    def batch_analyze(self, image_paths: list, screenshot_mode: bool = False) -> dict:
        """批量分析图片
        
        Args:
            image_paths: 图片路径列表
            screenshot_mode: 是否使用截图模式
        """
        results = {}
        
        for i, image_path in enumerate(image_paths, 1):
            print(f"[{i}/{len(image_paths)}] 正在分析: {os.path.basename(image_path)}")
            description = self.analyze_image(image_path, screenshot_mode)
            if description:
                results[image_path] = description
        
        return results