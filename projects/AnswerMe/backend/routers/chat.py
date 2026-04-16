from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


@router.post("/query")
async def query(question: str, knowledge_base_id: str, history: Optional[str] = None):
    """提交问题"""
    pass


@router.get("/history")
async def get_history(knowledge_base_id: str, limit: int = 10):
    """获取对话历史"""
    pass


@router.delete("/history")
async def clear_history(knowledge_base_id: str):
    """清空历史"""
    pass
