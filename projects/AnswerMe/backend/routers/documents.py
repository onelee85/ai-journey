from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("/")
async def list_documents(knowledge_base_id: Optional[str] = None):
    """获取文档列表"""
    pass


@router.get("/{doc_id}")
async def get_document(doc_id: str):
    """获取文档详情"""
    pass


@router.delete("/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档"""
    pass
