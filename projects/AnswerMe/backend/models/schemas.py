from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Message(BaseModel):
    role: str = Field(..., description="消息角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1, description="用户问题")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    history: List[Message] = Field(default_factory=list, description="对话历史")
    temperature: Optional[float] = Field(
        default=None, ge=0, le=2, description="LLM 温度参数"
    )
    top_k: Optional[int] = Field(default=None, ge=1, le=20, description="检索 top K")


class SourceDocument(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    content: str = Field(..., description="文档内容")
    score: float = Field(..., description="相似度分数")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class AnswerResponse(BaseModel):
    success: bool = Field(..., description="请求是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="响应数据")
    error: Optional[Dict[str, Any]] = Field(default=None, description="错误信息")


class ChatAnswerResponse(BaseModel):
    answer: str = Field(..., description="生成的答案")
    sources: List[SourceDocument] = Field(default=[], description="相关文档来源")
    response_time_ms: int = Field(..., description="响应时间 (毫秒)")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    question: str = Field(..., description="用户问题")


class ChatHistoryResponse(BaseModel):
    messages: List[Message] = Field(default_factory=list, description="对话消息")
    total: int = Field(..., description="消息总数")
    knowledge_base_id: str = Field(..., description="知识库 ID")


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., description="知识库名称", min_length=1, max_length=100)
    description: Optional[str] = Field(
        default="", description="知识库描述", max_length=500
    )


class KnowledgeBaseUpdate(BaseModel):
    name: Optional[str] = Field(
        default=None, description="知识库名称", min_length=1, max_length=100
    )
    description: Optional[str] = Field(
        default=None, description="知识库描述", max_length=500
    )


class KnowledgeBaseResponse(BaseModel):
    id: str = Field(..., description="知识库 ID")
    name: str = Field(..., description="知识库名称")
    description: str = Field(..., description="知识库描述")
    document_count: int = Field(..., description="文档数量")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class DocumentResponse(BaseModel):
    id: str = Field(..., description="文档 ID")
    filename: str = Field(..., description="文件名")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    status: str = Field(
        ..., description="处理状态: pending, processing, completed, failed"
    )
    page_count: Optional[int] = Field(default=None, description="页数")
    chunk_count: Optional[int] = Field(default=None, description="分块数量")
    file_size: Optional[int] = Field(default=None, description="文件大小(字节)")
    content_preview: Optional[str] = Field(default=None, description="内容预览")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse] = Field(..., description="文档列表")
    total: int = Field(..., description="总数")
    page: int = Field(..., description="当前页")
    page_size: int = Field(..., description="每页数量")


class UploadResponse(BaseModel):
    success: bool = Field(..., description="上传是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="上传数据")
    error: Optional[Dict[str, Any]] = Field(default=None, description="错误信息")


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    filename: str = Field(..., description="文件名")
    pages: int = Field(..., description="页数")
    chunk_count: int = Field(..., description="分块数量")
    status: str = Field(..., description="处理状态")


class DocumentDeleteResponse(BaseModel):
    success: bool = Field(..., description="删除是否成功")
    document_id: str = Field(..., description="文档 ID")


class ChunkInfo(BaseModel):
    chunk_id: str = Field(..., description="分块 ID")
    content: str = Field(..., description="分块内容")
    index: int = Field(..., description="分块索引")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="元数据")


class HealthResponse(BaseModel):
    status: str = Field(..., description="健康状态: healthy, degraded, unhealthy")
    version: str = Field(..., description="系统版本")
    timestamp: datetime = Field(..., description="检查时间")


class ErrorResponse(BaseModel):
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    details: Optional[str] = Field(default=None, description="详细信息")
