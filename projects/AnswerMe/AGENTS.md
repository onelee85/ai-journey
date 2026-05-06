# AGENTS.md

## 1. 项目概述

AnswerMe 是一个基于 RAG 的知识库问答系统，当前由 FastAPI 后端和 React 18 + TypeScript + Vite 前端组成。
仓库根目录下 `backend/` 是 Python API、RAG 服务、文档解析、Embedding、LLM 与 Chroma 本地向量库；`web/` 是单页前端，提供问答、知识库管理、文档管理和后端连接设置。
后端运行在 `http://localhost:8000`，前端开发服务默认运行在 `http://localhost:5173`，前端通过 `web/src/api.ts` 调用 `/api/v1/*` 接口。
运行时数据包括 `backend/uploads/` 和 `backend/vector_db/`，只应保存在本地，不要提交。
详细产品与接口背景见 [README.md](README.md)，后端说明见 [backend/README.md](backend/README.md)，前端说明见 [web/README.md](web/README.md)。

## 2. 快速命令

| 场景 | 命令 | 目录 | 说明 |
| --- | --- | --- | --- |
| 后端创建环境 | `python -m venv venv` | `backend/` | 创建本地虚拟环境 |
| 后端激活环境 | `source venv/bin/activate` | `backend/` | macOS/Linux shell |
| 后端安装依赖 | `pip install -r requirements.txt` | `backend/` | 安装 FastAPI、ChromaDB、文档解析等依赖 |
| 后端配置 env | `cp .env.example .env` | `backend/` | 本地配置文件，不提交 |
| 后端启动 | `uvicorn main:app --reload --port 8000` | `backend/` | `main.py` 启动时会自动加载 `backend/.env` |
| 后端健康检查 | `curl http://localhost:8000/health` | 任意目录 | 根健康检查 |
| 后端 API 文档 | 打开 `http://localhost:8000/docs` | 浏览器 | FastAPI Swagger |
| 前端安装依赖 | `pnpm install` | `web/` | 建议 Node.js 18+ |
| 前端开发启动 | `pnpm run dev` | `web/` | Vite dev server |
| 前端构建 | `pnpm run build` | `web/` | TypeScript build + Vite build |
| 前端预览 | `pnpm run preview` | `web/` | 预览生产构建 |

环境变量：

- 后端 env 文件：`backend/.env`，模板为 [backend/.env.example](backend/.env.example)，由 [backend/main.py](backend/main.py) 通过 `load_env()` 自动加载。
- 前端 env 文件：`web/.env`，模板为 [web/.env.example](web/.env.example)，常用变量是 `VITE_API_BASE_URL=http://localhost:8000`。
- 前端设置页也可修改 API Base URL，并保存到浏览器 `localStorage` 的 `answerme.apiBase`。

## 3. 后端架构

```text
backend/
├── main.py                    # FastAPI app、CORS、全局异常处理、路由注册、启动日志
├── requirements.txt           # Python 依赖
├── CONFIG.md                  # 环境变量与配置说明
├── config/
│   ├── settings.py            # Pydantic Settings，集中读取配置
│   ├── env_loader.py          # .env 加载逻辑
│   └── loader.py              # 配置加载辅助
├── routers/
│   ├── health.py              # /api/v1/health 健康检查
│   ├── chat.py                # /api/v1/chat 问答与历史
│   ├── documents.py           # /api/v1/documents 文档列表与删除
│   └── knowledge_base.py      # /api/v1/knowledge-base 知识库 CRUD 与上传
├── services/
│   ├── document_service.py    # 文档解析与文本抽取
│   ├── embedding_service.py   # OpenAI/local Embedding 封装
│   ├── llm_service.py         # OpenAI/local LLM 封装
│   └── rag_service.py         # 知识库、向量检索、上传、问答核心流程
└── models/
    └── schemas.py             # Pydantic 请求/响应模型
```

核心子系统：

- 路由层：只做 HTTP 入参校验、状态码和响应模型组织；业务逻辑下沉到 `services/`。详见 [backend/README.md](backend/README.md)。
- RAG 服务：`rag_service.py` 负责知识库生命周期、文档入库、向量检索和问答编排。详见 [backend/README.md](backend/README.md)。
- 配置系统：`config/settings.py` 统一管理 LLM、Embedding、向量库、检索参数。详见 [backend/CONFIG.md](backend/CONFIG.md)。
- 运行时存储：`backend/uploads/` 保存上传文件，`backend/vector_db/` 保存 Chroma 数据，不进入版本库。

