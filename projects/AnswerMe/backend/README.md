# AnswerMe 后端代码说明文档

## 一、概述

**AnswerMe** 是一个基于 **RAG (Retrieval-Augmented Generation)** 的智能问答系统后端，采用 FastAPI 框架构建。系统通过向量检索从知识库中获取相关文档，再利用大语言模型生成准确的答案。

***

## 二、技术栈

| 类别        | 技术                    | 说明           |
| --------- | --------------------- | ------------ |
| Web框架     | FastAPI 0.109.0       | 高性能异步API框架   |
| 服务器       | Uvicorn 0.27.0        | ASGI服务器      |
| 数据验证      | Pydantic 2.5.3        | 数据模型和验证      |
| LLM服务     | OpenAI SDK 1.12.0     | GPT模型调用      |
| 向量数据库     | ChromaDB              | 本地向量存储和检索    |
| Embedding | sentence-transformers | 本地文本向量化      |
| 文档解析      | PyPDF2, python-docx   | PDF和Word文档处理 |

***

## 三、目录结构

```
backend/
├── main.py                 # 应用入口，FastAPI实例配置
├── requirements.txt        # 依赖清单
├── .env.example           # 环境变量示例
├── CONFIG.md              # 配置说明文档
│
├── config/                 # 配置模块
│   ├── __init__.py
│   ├── settings.py         # Pydantic Settings配置类
│   ├── env_loader.py      # 环境变量加载器
│   └── loader.py          # 配置加载辅助
│
├── routers/                # 路由模块（API端点）
│   ├── __init__.py
│   ├── health.py          # 健康检查路由
│   ├── chat.py            # 问答路由
│   ├── documents.py       # 文档管理路由
│   └── knowledge_base.py  # 知识库管理路由
│
├── services/              # 业务逻辑服务层
│   ├── __init__.py
│   ├── llm_service.py     # LLM服务（OpenAI/本地）
│   ├── embedding_service.py # Embedding服务
│   └── rag_service.py     # RAG核心服务
│
├── models/                # 数据模型/Schema
│   ├── __init__.py
│   └── schemas.py         # Pydantic数据模型
│
└── vector_db/             # 向量数据库抽象层
    ├── __init__.py
    └── database.py        # Chroma数据库实现
```

***

## 四、核心模块详解

### 4.1 应用入口 (main.py)

```python
# 创建FastAPI应用实例
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-based QA System Backend"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(health.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1/chat")
app.include_router(documents.router, prefix="/api/v1/documents")
app.include_router(knowledge_base.router, prefix="/api/v1/knowledge-base")
```

### 4.2 配置系统 (config/settings.py)

使用 Pydantic Settings 管理所有配置，支持环境变量注入：

```python
class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "AnswerMe QA System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # LLM配置
    LLM_API_TYPE: str = "openai"  # openai / local
    LLM_API_KEY: Optional[str]
    LLM_MODEL_NAME: str = "gpt-3.5-turbo"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048

    # Embedding配置
    EMBEDDING_API_TYPE: str = "openai"  # openai / local
    EMBEDDING_DIMENSION: int = 1536

    # 向量数据库配置
    VECTOR_DB_TYPE: str = "chroma"
    VECTOR_DB_PATH: str = "./vector_db"

    # 检索配置
    RETRIEVER_TOP_K: int = 5
    RETRIEVER_SCORE_THRESHOLD: float = 0.5
```

### 4.3 数据模型 (models/schemas.py)

核心数据结构：

```python
# 问答请求
class QuestionRequest(BaseModel):
    question: str                          # 用户问题
    knowledge_base_id: str                 # 知识库ID
    history: Optional[List[Message]] = []  # 对话历史
    temperature: Optional[float] = 0.7     # LLM温度参数
    top_k: Optional[int] = 5              # 检索文档数量

# 聊天响应
class ChatAnswerResponse(BaseModel):
    answer: str                            # 生成的答案
    sources: List[SourceDocument]          # 引用来源
    response_time_ms: int                   # 响应时间
    knowledge_base_id: str                  # 知识库ID
    question: str                          # 用户问题

# 知识库创建
class KnowledgeBaseCreate(BaseModel):
    name: str                              # 知识库名称
    description: Optional[str] = None      # 描述

# 文档上传响应
class DocumentUploadResponse(BaseModel):
    document_id: str                      # 文档ID
    filename: str                          # 文件名
    pages: int                             # 页数
    status: str                            # 处理状态
```

