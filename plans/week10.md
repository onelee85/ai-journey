# 第 10 周：PDF 知识库

## 本周学习目标
- 掌握 PDF 文件上传、存储和基础校验流程
- 学习 PDF 文本解析、清洗、切分和元数据提取方法
- 将 PDF 内容接入向量数据库，构建可检索知识库
- 实现基于 PDF 内容的 RAG 问答能力，并返回引用来源
- 构建简单 Web 界面，完成上传、索引、提问和答案展示流程
- 发布一个可运行的 PDF 知识库项目，并补齐 README 和使用说明

## 建议技术栈
- 后端：Python、FastAPI
- 文档解析：pypdf 或 pymupdf
- 文档切分：LangChain Text Splitter
- 向量数据库：Chroma、FAISS 或 Milvus
- Embedding：OpenAI Embeddings、Ollama Embeddings 或其他本地嵌入模型
- 前端：简单 HTML + JavaScript，或 Streamlit / Gradio
- LLM：OpenAI API、兼容 OpenAI API 的模型服务，或本地 Ollama 模型

## 详细学习任务步骤

### 第 1 天：PDF 上传

**学习目标**：完成 PDF 文件上传入口，为后续解析和知识库构建准备数据。

**学习内容**：
1. 文件上传接口的基本原理
2. FastAPI 中 `UploadFile` 的使用方法
3. 文件类型、大小和文件名校验
4. 上传文件的本地存储目录设计
5. 上传记录的数据结构设计

**实践任务**：
- 新建 PDF 知识库项目目录，规划 `api`、`services`、`data`、`vector_store` 等模块
- 实现 `POST /upload` 接口，支持上传单个 PDF 文件
- 增加文件校验：只允许 `.pdf` 文件，限制文件大小，避免空文件
- 将上传文件保存到本地目录，例如 `data/uploads`
- 为每个 PDF 生成唯一 `document_id`
- 返回上传结果：文件名、文件大小、`document_id`、保存路径
- 准备 2-3 个测试 PDF，用于后续解析和问答测试

**验收标准**：
- 可以通过接口或页面成功上传 PDF
- 非 PDF 文件会被拒绝，并返回清晰错误信息
- 上传后的文件能够在本地目录中找到
- 每个上传文件都有唯一 ID，后续接口可以用 ID 访问

### 第 2 天：文档解析

**学习目标**：解析 PDF 内容，并将内容清洗、切分成适合检索的文本块。

**学习内容**：
1. PDF 文本解析的常见方案：pypdf、pymupdf、pdfplumber
2. PDF 页码、标题、段落等元数据的提取方法
3. 文本清洗：去除多余空格、换行、页眉页脚
4. 文档切分策略：按字符、按 token、按段落递归切分
5. Chunk size 和 chunk overlap 对检索效果的影响

**实践任务**：
- 实现 PDF 解析服务，输入 `document_id`，输出每页文本内容
- 为每个文本片段保留元数据：文件名、页码、chunk 编号、`document_id`
- 使用递归文本切分器将 PDF 内容切分为多个 chunk
- 设置初始切分参数，例如 `chunk_size=800`、`chunk_overlap=120`
- 将解析后的 chunk 保存为 JSON 文件，方便调试和复用
- 输出解析统计信息：页数、chunk 数、总字符数、空页数量
- 对比至少 2 个不同 PDF 的解析效果，记录问题

**验收标准**：
- 可以从上传的 PDF 中提取可读文本
- 每个 chunk 都包含完整文本和必要元数据
- 空页、扫描版 PDF 或解析失败的页面有明确处理
- 能够通过日志或调试文件检查解析结果

### 第 3 天：RAG 问答

**学习目标**：将 PDF 文本写入向量数据库，并实现基于文档内容的问答流程。

**学习内容**：
1. PDF 知识库的索引构建流程
2. Embedding 模型调用和批量向量化
3. 向量数据库 collection / index 的设计
4. RAG 问答链路：问题向量化、相似度检索、上下文拼接、LLM 回答
5. 答案引用来源的设计：文件名、页码、文本片段

