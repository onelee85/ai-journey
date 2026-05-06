# AnswerMe 前端

AnswerMe 前端是基于 React、TypeScript 和 Vite 构建的单页应用，对接已完成的 FastAPI 后端，提供 RAG 问答、知识库管理、文档管理和后端连接配置能力。

## 技术栈

- React 18 + TypeScript
- Vite 4
- pnpm
- lucide-react 图标
- 原生 Fetch API 调用后端接口

## 目录结构

```text
web/
├── index.html              # Vite HTML 入口
├── package.json            # 脚本与依赖
├── pnpm-lock.yaml          # pnpm 锁文件
├── vite.config.ts          # Vite 配置
└── src/
    ├── App.tsx             # 主应用、页面与交互逻辑
    ├── api.ts              # 后端 API client
    ├── types.ts            # 前后端数据类型
    ├── main.tsx            # React 挂载入口
    ├── styles.css          # 全局样式
    └── vite-env.d.ts       # Vite 类型声明
```

## 环境要求

建议使用 Node.js 18+。如果本机使用 nvm：

```bash
nvm use 18
```

项目使用 pnpm 管理依赖和运行脚本。

## 安装与运行

在 `web/` 目录执行：

```bash
pnpm install
pnpm run dev
```

默认开发服务地址为：

```text
http://localhost:5173
```

构建生产包：

```bash
pnpm run build
```

本地预览生产包：

```bash
pnpm run preview
```

## 后端配置

默认后端地址为：

```text
http://localhost:8000
```

可复制 `.env.example` 创建本地配置：

```bash
cp .env.example .env
```

然后按需修改：

```env
VITE_API_BASE_URL=http://localhost:8000
```

也可以在前端“设置”页面中修改 API Base URL，配置会保存到浏览器 `localStorage`。

## 功能说明

- 问答页面：选择知识库后发送问题，读取聊天历史，展示答案和来源文档片段。
- 知识库页面：创建、选择、删除知识库，并上传 `.pdf`、`.docx`、`.txt`、`.md` 文档。
- 文档页面：按知识库筛选文档，搜索文件名，查看状态、大小、分块数和更新时间，支持删除。
- 设置页面：查看后端健康状态、版本、检查时间，并跳转 FastAPI Swagger 文档。

## 对接接口

前端主要调用以下后端接口：

- `GET /api/v1/health/`
- `GET /api/v1/knowledge-base/`
- `POST /api/v1/knowledge-base/`
- `DELETE /api/v1/knowledge-base/{kb_id}`
- `POST /api/v1/knowledge-base/{kb_id}/upload`
- `GET /api/v1/documents/`
- `DELETE /api/v1/documents/{kb_id}/{doc_id}`
- `GET /api/v1/chat/history`
- `DELETE /api/v1/chat/history`
- `POST /api/v1/chat/query`

## 开发注意事项

- 后端需先启动并允许前端来源访问，开发环境通常运行在 `http://localhost:8000`。
- 上传文件大小和格式限制由后端配置控制。
- 不要提交本地 `.env`、构建产物或包含敏感内容的测试文件。
