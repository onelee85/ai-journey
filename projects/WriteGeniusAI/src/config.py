import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """系统配置类"""
    # 应用配置
    APP_NAME = os.getenv('APP_NAME', 'WriteGeniusAI')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

    # OpenAI API 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', '')

    # Ollama 配置
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3')

    # API 配置
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))
    API_RETRY_COUNT = int(os.getenv('API_RETRY_COUNT', '3'))

    # 模型配置
    DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'gpt-3.5-turbo')
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1000'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # 模型提供者配置 (openai, ollama)
    MODEL_PROVIDER = os.getenv('MODEL_PROVIDER', 'openai')


# 创建配置实例
config = Config()
