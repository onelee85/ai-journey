from fastapi import APIRouter, HTTPException, UploadFile, File, Query, Body
from typing import List, Optional
import logging
import os
import uuid
from datetime import datetime

from models.schemas import (
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseResponse,
    DocumentListResponse,
    DocumentResponse,
    DocumentUploadResponse,
    UploadResponse,
    DocumentDeleteResponse,
)
from services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/knowledge-base", tags=["knowledge-base"])

UPLOAD_DIR = "./uploads"


@router.get("/", response_model=List[KnowledgeBaseResponse])
async def list_knowledge_bases():
    """获取知识库列表"""
    try:
        rag_service = get_rag_service()
        kbs = rag_service.get_knowledge_bases()

        return [
            KnowledgeBaseResponse(
                id=kb["id"],
                name=kb["name"],
                description=kb.get("description", ""),
                document_count=kb.get("document_count", 0),
                created_at=datetime.fromtimestamp(kb.get("created_at", 0)),
                updated_at=datetime.fromtimestamp(kb.get("updated_at", 0)),
            )
            for kb in kbs
        ]
    except Exception as e:
        logger.error(f"Error listing knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(kb_data: KnowledgeBaseCreate):
    """创建知识库"""
    try:
        rag_service = get_rag_service()
        result = rag_service.create_knowledge_base(
            name=kb_data.name, description=kb_data.description or ""
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 500),
                detail=result.get("error", {}).get(
                    "message", "Failed to create knowledge base"
                ),
            )

        data = result["data"]
        return KnowledgeBaseResponse(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            document_count=data.get("document_count", 0),
            created_at=datetime.fromtimestamp(data.get("created_at", 0)),
            updated_at=datetime.fromtimestamp(data.get("updated_at", 0)),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating knowledge base: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kb_id}", response_model=KnowledgeBaseResponse)
async def get_knowledge_base(kb_id: str):
    """获取知识库详情"""
    try:
        rag_service = get_rag_service()
        result = rag_service.get_knowledge_base(kb_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 404),
                detail=result.get("error", {}).get(
                    "message", "Knowledge base not found"
                ),
            )

        data = result["data"]
        return KnowledgeBaseResponse(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            document_count=data.get("document_count", 0),
            created_at=datetime.fromtimestamp(data.get("created_at", 0)),
            updated_at=datetime.fromtimestamp(data.get("updated_at", 0)),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{kb_id}", response_model=KnowledgeBaseResponse)
async def update_knowledge_base(kb_id: str, kb_data: KnowledgeBaseUpdate):
    """更新知识库"""
    try:
        rag_service = get_rag_service()
        result = rag_service.update_knowledge_base(
            kb_id=kb_id, name=kb_data.name, description=kb_data.description
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 500),
                detail=result.get("error", {}).get(
                    "message", "Failed to update knowledge base"
                ),
            )

        data = result["data"]
        kb_detail = rag_service.get_knowledge_base(kb_id)
        if kb_detail.get("success"):
            kb_info = kb_detail["data"]
            return KnowledgeBaseResponse(
                id=kb_id,
                name=data.get("name", kb_info.get("name", "")),
                description=data.get("description", kb_info.get("description", "")),
                document_count=kb_info.get("document_count", 0),
                created_at=datetime.fromtimestamp(kb_info.get("created_at", 0)),
                updated_at=datetime.fromtimestamp(data.get("updated_at", 0)),
            )
        else:
            raise HTTPException(status_code=404, detail="Knowledge base not found")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kb_id}")
async def delete_knowledge_base(kb_id: str):
    """删除知识库"""
    try:
        rag_service = get_rag_service()
        result = rag_service.delete_knowledge_base(kb_id)

        if not result.get("success"):
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 500),
                detail=result.get("error", {}).get(
                    "message", "Failed to delete knowledge base"
                ),
            )

        return {
            "success": True,
            "message": f"Knowledge base {kb_id} deleted successfully",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge base {kb_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{kb_id}/upload", response_model=DocumentUploadResponse)
async def upload_document(kb_id: str, file: UploadFile = File(...)):
    """上传文档到知识库"""
    try:
        os.makedirs(UPLOAD_DIR, exist_ok=True)

        file_ext = os.path.splitext(file.filename)[1].lower()
        allowed_exts = {".txt", ".pdf", ".docx", ".md"}

        if file_ext not in allowed_exts:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file_ext}. Supported types: {', '.join(allowed_exts)}",
            )

        file_id = str(uuid.uuid4())
        file_path = os.path.join(UPLOAD_DIR, f"{kb_id}_{file_id}{file_ext}")

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        rag_service = get_rag_service()

        kb_check = rag_service.get_knowledge_base(kb_id)
        if not kb_check.get("success"):
            os.remove(file_path)
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        result = rag_service.upload_document(kb_id, file_path)

        if not result.get("success"):
            if os.path.exists(file_path):
                os.remove(file_path)
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 500),
                detail=result.get("error", {}).get(
                    "message", "Failed to upload document"
                ),
            )

        data = result["data"]
        return DocumentUploadResponse(
            document_id=data["document_id"],
            filename=data["filename"],
            pages=data.get("pages", 1),
            chunk_count=data.get("chunk_count", 0),
            status=data.get("status", "completed"),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kb_id}/documents", response_model=DocumentListResponse)
async def list_documents(
    kb_id: str,
    page: int = Query(default=1, ge=1, description="页码"),
    page_size: int = Query(default=20, ge=1, le=100, description="每页数量"),
):
    """获取知识库中的文档列表"""
    try:
        rag_service = get_rag_service()

        kb_check = rag_service.get_knowledge_base(kb_id)
        if not kb_check.get("success"):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        result = rag_service.get_documents(kb_id, page=page, page_size=page_size)

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
                    created_at=datetime.fromtimestamp(doc.get("created_at", 0)),
                    updated_at=datetime.fromtimestamp(doc.get("updated_at", 0)),
                )
                for doc in data["documents"]
            ],
            total=data["total"],
            page=data["page"],
            page_size=data["page_size"],
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{kb_id}/documents/{doc_id}", response_model=DocumentResponse)
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
            created_at=datetime.fromtimestamp(data.get("created_at", 0)),
            updated_at=datetime.fromtimestamp(data.get("updated_at", 0)),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{kb_id}/documents/{doc_id}", response_model=DocumentDeleteResponse)
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