前后端术语映射：

| 后端字段/接口 | 前端名称 | 说明 |
| --- | --- | --- |
| `knowledge_base_id` | `selectedKbId` | 当前选中的知识库 ID |
| `KnowledgeBaseResponse` | `KnowledgeBase` | 知识库列表、创建、更新返回类型 |
| `DocumentResponse` | `DocumentItem` | 文档列表行数据 |
| `QuestionRequest.history` | `messages` | 前端聊天消息数组 |
| `ChatAnswerResponse.sources` | 来源文档 | 问答页右侧的检索片段 |

## 4. 前端架构

技术栈：React 18、TypeScript、Vite 4、pnpm、lucide-react、原生 Fetch API。当前没有路由库，应用在 [web/src/App.tsx](web/src/App.tsx) 内用 `activeView` 状态切换 `chat`、`knowledge`、`documents`、`settings` 四个视图。

```text
web/
├── package.json              # pnpm 脚本与依赖
├── vite.config.ts            # Vite 配置
├── index.html                # HTML 入口
└── src/
    ├── main.tsx              # React 挂载入口
    ├── App.tsx               # 主应用、视图组件、交互状态
    ├── api.ts                # AnswerMeApi，集中封装后端请求
    ├── types.ts              # 前后端共享语义的 TS 类型
    └── styles.css            # 全局 CSS
```

前端约定：

- API 层集中在 [web/src/api.ts](web/src/api.ts)，新增接口先扩展 `AnswerMeApi`，组件不要直接散落 `fetch`。
- 类型集中在 [web/src/types.ts](web/src/types.ts)，接口字段应与 Pydantic schema 保持一致。
- 组件目前为轻量本地组件，没有引入 shadcn/ui、MUI、Redux、Zustand 或 React Router。
- 图标使用 `lucide-react`，按钮内优先使用已有图标。
- 全局样式在 [web/src/styles.css](web/src/styles.css)，保持现有紧凑后台工具风格。

详细说明见 [web/README.md](web/README.md)。

## 5. 关键约定

1. 不要提交 `.env`、API key、上传文档、向量库数据或构建产物；本地数据只放 `backend/uploads/`、`backend/vector_db/`、`web/dist/`。详见 [backend/CONFIG.md](backend/CONFIG.md) 与 [web/README.md](web/README.md)。
2. 后端配置只能通过 `backend/config` 读取，不要在路由或服务里手写 `os.getenv` 分散配置。详见 [backend/CONFIG.md](backend/CONFIG.md)。
3. 后端路由保持薄层：HTTP 处理在 `backend/routers/`，业务流程在 `backend/services/`，数据契约在 `backend/models/schemas.py`。详见 [backend/README.md](backend/README.md)。
4. 前端请求只能通过 `AnswerMeApi` 扩展；错误响应统一走 `parseResponse()`。详见 [web/src/api.ts](web/src/api.ts)。
5. 前后端字段名要保持一致，尤其是 `knowledge_base_id`、`document_id`、`created_at`、`updated_at`；不要在组件内临时改名造成映射混乱。详见 [web/src/types.ts](web/src/types.ts)。
6. 文档上传支持格式由后端限制为 `.txt`、`.pdf`、`.docx`、`.md`；前端 `accept` 只能与后端保持同步。详见 [backend/routers/knowledge_base.py](backend/routers/knowledge_base.py)。
7. 对外 API 路径以 `/api/v1` 为准；根 `/health` 可用于快速探活，前端主要调用 `/api/v1/health/`。详见 [backend/main.py](backend/main.py)。
8. 当前没有鉴权和 Token 流程；不要给 curl、fetch 或 UI 增加伪造的 Authorization 逻辑，除非后端先实现认证。详见 [backend/routers/](backend/routers/)。
9. Python 代码遵循 PEP 8、4 空格缩进；TypeScript 保持现有函数组件和显式类型风格。详见 [backend/README.md](backend/README.md) 与 [web/README.md](web/README.md)。

## 6. 本地开发及验证流程

完整闭环：

1. 改代码：后端改 `backend/routers`、`backend/services`、`backend/models`；前端改 `web/src`。
2. 构建检查：前端执行 `cd web && pnpm run build`；后端当前未配置统一 build，可至少执行导入/启动检查。
3. 启动后端：

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --port 8000
```

4. 启动前端：

```bash
cd web
pnpm run dev
```

5. 浏览器验证：打开 `http://localhost:5173`，在设置页确认 API Base URL 指向 `http://localhost:8000`。

