import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "AnswerMe QA System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # LLM 配置
    LLM_API_TYPE: str = Field(
        default="openai", description="LLM API 类型: openai, anthropic, local"
    )
    LLM_API_KEY: Optional[str] = Field(default=None, description="LLM API Key")
    LLM_API_BASE: Optional[str] = Field(
        default=None, description="LLM API Base URL (for local models)"
    )
    LLM_MODEL_NAME: str = Field(default="gpt-3.5-turbo", description="LLM 模型名称")
    LLM_TEMPERATURE: float = Field(default=0.7, description="LLM 温度参数")
    LLM_MAX_TOKENS: int = Field(default=2048, description="LLM 最大 token 数")

    # Embedding 配置
    EMBEDDING_API_TYPE: str = Field(
        default="openai", description="Embedding API 类型: openai, local"
    )
    EMBEDDING_API_KEY: Optional[str] = Field(
        default=None, description="Embedding API Key"
    )
    EMBEDDING_API_BASE: Optional[str] = Field(
        default=None, description="Embedding API Base URL"
    )
    EMBEDDING_MODEL_NAME: str = Field(
        default="text-embedding-ada-002", description="Embedding 模型名称"
    )
    EMBEDDING_DIMENSION: int = Field(default=1536, description="Embedding 向量维度")

    # 向量数据库配置
    VECTOR_DB_TYPE: str = Field(
        default="chroma", description="向量数据库类型: chroma, milvus, pinecone"
    )
    VECTOR_DB_PATH: str = Field(default="./vector_db", description="Chroma 数据库路径")
    VECTOR_DB_HOST: Optional[str] = Field(
        default=None, description="Milvus/Pinecone 主机地址"
    )
    VECTOR_DB_PORT: Optional[int] = Field(
        default=None, description="Milvus/Pinecone 端口"
    )
    VECTOR_DB_USER: Optional[str] = Field(default=None, description="Milvus 用户名")
    VECTOR_DB_PASSWORD: Optional[str] = Field(default=None, description="Milvus 密码")

    # 检索配置
    RETRIEVER_TOP_K: int = Field(default=5, description="检索 top K 个相关文档")
    RETRIEVER_SCORE_THRESHOLD: float = Field(default=0.5, description="检索分数阈值")

    # CORS 配置
    CORS_ORIGINS: list = Field(default=["*"], description="允许的 CORS 原源")
    CORS_METHODS: list = Field(default=["*"], description="允许的 CORS 方法")
    CORS_HEADERS: list = Field(default=["*"], description="允许的 CORS 请求头")

    # 文档处理配置
    DOCUMENT_MAX_SIZE: int = Field(
        default=10 * 1024 * 1024, description="最大文档大小 (字节)"
    )
    DOCUMENT_SUPPORTED_FORMATS: list = Field(
        default=[".pdf", ".docx", ".txt", ".md"], description="支持的文档格式"
    )

    # 缓存配置
    CACHE_ENABLED: bool = Field(default=True, description="是否启用缓存")
    CACHE_TTL: int = Field(default=3600, description="缓存过期时间 (秒)")

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
