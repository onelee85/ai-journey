from routers import chat_router, knowledge_base_router, documents_router, health_router
from config import settings
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import os
import sys
import logging
from pathlib import Path

# 加载环境变量
from config import load_env

# 加载 .env 文件
load_env()


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AnswerMe QA System - 基于 RAG 的问答系统 API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)


@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"LLM API Type: {settings.LLM_API_TYPE}")
    logger.info(f"Embedding API Type: {settings.EMBEDDING_API_TYPE}")
    logger.info(f"Vector DB Type: {settings.VECTOR_DB_TYPE}")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down AnswerMe QA System")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "timestamp": "2024-01-01T00:00:00Z",
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": 500,
                "message": "Internal server error",
                "details": str(exc),
            },
        },
    )


app.include_router(chat_router)
app.include_router(knowledge_base_router)
app.include_router(documents_router)
app.include_router(health_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