**实践任务**：
- 实现 `POST /documents/{document_id}/index` 接口，将 PDF chunk 写入向量数据库
- 为每个 chunk 生成 embedding，并保存文本和元数据
- 实现 `POST /chat` 或 `POST /ask` 接口，支持基于某个 PDF 或全部 PDF 提问
- 设置检索参数，例如 `top_k=4`
- 设计 RAG Prompt，要求模型只基于检索内容回答，不知道时明确说明
- 在回答中返回引用来源，例如页码和 chunk 摘要
- 测试 8-10 个问题，覆盖事实型问题、总结型问题和文档外问题

**验收标准**：
- 上传并解析后的 PDF 可以成功入库
- 用户提问后可以检索到相关 chunk
- 回答内容与 PDF 原文相关，不明显编造
- 每个回答至少返回 1 个可追溯来源
- 文档外问题能够得到合理拒答或说明

### 第 4 天：简单 Web 界面

**学习目标**：构建可用的前端界面，将上传、索引和问答流程串起来。

**学习内容**：
1. PDF 知识库的基础用户流程设计
2. 文件上传组件和进度反馈
3. 文档列表、索引状态和问答输入框设计
4. RAG 答案和引用来源的展示方式
5. 前端错误状态和加载状态处理

**实践任务**：
- 创建简单 Web 页面或 Streamlit / Gradio 页面
- 实现 PDF 上传入口，上传成功后显示文件名和 `document_id`
- 增加“解析并入库”按钮，触发后端索引流程
- 显示文档列表和每个文档的状态：已上传、已解析、已入库、失败
- 实现问答输入框和提交按钮
- 展示模型回答、引用页码、来源 chunk 文本摘要
- 增加基础错误提示，例如上传失败、索引失败、模型调用失败

**验收标准**：
- 不依赖命令行也能完成上传、入库和提问
- 页面状态清晰，用户知道当前文档是否可问答
- 回答区域能清楚展示答案和引用来源
- 常见失败场景有可读的错误提示

### 第 5 天：发布知识库项目

**学习目标**：整理项目代码、文档和演示材料，完成可复现的项目发布。

**学习内容**：
1. 项目结构整理和配置管理
2. 环境变量和密钥管理
3. README 编写方法
4. 本地运行、测试和演示流程
5. GitHub 提交和项目复盘

**实践任务**：
- 整理项目目录，拆分上传、解析、索引、问答、Web UI 等模块
- 编写 `.env.example`，说明需要配置的模型、Embedding 和向量库参数
- 编写 README，包含项目介绍、功能列表、安装步骤、运行命令、接口说明和截图
- 增加最小可用测试：上传接口、解析函数、问答接口的基础测试
- 准备一个演示 PDF 和 5 个示例问题
- 完成本地完整流程验证：上传 PDF -> 解析 -> 入库 -> 提问 -> 返回引用
- 提交 GitHub，并在学习笔记中总结本周收获和遇到的问题

**验收标准**：
- 新环境可以按照 README 跑起项目
- 项目至少支持一个 PDF 的完整知识库问答流程
- README 清楚说明如何配置 API Key 或本地模型
- GitHub 提交记录完整，代码结构清晰
- 有一份本周复盘，记录问题、解决方案和下一步优化方向

## 项目功能清单
- PDF 上传和文件校验
- PDF 文本解析和页码元数据提取
- 文本清洗和 chunk 切分
- Embedding 生成和向量数据库写入
- 基于 PDF 的 RAG 问答
- 答案引用来源展示
- 简单 Web 界面
- README、环境配置示例和演示问题

## 学习资源推荐
- [FastAPI 文件上传文档](https://fastapi.tiangolo.com/tutorial/request-files/)
- [LangChain Document Loaders](https://python.langchain.com/docs/integrations/document_loaders/)
- [LangChain Text Splitters](https://python.langchain.com/docs/concepts/text_splitters/)
- [Chroma 官方文档](https://docs.trychroma.com/)
- [PyMuPDF 官方文档](https://pymupdf.readthedocs.io/)
- [pypdf 官方文档](https://pypdf.readthedocs.io/)

## 本周总结
- 完成一个可以真实上传 PDF 并基于 PDF 内容问答的知识库项目
- 理解从原始 PDF 到 RAG 问答的完整工程链路
- 掌握文档解析、chunk 切分、向量入库、检索和引用返回的关键细节
- 为第 11 周 RAG 优化做好基础，包括 chunk 策略、metadata 过滤、评测集和质量指标
