# 后端配置说明

## 环境变量配置

### 1. 创建 .env 文件

```bash
cd backend
cp .env.example .env
```

### 2. 配置项说明

#### LLM 配置
- `LLM_API_TYPE`: LLM API 类型 (`openai` 或 `local`)
- `LLM_API_KEY`: API Key (OpenAI 或其他服务)
- `LLM_API_BASE`: API Base URL (本地模型地址)
- `LLM_MODEL_NAME`: 模型名称 (如 `gpt-3.5-turbo` 或 `llama2`)
- `LLM_TEMPERATURE`: 温度参数 (0-1)
- `LLM_MAX_TOKENS`: 最大 token 数

#### Embedding 配置
- `EMBEDDING_API_TYPE`: Embedding API 类型 (`openai` 或 `local`)
- `EMBEDDING_API_KEY`: API Key
- `EMBEDDING_API_BASE`: API Base URL
- `EMBEDDING_MODEL_NAME`: 模型名称
- `EMBEDDING_DIMENSION`: 向量维度

#### 向量数据库配置
- `VECTOR_DB_TYPE`: 数据库类型 (`chroma` 或 `milvus`)
- `VECTOR_DB_PATH`: Chroma 数据库路径
- `VECTOR_DB_HOST`: 主机地址
- `VECTOR_DB_PORT`: 端口
- `VECTOR_DB_USER`: 用户名
- `VECTOR_DB_PASSWORD`: 密码

#### 检索配置
- `RETRIEVER_TOP_K`: 检索 top K 个文档
- `RETRIEVER_SCORE_THRESHOLD`: 相似度分数阈值

### 3. 示例配置

#### 使用 OpenAI API
```bash
LLM_API_TYPE=openai
LLM_API_KEY=sk-your_openai_api_key
LLM_MODEL_NAME=gpt-3.5-turbo

EMBEDDING_API_TYPE=openai
EMBEDDING_API_KEY=sk-your_openai_api_key
EMBEDDING_MODEL_NAME=text-embedding-ada-002

VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=./vector_db
```

#### 使用本地 Ollama
```bash
LLM_API_TYPE=local
LLM_API_BASE=http://localhost:11434/v1
LLM_MODEL_NAME=llama2

EMBEDDING_API_TYPE=local
EMBEDDING_API_BASE=http://localhost:11434/v1
EMBEDDING_MODEL_NAME=nomic-embed-text

VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=./vector_db
```

## 配置加载

配置通过 `backend.config` 模块加载:

```python
from backend.config import settings, load_env

# 加载 .env 文件
load_env()

# 访问配置
print(settings.LLM_MODEL_NAME)
```

## 配置验证

启动服务时会自动加载配置并记录日志:

```bash
uvicorn main:app --reload --port 8000
```

查看日志确认配置已加载:
```
INFO - Starting AnswerMe QA System v1.0.0
INFO - LLM API Type: local
INFO - Embedding API Type: local
INFO - Vector DB Type: chroma
```