### 4.4 服务层架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Router Layer                            │
│  (health.py, chat.py, documents.py, knowledge_base.py)      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Service Layer                           │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │ LLM Service │  │ Embedding Svc   │  │ RAG Service     │  │
│  │ - OpenAI    │  │ - OpenAI        │  │ - query()       │  │
│  │ - Local     │  │ - Local         │  │ - upload()      │  │
│  └─────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Vector Database                           │
│              (ChromaDB - ChromaVectorDatabase)              │
└─────────────────────────────────────────────────────────────┘
```

***

## 五、API端点清单

### 5.1 健康检查

| 方法  | 路径        | 功能     |
| --- | --------- | ------ |
| GET | `/`       | 获取应用信息 |
| GET | `/health` | 健康检查   |

### 5.2 问答模块 (`/api/v1/chat`)

| 方法     | 路径         | 功能       |
| ------ | ---------- | -------- |
| POST   | `/query`   | 提交问题获取回答 |
| GET    | `/history` | 获取对话历史   |
| DELETE | `/history` | 清空对话历史   |

### 5.3 文档管理 (`/api/v1/documents`)

| 方法     | 路径          | 功能     |
| ------ | ----------- | ------ |
| GET    | `/`         | 获取文档列表 |
| GET    | `/{doc_id}` | 获取文档详情 |
| DELETE | `/{doc_id}` | 删除文档   |

### 5.4 知识库管理 (`/api/v1/knowledge-base`)

| 方法     | 路径                | 功能      |
| ------ | ----------------- | ------- |
| GET    | `/`               | 获取知识库列表 |
| POST   | `/`               | 创建知识库   |
| GET    | `/{kb_id}`        | 获取知识库详情 |
| DELETE | `/{kb_id}`        | 删除知识库   |
| POST   | `/{kb_id}/upload` | 上传文档    |

***

## 六、关键API完整链路与流程

### 6.1 问答查询流程 (`POST /api/v1/chat/query`)

这是系统的核心功能，完整的请求处理链路如下：

```
┌──────────┐    ┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│  Client  │───▶│   Router    │───▶│  RAG Service │───▶│ Vector Database│
│  Request │    │  (chat.py)  │    │ (rag_service)│    │   (ChromaDB)   │
└──────────┘    └─────────────┘    └──────────────┘    └────────────────┘
                                                     │
                    ┌──────────────────────────────┘
                    ▼
              ┌──────────────┐    ┌──────────────┐
              │  Embedding   │───▶│     LLM      │
              │   Service    │    │   Service    │
              └──────────────┘    └──────────────┘
                                        │
                                        ▼
                                 ┌──────────────┐
                                 │    Client     │
                                 │   Response    │
                                 └──────────────┘
```

**详细步骤：**

```
步骤1: 接收请求
   POST /api/v1/chat/query
   Body: {
       "question": "什么是机器学习？",
       "knowledge_base_id": "kb_xxx",
       "history": [{"role": "user", "content": "..."}]
   }

步骤2: 路由处理 (routers/chat.py)
   - 验证请求数据 (QuestionRequest)
   - 调用 rag_service.query()

步骤3: 问题向量化 (services/rag_service.py → embedding_service.py)
   - 使用 OpenAIEmbeddingService 或 LocalEmbeddingService
   - 调用 embedding.encode(question)
   - 返回 1536维向量 (OpenAI) 或 384维向量 (Local)

步骤4: 向量检索 (vector_db/database.py)
   - ChromaVectorDatabase.search()
   - 在指定collection中检索top_k=5个相似文档
   - 使用余弦相似度计算

步骤5: 构建Prompt
   - 将检索到的文档内容拼接为上下文
   - 组装对话历史
   - 构建完整的system prompt + user prompt

步骤6: LLM生成 (services/llm_service.py)
   - 使用 OpenAI ChatGPT 或本地LLM
   - 调用 generate(prompt, temperature, max_tokens)
   - 返回生成的答案

步骤7: 返回响应
   Response: {
       "answer": "机器学习是...",
       "sources": [
           {"document_id": "...", "content": "...", "score": 0.95}
       ],
       "response_time_ms": 1234,
       "knowledge_base_id": "kb_xxx",
       "question": "什么是机器学习？"
   }