curl 验证模板：

```bash
curl http://localhost:8000/health
curl http://localhost:8000/api/v1/health/
curl http://localhost:8000/api/v1/knowledge-base/
curl -X POST http://localhost:8000/api/v1/knowledge-base/ \
  -H "Content-Type: application/json" \
  -d '{"name":"测试知识库","description":"本地验证"}'
curl -X PATCH http://localhost:8000/api/v1/knowledge-base/<kb_id> \
  -H "Content-Type: application/json" \
  -d '{"name":"更新后的知识库","description":"更新验证"}'
curl -F "file=@docs/机器学习入门.md" \
  http://localhost:8000/api/v1/knowledge-base/<kb_id>/upload
curl "http://localhost:8000/api/v1/documents/?knowledge_base_id=<kb_id>&page=1&page_size=20"
curl -X POST http://localhost:8000/api/v1/chat/query \
  -H "Content-Type: application/json" \
  -d '{"question":"什么是机器学习？","knowledge_base_id":"<kb_id>","history":[],"temperature":0.7,"top_k":5}'
```

Token 获取：当前项目没有登录、鉴权和 Token 获取流程。

日志路径：后端日志通过 `logging.StreamHandler(sys.stdout)` 输出到启动终端；当前没有文件日志路径。前端日志查看浏览器 DevTools Console 和 Vite 终端输出。

## 7. 质量检查

| 类型 | 命令 | 目录 | 当前状态 |
| --- | --- | --- | --- |
| 前端类型检查 + 构建 | `pnpm run build` | `web/` | 已配置，必须跑 |
| 前端开发启动 | `pnpm run dev` | `web/` | 已配置 |
| 前端生产预览 | `pnpm run preview` | `web/` | 已配置 |
| 前端 lint | 无 | `web/` | 未配置 ESLint |
| 前端 format | 无 | `web/` | 未配置 Prettier |
| 后端测试 | `pytest` | `backend/` | 约定命令，当前未提交测试套件 |
| 后端 lint | 无 | `backend/` | 未配置 Ruff/Flake8 |
| 后端 format | 无 | `backend/` | 未配置 Black/isort |
| 后端启动检查 | `uvicorn main:app --reload --port 8000` | `backend/` | 已配置 |

新增行为变更时，优先补 `backend/tests/test_<module>.py` 的服务或 API 测试；如果引入 lint/format 工具，需要同步更新本节和对应 README。

## 8. 参考项目约定

优先级规则：

1. 当前代码实现优先于早期规划文档；例如前端当前使用原生 fetch 和本地状态，不使用 README 规划中的 Axios、Zustand、shadcn/ui。
2. 离目标文件最近的文档优先：改后端看 [backend/README.md](backend/README.md) 和 [backend/CONFIG.md](backend/CONFIG.md)，改前端看 [web/README.md](web/README.md)。
3. 根 [README.md](README.md) 作为产品、架构和 API 背景参考；若与实际代码冲突，以实际代码和专项 README 为准。
4. 无外部参考项目被固定要求；新增框架、组件库或架构模式前，先复用本仓库现有模式。

## 9. 文档导航

| 文档 | 用途 | 何时阅读 |
| --- | --- | --- |
| [README.md](README.md) | 产品背景、系统分层、API 概览 | 理解项目整体目标 |
| [AGENTS.md](AGENTS.md) | AI 协作入口、命令、架构、约定 | 每次开始任务先读 |
| [backend/README.md](backend/README.md) | 后端目录、模块、API 链路说明 | 修改 FastAPI、RAG、文档或模型逻辑 |
| [backend/CONFIG.md](backend/CONFIG.md) | LLM、Embedding、向量库、检索配置 | 修改配置、排查模型或环境变量问题 |
| [backend/.env.example](backend/.env.example) | 后端环境变量模板 | 初始化或调整本地后端环境 |
| [web/README.md](web/README.md) | 前端技术栈、目录、运行和接口说明 | 修改 React/Vite 前端 |
| [web/.env.example](web/.env.example) | 前端环境变量模板 | 修改前端 API Base URL 默认值 |
| [docs/机器学习入门.md](docs/机器学习入门.md) | 示例知识文档 | 本地上传和问答验证 |
