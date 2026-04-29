import os
from typing import List, Dict, Any, Optional
from uuid import uuid4
import logging

logger = logging.getLogger(__name__)


class VectorDatabase:
    """向量数据库基类，支持多种后端"""

    def __init__(self, db_type: str = "chroma", **kwargs):
        self.db_type = db_type
        self.kwargs = kwargs
        self._client = None
        self._collections: Dict[str, Any] = {}

    def connect(self):
        """连接数据库"""
        raise NotImplementedError

    def create_collection(self, name: str, dimension: int = 1536) -> str:
        """创建集合（知识库）"""
        raise NotImplementedError

    def get_collection(self, name: str):
        """获取集合"""
        raise NotImplementedError

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
    ) -> List[str]:
        """添加文档到集合"""
        raise NotImplementedError

    def delete_documents(self, collection_name: str, ids: List[str]) -> bool:
        """从集合中删除文档"""
        raise NotImplementedError

    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        k: int = 5,
        score_threshold: float = 0.5,
    ) -> List[Dict]:
        """搜索相似文档"""
        raise NotImplementedError

    def delete_collection(self, name: str) -> bool:
        """删除集合"""
        raise NotImplementedError

    def get_document_count(self, collection_name: str) -> int:
        """获取集合中文档数量"""
        raise NotImplementedError

    def list_collections(self) -> List[Dict]:
        """列出所有集合"""
        raise NotImplementedError


class ChromaVectorDatabase(VectorDatabase):
    """Chroma 向量数据库实现"""

    def __init__(self, path: str = "./vector_db", **kwargs):
        super().__init__(db_type="chroma", path=path, **kwargs)
        self.path = path
        self._client = None

    def connect(self):
        """连接 Chroma 数据库"""
        try:
            import chromadb
            from chromadb.config import Settings

            os.makedirs(self.path, exist_ok=True)
            self._client = chromadb.PersistentClient(path=self.path)
            logger.info(f"Connected to Chroma database at {self.path}")
        except ImportError:
            raise ImportError("Please install chromadb: pip install chromadb")

    def create_collection(self, name: str, dimension: int = 1536) -> str:
        """创建集合"""
        if self._client is None:
            self.connect()

        collection_name = f"kb_{uuid4().hex}"
        collection = self._client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine", "display_name": name},
        )
        self._collections[collection_name] = collection
        logger.info(f"Created collection: {collection_name}")
        return collection_name

    def get_collection(self, name: str):
        """获取集合"""
        if self._client is None:
            self.connect()

        if name not in self._collections:
            collection = self._client.get_collection(name=name)
            self._collections[name] = collection

        return self._collections[name]

    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        embeddings: List[List[float]],
        metadatas: List[Dict],
    ) -> List[str]:
        """添加文档"""
        collection = self.get_collection(collection_name)

        ids = [str(uuid4()) for _ in range(len(documents))]

        collection.add(
            ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
        )

        logger.info(
            f"Added {len(documents)} documents to collection: {collection_name}"
        )
        return ids

    def delete_documents(self, collection_name: str, ids: List[str]) -> bool:
        """删除集合中的指定文档块"""
        if not ids:
            return True

        try:
            collection = self.get_collection(collection_name)
            collection.delete(ids=ids)
            logger.info(
                f"Deleted {len(ids)} documents from collection: {collection_name}"
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting documents from {collection_name}: {e}")
            return False

    def search(
        self,
        collection_name: str,
        query_embedding: List[float],
        k: int = 5,
        score_threshold: float = 0.5,
    ) -> List[Dict]:
        """搜索相似文档"""
        collection = self.get_collection(collection_name)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=k,
            include=["documents", "embeddings", "metadatas", "distances"],
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        search_results = []
        for i, (doc, metadata, dist) in enumerate(zip(documents, metadatas, distances)):
            score = 1 - dist
            if score >= score_threshold:
                search_results.append(
                    {
                        "document": doc,
                        "metadata": metadata,
                        "score": score,
                        "distance": dist,
                    }
                )

        logger.info(
            f"Search returned {len(search_results)} results for collection: {collection_name}"
        )
        return search_results

    def delete_collection(self, name: str) -> bool:
        """删除集合"""
        if self._client is None:
            self.connect()

        try:
            self._client.delete_collection(name=name)
            if name in self._collections:
                del self._collections[name]
            logger.info(f"Deleted collection: {name}")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {name}: {e}")
            return False

    def get_document_count(self, collection_name: str) -> int:
        """获取文档数量"""
        collection = self.get_collection(collection_name)
        return collection.count()

    def list_collections(self) -> List[Dict]:
        """列出所有集合"""
        if self._client is None:
            self.connect()

        collections = self._client.list_collections()
        return [
            {"id": coll.name, "name": coll.name, "count": coll.count()}
            for coll in collections
        ]


def get_vector_database(db_type: str = None, **kwargs) -> VectorDatabase:
    """获取向量数据库实例"""
    if db_type is None:
        from config import settings

        db_type = settings.VECTOR_DB_TYPE

    if db_type == "chroma":
        from config import settings

        path = kwargs.get("path", kwargs.get("VECTOR_DB_PATH", settings.VECTOR_DB_PATH))
        return ChromaVectorDatabase(path=path)
    elif db_type == "milvus":
        raise NotImplementedError("Milvus database not implemented yet")
    elif db_type == "pinecone":
        raise NotImplementedError("Pinecone database not implemented yet")
    else:
        raise ValueError(f"Unknown database type: {db_type}")