```

**代码示例：**

```python
# routers/chat.py
@router.post("/query", response_model=ChatAnswerResponse)
async def query_question(request: QuestionRequest):
    start_time = time.time()

    answer, sources = rag_service.query(
        question=request.question,
        knowledge_base_id=request.knowledge_base_id,
        history=[{"role": m.role, "content": m.content} for m in request.history],
        top_k=request.top_k or settings.RETRIEVER_TOP_K,
        temperature=request.temperature or settings.LLM_TEMPERATURE
    )

    response_time = int((time.time() - start_time) * 1000)

    return ChatAnswerResponse(
        answer=answer,
        sources=sources,
        response_time_ms=response_time,
        knowledge_base_id=request.knowledge_base_id,
        question=request.question
    )

# services/rag_service.py
def query(self, question, knowledge_base_id, history, top_k, temperature):
    # 1. 嵌入问题
    query_embedding = self.embedding_service.encode(question)

    # 2. 检索相关文档
    search_results = self.vector_db.search(
        collection_name=knowledge_base_id,
        query_embedding=query_embedding,
        k=top_k
    )

    # 3. 构建上下文
    context = self._build_context(search_results)

    # 4. 构建Prompt
    prompt = self._build_prompt(question, context, history)

    # 5. 生成答案
    answer = self.llm_service.generate(prompt, temperature)

    # 6. 提取来源
    sources = self._extract_sources(search_results)

    return answer, sources
```

***

### 6.2 文档上传流程 (`POST /api/v1/knowledge-base/{kb_id}/upload`)

```
┌──────────┐    ┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│  Client  │───▶│   Router    │───▶│  Document    │───▶│   File System  │
│  (File)  │    │ (kb_router)  │    │  Processor   │    │   (Storage)   │
└──────────┘    └─────────────┘    └──────────────┘    └────────────────┘
                                              │
                    ┌────────────────────────┘
                    ▼
              ┌──────────────┐    ┌──────────────┐
              │  Embedding   │───▶│ Vector DB    │
              │   Service    │    │  (ChromaDB)  │
              └──────────────┘    └──────────────┘
```

**详细步骤：**

```
步骤1: 文件上传
   POST /api/v1/knowledge-base/{kb_id}/upload
   Content-Type: multipart/form-data
   Body: file (PDF/DOCX/TXT/MD)

步骤2: 路由处理 (routers/knowledge_base.py)
   - 获取kb_id参数
   - 验证文件类型 (检查扩展名)
   - 验证文件大小 (< 10MB)
   - 调用 rag_service.upload_document()

步骤3: 文件保存
   - 生成唯一文件名
   - 保存到 uploads/{kb_id}/ 目录

步骤4: 文档解析 (rag_service.py)
   根据文件类型调用不同解析器：
   - PDF: PyPDF2 提取文本
   - DOCX: python-docx 提取文本
   - TXT/MD: 直接读取

步骤5: 文本分块
   - 按固定长度或段落分块
   - 块大小: 约500-1000字符
   - 块之间可重叠

步骤6: 向量化
   - 对每个文本块调用 embedding.encode()
   - 生成向量列表

步骤7: 存储到向量数据库
   - 调用 vector_db.add_documents()
   - 存储: ids, documents, embeddings, metadatas

步骤8: 返回响应
   Response: {
       "document_id": "doc_xxx",
       "filename": "machine_learning.pdf",
       "pages": 42,
       "status": "completed"
   }
```

**代码示例：**

```python
# routers/knowledge_base.py
@router.post("/{kb_id}/upload", response_model=DocumentUploadResponse)
async def upload_document(kb_id: str, file: UploadFile):
    # 验证文件类型
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in settings.DOCUMENT_SUPPORTED_FORMATS:
        raise HTTPException(400, f"Unsupported file type: {ext}")

    # 验证文件大小
    content = await file.read()
    if len(content) > settings.DOCUMENT_MAX_SIZE:
        raise HTTPException(400, "File too large")

    # 保存文件
    upload_path = f"uploads/{kb_id}/{file.filename}"
    os.makedirs(os.path.dirname(upload_path), exist_ok=True)
    with open(upload_path, "wb") as f:
        f.write(content)

    # 上传到RAG服务
    document_id = rag_service.upload_document(kb_id, upload_path)

    return DocumentUploadResponse(
        document_id=document_id,
        filename=file.filename,
        pages=0,
        status="completed"
    )

