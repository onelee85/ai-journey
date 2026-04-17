from typing import List, Dict, Any, Optional
import logging
import time
import os
from uuid import uuid4

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

    def get_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """获取知识库详情"""
        raise NotImplementedError

    def update_knowledge_base(
        self, kb_id: str, name: str = None, description: str = None
    ) -> Dict[str, Any]:
        """更新知识库"""
        raise NotImplementedError

    def delete_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """删除知识库"""
        raise NotImplementedError

    def get_documents(
        self, kb_id: str, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """获取知识库中的文档列表"""
        raise NotImplementedError

    def get_document(self, kb_id: str, doc_id: str) -> Dict[str, Any]:
        """获取文档详情"""
        raise NotImplementedError

    def delete_document(self, kb_id: str, doc_id: str) -> Dict[str, Any]:
        """删除文档"""
        raise NotImplementedError


class SimpleRAGService(RAGService):
    """简单的 RAG 服务实现"""

    def __init__(
        self,
        vector_db=None,
        embedding_service=None,
        llm_service=None,
        upload_dir: str = "./uploads",
    ):
        super().__init__(vector_db, embedding_service, llm_service)

        self.upload_dir = upload_dir

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

        os.makedirs(self.upload_dir, exist_ok=True)

        self._doc_metadata: Dict[str, Dict[str, Any]] = {}

    def _load_doc_metadata(self, kb_id: str) -> None:
        """加载知识库的文档元数据"""
        metadata_file = os.path.join(self.upload_dir, f"{kb_id}_metadata.json")
        if os.path.exists(metadata_file):
            import json

            try:
                with open(metadata_file, "r", encoding="utf-8") as f:
                    self._doc_metadata = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._doc_metadata = {}
        else:
            self._doc_metadata = {}

    def _save_doc_metadata(self, kb_id: str) -> None:
        """保存文档元数据"""
        import json

        metadata_file = os.path.join(self.upload_dir, f"{kb_id}_metadata.json")
        with open(metadata_file, "w", encoding="utf-8") as f:
            json.dump(self._doc_metadata, f, ensure_ascii=False, indent=2)

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

            from services.document_service import get_document_processor

            processor = get_document_processor()

            result = processor.process_file(file_path)
            chunks = result["chunks"]
            content = result["content"]
            filename = result["filename"]

            if not chunks:
                return {
                    "success": False,
                    "error": {
                        "code": 400,
                        "message": "No content extracted from document",
                        "details": "The document appears to be empty",
                    },
                }

            embeddings = [
                self.embedding_service.encode(chunk["content"]) for chunk in chunks
            ]

            metadatas = [
                {
                    "filename": filename,
                    "file_path": file_path,
                    "knowledge_base_id": knowledge_base_id,
                    "page": chunk.get("page", 1),
                    "chunk_index": chunk.get("index", 0),
                }
                for chunk in chunks
            ]

            doc_ids = self.vector_db.add_documents(
                collection_name=knowledge_base_id,
                documents=[chunk["content"] for chunk in chunks],
                embeddings=embeddings,
                metadatas=metadatas,
            )

            self._load_doc_metadata(knowledge_base_id)

            parent_doc_id = str(uuid4())
            self._doc_metadata[parent_doc_id] = {
                "filename": filename,
                "file_path": file_path,
                "knowledge_base_id": knowledge_base_id,
                "status": "completed",
                "page_count": result.get("page_count", 1),
                "chunk_count": len(chunks),
                "file_size": result.get("file_size", 0),
                "content_preview": content[:500],
                "created_at": time.time(),
                "updated_at": time.time(),
                "chunk_ids": doc_ids,
            }
            self._save_doc_metadata(knowledge_base_id)

            return {
                "success": True,
                "data": {
                    "document_id": parent_doc_id,
                    "filename": filename,
                    "pages": result.get("page_count", 1),
                    "chunk_count": len(chunks),
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

            result = []
            for coll in collections:
                self._load_doc_metadata(coll["id"])
                kb_metadata = self._doc_metadata.get("_kb_info", {})
                result.append(
                    {
                        "id": coll["id"],
                        "name": kb_metadata.get("name", coll["name"]),
                        "description": kb_metadata.get("description", ""),
                        "document_count": len(
                            [k for k in self._doc_metadata.keys() if k != "_kb_info"]
                        ),
                        "created_at": kb_metadata.get("created_at", time.time()),
                        "updated_at": kb_metadata.get("updated_at", time.time()),
                    }
                )

            return result

        except Exception as e:
            logger.error(f"Error getting knowledge bases: {e}")
            return []

    def get_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """获取知识库详情"""
        try:
            collection = self.vector_db.get_collection(kb_id)

            self._load_doc_metadata(kb_id)
            kb_metadata = self._doc_metadata.get("_kb_info", {})

            return {
                "success": True,
                "data": {
                    "id": kb_id,
                    "name": kb_metadata.get("name", collection.name),
                    "description": kb_metadata.get("description", ""),
                    "document_count": len(
                        [k for k in self._doc_metadata.keys() if k != "_kb_info"]
                    ),
                    "created_at": kb_metadata.get("created_at", time.time()),
                    "updated_at": kb_metadata.get("updated_at", time.time()),
                },
            }
        except Exception as e:
            logger.error(f"Error getting knowledge base {kb_id}: {e}")
            return {
                "success": False,
                "error": {
                    "code": 404,
                    "message": "Knowledge base not found",
                    "details": str(e),
                },
            }

    def update_knowledge_base(
        self, kb_id: str, name: str = None, description: str = None
    ) -> Dict[str, Any]:
        """更新知识库"""
        try:
            self._load_doc_metadata(kb_id)

            if "_kb_info" not in self._doc_metadata:
                self._doc_metadata["_kb_info"] = {}

            if name is not None:
                self._doc_metadata["_kb_info"]["name"] = name
            if description is not None:
                self._doc_metadata["_kb_info"]["description"] = description

            self._doc_metadata["_kb_info"]["updated_at"] = time.time()
            self._save_doc_metadata(kb_id)

            return {
                "success": True,
                "data": {
                    "id": kb_id,
                    "name": self._doc_metadata["_kb_info"].get("name", ""),
                    "description": self._doc_metadata["_kb_info"].get(
                        "description", ""
                    ),
                    "updated_at": self._doc_metadata["_kb_info"]["updated_at"],
                },
            }
        except Exception as e:
            logger.error(f"Error updating knowledge base {kb_id}: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error updating knowledge base",
                    "details": str(e),
                },
            }

    def delete_knowledge_base(self, kb_id: str) -> Dict[str, Any]:
        """删除知识库"""
        try:
            success = self.vector_db.delete_collection(kb_id)

            if success:
                metadata_file = os.path.join(self.upload_dir, f"{kb_id}_metadata.json")
                if os.path.exists(metadata_file):
                    os.remove(metadata_file)

            return {"success": success, "data": {"kb_id": kb_id} if success else None}
        except Exception as e:
            logger.error(f"Error deleting knowledge base {kb_id}: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error deleting knowledge base",
                    "details": str(e),
                },
            }

    def get_documents(
        self, kb_id: str, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """获取知识库中的文档列表"""
        try:
            self._load_doc_metadata(kb_id)

            docs = [
                {
                    "id": doc_id,
                    "filename": doc_info.get("filename", ""),
                    "knowledge_base_id": kb_id,
                    "status": doc_info.get("status", "completed"),
                    "page_count": doc_info.get("page_count", 1),
                    "chunk_count": doc_info.get("chunk_count", 0),
                    "file_size": doc_info.get("file_size", 0),
                    "content_preview": doc_info.get("content_preview", "")[:200],
                    "created_at": doc_info.get("created_at", time.time()),
                    "updated_at": doc_info.get("updated_at", time.time()),
                }
                for doc_id, doc_info in self._doc_metadata.items()
                if doc_id != "_kb_info"
            ]

            docs.sort(key=lambda x: x["created_at"], reverse=True)

            total = len(docs)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_docs = docs[start:end]

            return {
                "success": True,
                "data": {
                    "documents": paginated_docs,
                    "total": total,
                    "page": page,
                    "page_size": page_size,
                },
            }
        except Exception as e:
            logger.error(f"Error getting documents for kb {kb_id}: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error getting documents",
                    "details": str(e),
                },
            }

    def get_document(self, kb_id: str, doc_id: str) -> Dict[str, Any]:
        """获取文档详情"""
        try:
            self._load_doc_metadata(kb_id)

            if doc_id not in self._doc_metadata:
                return {
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": "Document not found",
                        "details": f"Document {doc_id} not found in knowledge base {kb_id}",
                    },
                }

            doc_info = self._doc_metadata[doc_id]
            return {
                "success": True,
                "data": {
                    "id": doc_id,
                    "filename": doc_info.get("filename", ""),
                    "knowledge_base_id": kb_id,
                    "status": doc_info.get("status", "completed"),
                    "page_count": doc_info.get("page_count", 1),
                    "chunk_count": doc_info.get("chunk_count", 0),
                    "file_size": doc_info.get("file_size", 0),
                    "content_preview": doc_info.get("content_preview", ""),
                    "created_at": doc_info.get("created_at", time.time()),
                    "updated_at": doc_info.get("updated_at", time.time()),
                },
            }
        except Exception as e:
            logger.error(f"Error getting document {doc_id}: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error getting document",
                    "details": str(e),
                },
            }

    def delete_document(self, kb_id: str, doc_id: str) -> Dict[str, Any]:
        """删除文档"""
        try:
            self._load_doc_metadata(kb_id)

            if doc_id not in self._doc_metadata:
                return {
                    "success": False,
                    "error": {
                        "code": 404,
                        "message": "Document not found",
                        "details": f"Document {doc_id} not found",
                    },
                }

            del self._doc_metadata[doc_id]
            self._save_doc_metadata(kb_id)

            return {"success": True, "data": {"document_id": doc_id}}
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return {
                "success": False,
                "error": {
                    "code": 500,
                    "message": "Error deleting document",
                    "details": str(e),
                },
            }


def get_rag_service() -> RAGService:
    """获取 RAG 服务实例"""
    return SimpleRAGService()
