import openai
from typing import Optional, Generator, Dict, Any
import time

# Try to import config from the same directory
try:
    from .config import config
except ImportError:
    # If running directly, add the src directory to the path
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config import config


class OpenAIClient:
    """OpenAI API客户端"""

    def __init__(self):
        """初始化客户端"""
        openai.api_key = config.OPENAI_API_KEY
        if config.OPENAI_BASE_URL:
            openai.base_url = config.OPENAI_BASE_URL

    def generate_content(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None
    ) -> Optional[str]:
        """生成内容

        Args:
            prompt: 提示词
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数

        Returns:
            生成的内容
        """
        model = model or config.DEFAULT_MODEL
        max_tokens = max_tokens or config.MAX_TOKENS
        temperature = temperature or config.TEMPERATURE
        for attempt in range(config.API_RETRY_COUNT):
            try:
                response = openai.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=config.API_TIMEOUT
                )
                # print(response)
                # 检查response的类型
                if hasattr(response, 'choices'):
                    return response.choices[0].message.content
                else:
                    # 如果response是字符串，直接返回
                    return response
            except openai.APIError as e:
                if attempt == config.API_RETRY_COUNT - 1:
                    raise
                time.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                print(f"Error in generate_content: {e}")
                raise

    def stream_content(
        self,
        prompt: str,
        model: str = None,
        max_tokens: int = None,
        temperature: float = None
    ) -> Generator[str, None, None]:
        """流式生成内容

        Args:
            prompt: 提示词
            model: 模型名称
            max_tokens: 最大token数
            temperature: 温度参数

        Yields:
            生成的内容片段
        """
        model = model or config.DEFAULT_MODEL
        max_tokens = max_tokens or config.MAX_TOKENS
        temperature = temperature or config.TEMPERATURE

        try:
            stream = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                stream=True,
                timeout=config.API_TIMEOUT
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise


# 创建客户端实例
openai_client = OpenAIClient()

if __name__ == "__main__":
    print(openai_client.generate_content("你好"))
