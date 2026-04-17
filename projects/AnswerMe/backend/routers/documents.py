from fastapi import APIRouter, HTTPException, Query
from typing import Optional
import logging

from models.schemas import (
    DocumentListResponse,
    DocumentResponse,
    DocumentDeleteResponse,
)
from services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("/", response_model=DocumentListResponse)
async def list_all_documents(
    knowledge_base_id: Optional[str] = Query(
        default=None, description="知识库 ID，指定时只返回该知识库的文档"
    ),
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
):
    """获取文档列表（支持按知识库筛选）"""
    try:
        rag_service = get_rag_service()

        if knowledge_base_id:
            kb_check = rag_service.get_knowledge_base(knowledge_base_id)
            if not kb_check.get("success"):
                raise HTTPException(status_code=404, detail="Knowledge base not found")

            result = rag_service.get_documents(
                knowledge_base_id, page=page, page_size=page_size
            )
            if not result.get("success"):
                raise HTTPException(
                    status_code=result.get("error", {}).get("code", 500),
                    detail=result.get("error", {}).get(
                        "message", "Failed to get documents"
                    ),
                )
            data = result["data"]

            return DocumentListResponse(
                documents=[
                    DocumentResponse(
                        id=doc["id"],
                        filename=doc["filename"],
                        knowledge_base_id=doc["knowledge_base_id"],
                        status=doc["status"],
                        page_count=doc.get("page_count"),
                        chunk_count=doc.get("chunk_count"),
                        file_size=doc.get("file_size"),
                        content_preview=doc.get("content_preview"),
                        created_at=doc.get("created_at"),
                        updated_at=doc.get("updated_at"),
                    )
                    for doc in data["documents"]
                ],
                total=data["total"],
                page=data["page"],
                page_size=data["page_size"],
            )
        else:
            kbs = rag_service.get_knowledge_bases()
            all_docs = []
            for kb in kbs:
                kb_id = kb["id"]
                result = rag_service.get_documents(kb_id, page=1, page_size=1000)
                if result.get("success"):
                    all_docs.extend(result["data"]["documents"])

            all_docs.sort(key=lambda x: x.get("created_at", 0), reverse=True)

            total = len(all_docs)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_docs = all_docs[start:end]

            return DocumentListResponse(
                documents=[
                    DocumentResponse(
                        id=doc["id"],
                        filename=doc["filename"],
                        knowledge_base_id=doc["knowledge_base_id"],
                        status=doc["status"],
                        page_count=doc.get("page_count"),
                        chunk_count=doc.get("chunk_count"),
                        file_size=doc.get("file_size"),
                        content_preview=doc.get("content_preview"),
                        created_at=doc.get("created_at"),
                        updated_at=doc.get("updated_at"),
                    )
                    for doc in paginated_docs
                ],
                total=total,
                page=page,
                page_size=page_size,
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kb_id}/{doc_id}", response_model=DocumentResponse)
async def get_document(kb_id: str, doc_id: str):
    """获取文档详情"""
    try:
        rag_service = get_rag_service()
        result = rag_service.get_document(kb_id, doc_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 404),
                detail=result.get("error", {}).get("message", "Document not found"),
            )

        data = result["data"]
        return DocumentResponse(
            id=data["id"],
            filename=data["filename"],
            knowledge_base_id=data["knowledge_base_id"],
            status=data["status"],
            page_count=data.get("page_count"),
            chunk_count=data.get("chunk_count"),
            file_size=data.get("file_size"),
            content_preview=data.get("content_preview"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kb_id}/{doc_id}", response_model=DocumentDeleteResponse)
async def delete_document(kb_id: str, doc_id: str):
    """删除文档"""
    try:
        rag_service = get_rag_service()
        result = rag_service.delete_document(kb_id, doc_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 404),
                detail=result.get("error", {}).get("message", "Document not found"),
            )

        return DocumentDeleteResponse(success=True, document_id=doc_id)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
