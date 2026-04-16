from typing import List, Optional
import logging
import time

logger = logging.getLogger(__name__)


class LLMService:
    """LLM 服务基类"""

    def __init__(self, api_type: str = "openai", **kwargs):
        self.api_type = api_type
        self.kwargs = kwargs
        self._model = None

    def generate(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048
    ) -> str:
        """生成文本"""
        raise NotImplementedError

    def generate_stream(
        self, prompt: str, temperature: float = 0.7, max_tokens: int = 2048
    ):
        """流式生成文本"""
        raise NotImplementedError


class OpenAILLMService(LLMService):
    """OpenAI LLM 服务实现"""

    def __init__(
        self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", **kwargs
    ):
        super().__init__(api_type="openai", model=model, **kwargs)
        self.api_key = api_key
        self.model = model
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 2048)

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """生成文本"""
        try:
            import openai

            if self.api_key:
                openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )

            return response["choices"][0]["message"]["content"]

        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        except Exception as e:
            logger.error(f"Error generating text: {e}")
            raise

    def generate_stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """流式生成文本"""
        try:
            import openai

            if self.api_key:
                openai.api_key = self.api_key

            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
                stream=True,
            )

            for chunk in response:
                if chunk["choices"][0]["delta"].get("content"):
                    yield chunk["choices"][0]["delta"]["content"]

        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        except Exception as e:
            logger.error(f"Error streaming text: {e}")
            raise


class LocalLLMService(LLMService):
    """本地 LLM 服务实现 (使用 transformers)"""

    def __init__(self, model_name: str = "gpt2", **kwargs):
        super().__init__(api_type="local", model_name=model_name, **kwargs)
        self.model_name = model_name
        self._model = None
        self._tokenizer = None
        self.temperature = kwargs.get("temperature", 0.7)
        self.max_tokens = kwargs.get("max_tokens", 2048)

    def _load_model(self):
        """加载模型"""
        if self._model is None:
            try:
                from transformers import AutoTokenizer, AutoModelForCausalLM
                import torch

                self._tokenizer = AutoTokenizer.from_pretrained(self.model_name)
                self._model = AutoModelForCausalLM.from_pretrained(self.model_name)
                self._device = "cuda" if torch.cuda.is_available() else "cpu"
                self._model.to(self._device)

                logger.info(
                    f"Loaded local LLM model: {self.model_name} on {self._device}"
                )
            except ImportError:
                raise ImportError(
                    "Please install transformers: pip install transformers"
                )

    def generate(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """生成文本"""
        self._load_model()

        import torch

        inputs = self._tokenizer(prompt, return_tensors="pt").to(self._device)

        with torch.no_grad():
            outputs = self._model.generate(
                **inputs,
                max_new_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                do_sample=True,
                pad_token_id=self._tokenizer.eos_token_id,
            )

        return self._tokenizer.decode(outputs[0], skip_special_tokens=True)

    def generate_stream(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """流式生成文本"""
        self._load_model()
        raise NotImplementedError("Stream generation not implemented for local models")


def get_llm_service(api_type: str = None, **kwargs) -> LLMService:
    """获取 LLM 服务实例"""
    if api_type is None:
        from config import settings

        api_type = settings.LLM_API_TYPE

    if api_type == "openai":
        api_key = kwargs.get("api_key", kwargs.get("LLM_API_KEY"))
        model = kwargs.get("model", kwargs.get("LLM_MODEL_NAME", "gpt-3.5-turbo"))
        return OpenAILLMService(api_key=api_key, model=model)
    elif api_type == "local":
        model_name = kwargs.get("model_name", kwargs.get("LLM_MODEL_NAME", "gpt2"))
        return LocalLLMService(model_name=model_name)
    else:
        raise ValueError(f"Unknown LLM API type: {api_type}")
