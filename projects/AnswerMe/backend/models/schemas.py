from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Message(BaseModel):
    role: str = Field(..., description="消息角色: user 或 assistant")
    content: str = Field(..., description="消息内容")


class QuestionRequest(BaseModel):
    question: str = Field(..., description="用户问题")
    knowledge_base_id: str = Field(..., description="知识库 ID")
    history: List[Message] = Field(default=[], description="对话历史")
    temperature: Optional[float] = Field(default=None, description="LLM 温度参数")
    top_k: Optional[int] = Field(default=None, description="检索 top K")


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


class KnowledgeBaseCreate(BaseModel):
    name: str = Field(..., description="知识库名称")
    description: Optional[str] = Field(default="", description="知识库描述")


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
    status: str = Field(..., description="处理状态: pending, processing, completed, failed")
    page_count: Optional[int] = Field(default=None, description="页数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UploadResponse(BaseModel):
    success: bool = Field(..., description="上传是否成功")
    data: Optional[Dict[str, Any]] = Field(default=None, description="上传数据")
    error: Optional[Dict[str, Any]] = Field(default=None, description="错误信息")


class DocumentUploadResponse(BaseModel):
    document_id: str = Field(..., description="文档 ID")
    filename: str = Field(..., description="文件名")
    pages: int = Field(..., description="页数")
    status: str = Field(..., description="处理状态")


class HealthResponse(BaseModel):
    status: str = Field(..., description="健康状态: healthy, degraded, unhealthy")
    version: str = Field(..., description="系统版本")
    timestamp: datetime = Field(..., description="检查时间")


class ErrorResponse(BaseModel):
    code: int = Field(..., description="错误码")
    message: str = Field(..., description="错误消息")
    details: Optional[str] = Field(default=None, description="详细信息")
