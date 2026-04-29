from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List
import logging
import json
import os

from config import settings
from models.schemas import (
    AnswerResponse,
    ChatHistoryResponse,
    Message,
    QuestionRequest,
)
from services.rag_service import get_rag_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])

UPLOAD_DIR = "./uploads"
HISTORY_FILE = os.path.join(UPLOAD_DIR, "chat_history.json")


def _load_history() -> Dict[str, List[Dict[str, str]]]:
    if not os.path.exists(HISTORY_FILE):
        return {}

    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError) as e:
        logger.warning(f"Failed to load chat history: {e}")
        return {}


def _save_history(history: Dict[str, List[Dict[str, str]]]) -> None:
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


@router.post("/query", response_model=AnswerResponse)
async def query(request: QuestionRequest):
    """提交问题"""
    try:
        rag_service = get_rag_service()

        kb_check = rag_service.get_knowledge_base(request.knowledge_base_id)
        if not kb_check.get("success"):
            raise HTTPException(status_code=404, detail="Knowledge base not found")

        stored_history = _load_history()
        request_history = [message.model_dump() for message in request.history]
        effective_history = request_history or stored_history.get(
            request.knowledge_base_id, []
        )

        result = rag_service.query(
            question=request.question,
            knowledge_base_id=request.knowledge_base_id,
            history=effective_history,
            top_k=request.top_k or settings.RETRIEVER_TOP_K,
            temperature=request.temperature
            if request.temperature is not None
            else settings.LLM_TEMPERATURE,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=result.get("error", {}).get("code", 500),
                detail=result.get("error", {}).get("message", "Failed to query"),
            )

        messages = stored_history.get(request.knowledge_base_id, [])
        messages.extend(
            [
                {"role": "user", "content": request.question},
                {"role": "assistant", "content": result["data"]["answer"]},
            ]
        )
        stored_history[request.knowledge_base_id] = messages[-100:]
        _save_history(stored_history)

        return AnswerResponse(success=True, data=result["data"], error=None)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=AnswerResponse)
async def get_history(
    knowledge_base_id: str = Query(..., description="知识库 ID"),
    limit: int = Query(default=20, ge=1, le=100, description="返回消息数量"),
):
    """获取对话历史"""
    history = _load_history()
    messages = history.get(knowledge_base_id, [])[-limit:]
    data = ChatHistoryResponse(
        messages=[Message(**message) for message in messages],
        total=len(history.get(knowledge_base_id, [])),
        knowledge_base_id=knowledge_base_id,
    )
    return AnswerResponse(success=True, data=data.model_dump(), error=None)


@router.delete("/history", response_model=AnswerResponse)
async def clear_history(knowledge_base_id: str = Query(..., description="知识库 ID")):
    """清空历史"""
    history = _load_history()
    history[knowledge_base_id] = []
    _save_history(history)
    return AnswerResponse(
        success=True,
        data={"knowledge_base_id": knowledge_base_id, "cleared": True},
        error=None,
    )
