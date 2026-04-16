from typing import List, Optional
import logging
import time

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Embedding 服务基类"""

    def __init__(self, api_type: str = "openai", **kwargs):
        self.api_type = api_type
        self.kwargs = kwargs
        self._model = None

    def encode(self, text: str) -> List[float]:
        """编码单个文本"""
        raise NotImplementedError

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码文本"""
        raise NotImplementedError

    def get_dimension(self) -> int:
        """获取向量维度"""
        raise NotImplementedError


class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI Embedding 服务实现"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "text-embedding-ada-002",
        **kwargs,
    ):
        super().__init__(api_type="openai", model=model, **kwargs)
        self.api_key = api_key
        self.model = model
        self._dimension = 1536

    def encode(self, text: str) -> List[float]:
        """编码单个文本"""
        try:
            import openai

            if self.api_key:
                openai.api_key = self.api_key

            response = openai.Embedding.create(model=self.model, input=text)

            return response["data"][0]["embedding"]

        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        except Exception as e:
            logger.error(f"Error encoding text: {e}")
            raise

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码文本"""
        try:
            import openai

            if self.api_key:
                openai.api_key = self.api_key

            response = openai.Embedding.create(model=self.model, input=texts)

            return [item["embedding"] for item in response["data"]]

        except ImportError:
            raise ImportError("Please install openai: pip install openai")
        except Exception as e:
            logger.error(f"Error encoding batch texts: {e}")
            raise

    def get_dimension(self) -> int:
        """获取向量维度"""
        return self._dimension


class LocalEmbeddingService(EmbeddingService):
    """本地 Embedding 服务实现 (使用 sentence-transformers)"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", **kwargs):
        super().__init__(api_type="local", model_name=model_name, **kwargs)
        self.model_name = model_name
        self._model = None
        self._dimension = 384

    def _load_model(self):
        """加载模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                logger.info(f"Loaded local embedding model: {self.model_name}")
            except ImportError:
                raise ImportError(
                    "Please install sentence-transformers: pip install sentence-transformers"
                )

    def encode(self, text: str) -> List[float]:
        """编码单个文本"""
        self._load_model()
        embedding = self._model.encode(text)
        return embedding.tolist()

    def encode_batch(self, texts: List[str]) -> List[List[float]]:
        """批量编码文本"""
        self._load_model()
        embeddings = self._model.encode(texts)
        return [emb.tolist() for emb in embeddings]

    def get_dimension(self) -> int:
        """获取向量维度"""
        return self._dimension


def get_embedding_service(api_type: str = None, **kwargs) -> EmbeddingService:
    """获取 Embedding 服务实例"""
    if api_type is None:
        from config import settings

        api_type = settings.EMBEDDING_API_TYPE

    if api_type == "openai":
        api_key = kwargs.get("api_key", kwargs.get("EMBEDDING_API_KEY"))
        model = kwargs.get(
            "model", kwargs.get("EMBEDDING_MODEL_NAME", "text-embedding-ada-002")
        )
        return OpenAIEmbeddingService(api_key=api_key, model=model)
    elif api_type == "local":
        model_name = kwargs.get(
            "model_name", kwargs.get("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
        )
        return LocalEmbeddingService(model_name=model_name)
    else:
        raise ValueError(f"Unknown embedding API type: {api_type}")