# services/rag_service.py
def upload_document(self, kb_id, file_path):
    # 解析文档
    text = self._parse_document(file_path)

    # 分块
    chunks = self._chunk_text(text)

    # 向量化
    embeddings = self.embedding_service.encode_batch(chunks)

    # 生成IDs
    ids = [f"{kb_id}_{i}" for i in range(len(chunks))]

    # 存储元数据
    metadatas = [{
        "file_path": file_path,
        "chunk_index": i,
        "total_chunks": len(chunks)
    } for i in range(len(chunks))]

    # 存入向量数据库
    self.vector_db.add_documents(kb_id, ids, chunks, embeddings, metadatas)

    return kb_id
```

***

### 6.3 创建知识库流程 (`POST /api/v1/knowledge-base`)

```
┌──────────┐    ┌─────────────┐    ┌──────────────┐    ┌────────────────┐
│  Client  │───▶│   Router    │───▶│ RAG Service  │───▶│ Vector Database│
│  Request │    │ (kb_router) │    │              │    │   (ChromaDB)   │
└──────────┘    └─────────────┘    └──────────────┘    └────────────────┘
```

**详细步骤：**

```
步骤1: 创建请求
   POST /api/v1/knowledge-base
   Body: {
       "name": "机器学习知识库",
       "description": "包含机器学习相关的技术文档"
   }

步骤2: 路由处理
   - 验证请求数据
   - 检查名称是否重复
   - 调用 rag_service.create_knowledge_base()

步骤3: 创建集合 (在ChromaDB中)
   - 生成唯一ID
   - 调用 vector_db.create_collection()
   - Chroma会创建对应的collection

步骤4: 返回响应
   Response: {
       "id": "kb_xxx",
       "name": "机器学习知识库",
       "description": "...",
       "document_count": 0,
       "created_at": "2024-01-01T00:00:00",
       "updated_at": "2024-01-01T00:00:00"
   }
```

**代码示例：**

```python
# routers/knowledge_base.py
@router.post("/", response_model=KnowledgeBaseResponse)
async def create_knowledge_base(request: KnowledgeBaseCreate):
    kb = rag_service.create_knowledge_base(
        name=request.name,
        description=request.description
    )
    return KnowledgeBaseResponse(**kb)

# services/rag_service.py
def create_knowledge_base(self, name, description=None):
    kb_id = f"kb_{uuid.uuid4().hex[:8]}"

    # 创建向量数据库集合
    self.vector_db.create_collection(
        name=kb_id,
        dimension=settings.EMBEDDING_DIMENSION
    )

    # 创建元数据存储（可扩展为SQLite等）
    kb_meta = {
        "id": kb_id,
        "name": name,
        "description": description or "",
        "document_count": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

    return kb_meta
```

***

### 6.4 健康检查流程 (`GET /api/v1/health`)

```
┌──────────┐    ┌─────────────┐    ┌────────────────────────┐
│  Client  │───▶│   Router    │───▶│  Check Components      │
│  Request │    │ (health.py) │    │ - Vector DB Connection │
└──────────┘    └─────────────┘    │ - LLM Service Status   │
                                  └────────────────────────┘
```

**详细步骤：**

```
步骤1: 健康检查请求
   GET /api/v1/health

步骤2: 检查各组件状态
   - VectorDB连接: vector_db.connect()
   - LLM服务可用性
   - Embedding服务可用性

步骤3: 返回健康状态
   Response: {
       "status": "healthy",
       "version": "1.0.0",
       "timestamp": "2024-01-01T00:00:00",
       "components": {
           "vector_db": "connected",
           "llm_service": "available",
           "embedding_service": "available"
       }
   }
```

***

## 七、服务间依赖关系

```
                    ┌─────────────┐
                    │  FastAPI    │
                    │   App       │
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
    ┌───────────┐   ┌───────────┐    ┌───────────┐
    │  Routers  │   │  Routers  │    │  Routers  │
    │  (chat)   │   │ (kb_base) │    │(documents)│
    └─────┬─────┘   └─────┬─────┘    └─────┬─────┘
          │               │                │
          └───────────────┼────────────────┘
                          │
                          ▼
                  ┌───────────────┐
                  │ RAG Service   │  ◀─── 核心业务逻辑
                  └───────┬───────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │ LLM Svc   │  │Embedding  │  │ Vector DB │
    │           │  │   Svc     │  │           │
    └─────┬─────┘  └─────┬─────┘  └─────┬─────┘
          │              │              │
          ▼              ▼              ▼
    ┌───────────┐  ┌───────────┐  ┌───────────┐
    │ OpenAI    │  │ OpenAI    │  │ ChromaDB  │
    │ API       │  │ API       │  │ Local     │
    └───────────┘  └───────────┘  └───────────┘
```

***

## 八、向量数据库操作流程

### 8.1 ChromaDB集合管理

```python
# 创建知识库 (创建集合)
collection = client.create_collection(
    name="kb_xxx",
    metadata={"hnsw:space": "cosine"}  # 使用余弦相似度
)

# 获取集合
collection = client.get_collection(name="kb_xxx")

# 列出所有集合
collections = client.list_collections()

# 删除集合
client.delete_collection(name="kb_xxx")
```

### 8.2 文档存储

```python
# 添加文档
collection.add(
    ids=["doc_1", "doc_2", "doc_3"],
    documents=["文本内容1", "文本内容2", "文本内容3"],
    embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]],
    metadatas=[{"source": "file1.pdf"}, {"source": "file2.pdf"}, {"source": "file3.pdf"}]
)
```

### 8.3 向量检索

```python
# 相似性搜索
results = collection.query(
    query_embeddings=[[0.1, 0.2, ...]],  # 查询向量
    n_results=5,                          # 返回5个结果
    include=["documents", "metadatas", "distances"]  # 返回内容
)

