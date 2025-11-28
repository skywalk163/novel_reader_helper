# Configuration settings for Novel Reader Helper

# OCR Service
OCR_SERVICE_URL = "http://127.0.0.1:5000"

# UI Settings
WINDOW_TITLE = "小说阅读神器 v1.2"
WINDOW_SIZE = "1000x700"

# Content Processing
MAX_CONTENT_LENGTH = 50000
MAX_SEGMENT_LENGTH = 5000

# Default values
DEFAULT_KEYWORD_NUM = 8
DEFAULT_SUMMARY_NUM = 5

# File paths
TEST_IMAGE_PATH = r"E:\comatework\novel_reader_helper\test.png"

# Search engine URL
SEARCH_ENGINE_URL = "https://www.baidu.com/s?wd={}"

# AI Configuration
AI_CONFIG_DIR = "config"
AI_CONFIG_FILE = "ai_models.json"
AI_BACKUP_DIR = "backups"
AI_MAX_RETRIES = 3
AI_TIMEOUT = 30
AI_MAX_TOKENS = 500
AI_TEMPERATURE = 0.7

# AI Default Templates
AI_TEMPLATES = {
    "openai": {
        "name": "OpenAI ChatGPT",
        "base_url": "https://api.openai.com/v1",
        "model_name": "gpt-3.5-turbo",
        "description": "OpenAI官方API服务"
    },
    "azure": {
        "name": "Azure OpenAI",
        "base_url": "https://your-resource.openai.azure.com/",
        "model_name": "gpt-35-turbo",
        "description": "微软Azure OpenAI服务"
    },
    "localai": {
        "name": "LocalAI",
        "base_url": "http://localhost:8080/v1",
        "model_name": "gpt-3.5-turbo",
        "description": "本地部署的LocalAI服务"
    },
    "ollama": {
        "name": "Ollama",
        "base_url": "http://localhost:11434/v1",
        "model_name": "llama2",
        "description": "本地部署的Ollama服务"
    }
}

# AI Summary Prompts
AI_SUMMARY_PROMPT = """你是一个专业的小说内容分析师。请对提供的小说章节内容进行总结，要求：
1. 提取主要情节和关键信息
2. 总结要简洁明了，控制在3-5句话内
3. 重点关注故事发展和重要事件
4. 不要添加原书中没有的内容
5. 使用客观中性的语气进行总结"""

AI_ANALYSIS_PROMPT = """你是一个专业的文学分析师。请对以下小说章节进行全面分析，包括：
1. 情节发展和关键事件
2. 主要角色及其特征
3. 主题思想和情感基调
4. 文学手法和写作特点"""
