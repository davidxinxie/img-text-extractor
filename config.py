import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# 支持的图片格式
SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.heic', '.heif'}

# 图片识别提示词 - 优化为搜索友好的格式
VISION_PROMPT = """分析这张图片并生成搜索友好的描述。请按以下格式输出：

主要内容：[简短描述主体内容]
对象：[列出具体的物体、人物等，用空格分隔]
场景：[描述环境场所]
颜色：[主要颜色]
风格：[如现代、复古、卡通等]
文字：[如有文字内容则列出]
情感：[如快乐、宁静、热闹等]

要求：
1. 每个分类用简洁的关键词，避免完整句子
2. 优先使用常用搜索词汇
3. 用中文输出
4. 如某类别无内容可省略

示例：
主要内容：海边日落风景照
对象：太阳 海浪 沙滩 椰子树 情侣
场景：海滩 黄昏
颜色：橙色 金色 蓝色
风格：自然风光
情感：浪漫 宁静"""

# Spotlight索引的metadata字段
METADATA_FIELDS = {
    'description': 'ImageDescription',
    'comment': 'UserComment', 
    'subject': 'Subject',
    'keywords': 'Keywords'
}