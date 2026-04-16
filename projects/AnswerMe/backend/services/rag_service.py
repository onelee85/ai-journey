from typing import List, Dict, Any, Optional
import logging
import time
import os

logger = logging.getLogger(__name__)


class RAGService:
    """RAG (Retrieval-Augmented Generation) 服务"""

    def __init__(self, vector_db=None, embedding_service=None, llm_service=None):
        self.vector_db = vector_db
        self.embedding_service = embedding_service
        self.llm_service = llm_service

    def query(
        self,
        question: str,
        knowledge_base_id: str,
        history: List[Dict] = None,
        top_k: int = 5,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """处理用户查询"""
        raise NotImplementedError

    def upload_document(self, knowledge_base_id: str, file_path: str) -> Dict[str, Any]:
        """上传文档到知识库"""
        raise NotImplementedError

    def create_knowledge_base(self, name: str, description: str = "") -> Dict[str, Any]:
        """创建知识库"""
        raise NotImplementedError

    def get_knowledge_bases(self) -> List[Dict[str, Any]]:
        """获取知识库列表"""
        raise NotImplementedError


class SimpleRAGService(RAGService):
    """简单的 RAG 服务实现"""

    def __init__(self, vector_db=None, embedding_service=None, llm_service=None):
        super().__init__(vector_db, embedding_service, llm_service)

        if self.vector_db is None:
            from vector_db import get_vector_database

            self.vector_db = get_vector_database()

        if self.embedding_service is None:
            from services.embedding_service import get_embedding_service

            self.embedding_service = get_embedding_service()

        if self.llm_service is None:
            from services.llm_service import get_llm_service

            self.llm_service = get_llm_service()

        self.vector_db.connect()

    def _build_prompt(
        self, question: str, context: List[str], history: List[Dict] = None
    ) -> str:
        """构建提示词"""
        prompt = "你是一个智能问答助手。请根据以下上下文回答用户的问题。\n\n"

        if history:
            prompt += "对话历史:\n"
            for msg in history:
                role = "用户" if msg.get("role") == "user" else "助手"
                prompt += f"{role}: {msg.get('content', '')}\n"
            prompt += "\n"

        prompt += "相关上下文:\n"
        for i, ctx in enumerate(context, 1):
            prompt += f"[来源 {i}]\n{ctx}\n\n"

        prompt += f"问题: {question}\n\n"
        prompt += "请基于以上上下文回答问题，如果上下文无法回答，请说明无法回答。"

        return prompt

    def _format_sources(self, search_results: List[Dict]) -> List[Dict[str, Any]]:
        """格式化来源"""
        sources = []
        for result in search_results:
            sources.append(
                {
                    "document": result.get("document", ""),
                    "metadata": result.get("metadata", {}),
                    "score": result.get("score", 0),
                    "distance": result.get("distance", 0),
                }
            )
        return sources

    def query(
        self,
        question: str,
        knowledge_base_id: str,
        history: List[Dict] = None,
        top_k: int = 5,
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """处理用户查询"""
        start_time = time.time()

        try:
            logger.info(f"Processing query: {question[:50]}...")

            query_embedding = self.embedding_service.encode(question)

            search_results = self.vector_db.search(
                collection_name=knowledge_base_id,
                query_embedding=query_embedding,
                k=top_k,
            )

            context = [result["document"] for result in search_results]

            prompt = self._build_prompt(question, context, history)

            answer = self.llm_service.generate(prompt, temperature=temperature)

            response_time = int((time.time() - start_time) * 1000)

            return {
                "success": True,
                "data": {
                    "answer": answer,
                    "sources": self._format_sources(search_results),
                    "response_time_ms": response_time,
                    "knowledge_base_id": knowledge_base_id,
                    "question": question,
                },
            }

        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error processing query",
                    "details": str(e),
                },
            }

    def upload_document(self, knowledge_base_id: str, file_path: str) -> Dict[str, Any]:
        """上传文档到知识库"""
        try:
            logger.info(f"Uploading document: {file_path}")

            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            filename = os.path.basename(file_path)

            embedding = self.embedding_service.encode(content)

            metadata = {
                "filename": filename,
                "file_path": file_path,
                "knowledge_base_id": knowledge_base_id,
            }

            doc_id = self.vector_db.add_documents(
                collection_name=knowledge_base_id,
                documents=[content],
                embeddings=[embedding],
                metadatas=[metadata],
            )

            return {
                "success": True,
                "data": {
                    "document_id": doc_id[0],
                    "filename": filename,
                    "pages": 1,
                    "status": "completed",
                },
            }

        except Exception as e:
            logger.error(f"Error uploading document: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error uploading document",
                    "details": str(e),
                },
            }

    def create_knowledge_base(self, name: str, description: str = "") -> Dict[str, Any]:
        """创建知识库"""
        try:
            dimension = self.embedding_service.get_dimension()
            collection_id = self.vector_db.create_collection(
                name=name, dimension=dimension
            )

            return {
                "success": True,
                "data": {
                    "id": collection_id,
                    "name": name,
                    "description": description,
                    "document_count": 0,
                    "created_at": time.time(),
                    "updated_at": time.time(),
                },
            }

        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error creating knowledge base",
                    "details": str(e),
                },
            }

    def get_knowledge_bases(self) -> List[Dict[str, Any]]:
        """获取知识库列表"""
        try:
            collections = self.vector_db.list_collections()

            return [
                {
                    "id": coll["id"],
                    "name": coll["name"],
                    "description": "",
                    "document_count": coll["count"],
                    "created_at": time.time(),
                    "updated_at": time.time(),
                }
                for coll in collections
            ]

        except Exception as e:
            logger.error(f"Error getting knowledge bases: {e}")
            return []


def get_rag_service() -> RAGService:
    """获取 RAG 服务实例"""
    return SimpleRAGService()
