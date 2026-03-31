from typing import Optional, Generator, Dict, Any
import requests
import json
import time
from .config import config


class ModelProvider:
    """模型提供者抽象基类"""
    
    def generate_content(self, prompt: str, max_tokens: int = None, temperature: float = None) -> Optional[str]:
        """生成内容"""
        raise NotImplementedError
    
    def stream_content(self, prompt: str, max_tokens: int = None, temperature: float = None) -> Generator[str, None, None]:
        """流式生成内容"""
        raise NotImplementedError


class OpenAIProvider(ModelProvider):
    """OpenAI模型提供者"""
    
    def __init__(self):
        """初始化OpenAI提供者"""
        import openai
        self.openai = openai
        self.openai.api_key = config.OPENAI_API_KEY
        if config.OPENAI_BASE_URL:
            self.openai.base_url = config.OPENAI_BASE_URL
    
    def generate_content(self, prompt: str, max_tokens: int = None, temperature: float = None) -> Optional[str]:
        """生成内容"""
        model = config.DEFAULT_MODEL
        max_tokens = max_tokens or config.MAX_TOKENS
        temperature = temperature or config.TEMPERATURE
        
        for attempt in range(config.API_RETRY_COUNT):
            try:
                response = self.openai.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=temperature,
                    timeout=config.API_TIMEOUT
                )
                
                if hasattr(response, 'choices'):
                    return response.choices[0].message.content
                else:
                    return response
            except Exception as e:
                if attempt == config.API_RETRY_COUNT - 1:
                    raise
                time.sleep(2 ** attempt)
    
    def stream_content(self, prompt: str, max_tokens: int = None, temperature: float = None) -> Generator[str, None, None]:
        """流式生成内容"""
        model = config.DEFAULT_MODEL
        max_tokens = max_tokens or config.MAX_TOKENS
        temperature = temperature or config.TEMPERATURE
        
        try:
            stream = self.openai.chat.completions.create(
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


class OllamaProvider(ModelProvider):
    """Ollama模型提供者"""
    
    def __init__(self):
        """初始化Ollama提供者"""
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL
    
    def generate_content(self, prompt: str, max_tokens: int = None, temperature: float = None) -> Optional[str]:
        """生成内容"""
        max_tokens = max_tokens or config.MAX_TOKENS
        temperature = temperature or config.TEMPERATURE
        
        for attempt in range(config.API_RETRY_COUNT):
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "max_tokens": max_tokens,
                        "temperature": temperature
                    },
                    timeout=config.API_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "")
                else:
                    raise Exception(f"Ollama API error: {response.status_code}")
            except Exception as e:
                if attempt == config.API_RETRY_COUNT - 1:
                    raise
                time.sleep(2 ** attempt)
    
    def stream_content(self, prompt: str, max_tokens: int = None, temperature: float = None) -> Generator[str, None, None]:
        """流式生成内容"""
        max_tokens = max_tokens or config.MAX_TOKENS
        temperature = temperature or config.TEMPERATURE
        
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": True
                },
                stream=True,
                timeout=config.API_TIMEOUT
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line.decode('utf-8'))
                        if "response" in data:
                            yield data["response"]
                        if data.get("done", False):
                            break
            else:
                raise Exception(f"Ollama API error: {response.status_code}")
        except Exception as e:
            raise


class ModelProviderFactory:
    """模型提供者工厂"""
    
    @staticmethod
    def get_provider(provider_name: str = None) -> ModelProvider:
        """获取模型提供者实例"""
        provider_name = provider_name or config.MODEL_PROVIDER
        
        if provider_name == "openai":
            return OpenAIProvider()
        elif provider_name == "ollama":
            return OllamaProvider()
        else:
            raise ValueError(f"Unknown model provider: {provider_name}")


# 创建默认模型提供者实例
model_provider = ModelProviderFactory.get_provider()