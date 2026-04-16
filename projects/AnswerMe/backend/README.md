# AnswerMe QA System - Backend

## 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

## 配置环境变量

创建 `.env` 文件:

```bash
# LLM 配置
LLM_API_TYPE=openai
LLM_API_KEY=your_api_key_here
LLM_MODEL_NAME=gpt-3.5-turbo

# Embedding 配置
EMBEDDING_API_TYPE=openai
EMBEDDING_API_KEY=your_api_key_here
EMBEDDING_MODEL_NAME=text-embedding-ada-002

# 向量数据库配置
VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=./vector_db

# 其他配置
DEBUG=True
```

## 运行服务

```bash
# 开发模式
uvicorn main:app --reload --port 8000

# 生产模式
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API 文档

启动服务后访问:

```
http://localhost:8000/docs
```