# 结果格式
# {
#     "documents": [["相关文本1", "相关文本2", ...]],
#     "metadatas": [[{"source": "..."}, ...]],
#     "distances": [[0.1, 0.2, ...]]  # 距离分数，越小越相似
# }
```

***

## 九、配置与环境变量

### 9.1 必需的环境变量

```bash
# .env 文件
# LLM 配置
LLM_API_TYPE=openai                    # openai 或 local
LLM_API_KEY=sk-xxxx                    # OpenAI API Key
LLM_MODEL_NAME=gpt-3.5-turbo           # 模型名称
LLM_TEMPERATURE=0.7                    # 生成温度
LLM_MAX_TOKENS=2048                   # 最大token数

# Embedding 配置
EMBEDDING_API_TYPE=openai              # openai 或 local
EMBEDDING_API_KEY=sk-xxxx             # OpenAI API Key
EMBEDDING_MODEL_NAME=text-embedding-ada-002

# 向量数据库配置
VECTOR_DB_TYPE=chroma                  # chroma
VECTOR_DB_PATH=./vector_db            # 数据库存储路径

# 应用配置
DEBUG=true
CORS_ORIGINS=["http://localhost:3000"]
```

### 9.2 本地模式配置

```bash
# 使用本地LLM
LLM_API_TYPE=local
LLM_API_BASE=http://localhost:8080
LLM_MODEL_NAME=llama2

# 使用本地Embedding
EMBEDDING_API_TYPE=local
EMBEDDING_MODEL_NAME=all-MiniLM-L6-v2
```

***

## 十、运行与部署

### 10.1 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env
# 编辑 .env 填入必要的API Key

# 启动开发服务器
uvicorn main:app --reload --port 8000

# 或直接运行
python main.py
```

### 10.2 访问API文档

启动服务后，可通过以下地址访问自动生成的API文档：

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **OpenAPI JSON**: <http://localhost:8000/openapi.json>

### 10.3 测试API

```bash
# 健康检查
curl http://localhost:8000/api/v1/health

# 创建知识库
curl -X POST http://localhost:8000/api/v1/knowledge-base \
  -H "Content-Type: application/json" \
  -d '{"name": "测试知识库", "description": "测试用"}'

# 问答查询
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是AI？", "knowledge_base_id": "kb_xxx"}'
```

***

## 十一、项目特点与待完善功能

### 11.1 当前特点

1. **模块化设计**: 配置、路由、服务、数据模型分层清晰
2. **灵活扩展**: 支持多种LLM/Embedding后端（OpenAI/本地）
3. **RAG核心**: 完整的检索增强生成流程
4. **向量检索**: 基于Chroma的高效向量存储和检索
5. **自动API文档**: FastAPI自动生成Swagger/ReDoc文档

### 11.2 待完善功能

1. **API实现**: 部分路由端点为空实现
2. **用户认证**: 缺乏JWT/API Key认证机制
3. **文档处理**: 需完善PDF/DOCX解析和分块策略
4. **持久化存储**: 知识库元数据需持久化（可使用SQLite）
5. **错误处理**: 需完善各类异常处理和日志
6. **测试覆盖**: 缺乏单元测试和集成测试
7. **流式输出**: LLM流式响应支持

***

*文档版本: 1.0.0*
*最后更新: 2024年*
