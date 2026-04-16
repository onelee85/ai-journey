from .chat import router as chat_router
from .knowledge_base import router as knowledge_base_router
from .documents import router as documents_router
from .health import router as health_router

__all__ = ["chat_router", "knowledge_base_router", "documents_router", "health_router"]
