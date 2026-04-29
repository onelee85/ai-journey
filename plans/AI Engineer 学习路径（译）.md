# AI Engineer 学习路径（译）

原文链接：https://waytoagi.feishu.cn/wiki/LCSHw5fXqi0UbIkfFXec4H7OnQc

> 原帖链接：https://x.com/ParasVerma7454/status/2048366074169835559

![image.png](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/HReYbpXB6oZeKRxb7iAcLXXYnWh/?fallback_source=1&height=1280&mount_node_token=Ci9PdoRpUo1ijtxag1pcIpp7nJe&mount_point=docx_image&policy=equal&width=1280)

这是一份非常实用的路线图，告诉你该学什么、按什么顺序学，它基于大约 2000 份真实岗位描述中的需求总结而来。

如果你想进入 AI engineering，而不只是停留在 ML 理论层面，这条路径更贴近生产环境中的真实系统构建方式。

---

## 核心部分：20% 的技能，驱动 80% 的工作

这是大多数人最容易搞错的地方。

AI engineering 的重点，不是从零训练模型，而是围绕 LLM 去构建系统。

1. LLM 基础

先从这里开始，其他内容都建立在这之上。

![image.png](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/YEzibSInqoRUK8xmjv3cAiL3nhn/?fallback_source=1&height=1280&mount_node_token=L8G3dLFl8oxNrpxGxMvc8HvhnjS&mount_point=docx_image&policy=equal&width=1280)

- 从高层理解 LLM 是如何工作的
- 理解它擅长什么、又会在哪些地方失效
- 学会使用 OpenAI、Anthropic 这类 API
- 理解 structured outputs，比如 JSON、schema、tool responses
- 学会针对不同任务做 prompt engineering

目标：从“和模型聊天”升级为“可预测地控制模型”。

2. RAG（Retrieval-Augmented Generation）

这是大多数真实 AI 系统的骨架。

![image.png](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/L360bqV62ooJcwxWrB9coRabnVb/?fallback_source=1&height=1280&mount_node_token=J7P6dihBzo8ofKxcaEkcBzOBnDf&mount_point=docx_image&policy=equal&width=1280)

- 把自定义数据注入 LLM
- 理解 vector search 和 semantic retrieval
- 熟悉 Elasticsearch、Qdrant 这类工具
- 掌握 chunking 策略，这件事比很多人想象中更重要
- 处理真实数据源：PDF、网页、transcript

实践项目：

- FAQ 助手
- 文档问答系统
- 内部知识检索

3. AI Agents

这里开始变得有趣，同时也会开始变乱。

![image.png](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/ODMXbUfJOovDl1xOf9CcsqKnnIe/?fallback_source=1&height=1280&mount_node_token=WaiHdr7UeoQaDfxc0sFcUYMLnrV&mount_point=docx_image&policy=equal&width=1280)

- Tool calling，也就是让 LLM 不只是回答，还能执行动作
- Agent loop：think → act → observe → repeat
- 相关框架：LangChain、PydanticAI、OpenAI Agents SDK、Google ADK
- Model Context Protocol（MCP）
- Multi-agent systems，包括 routing、coordination 和 pipelines

实践项目：

- Web research agent
- 数据抽取流水线
- Multi-agent workflow

4. AI 系统测试

这部分容易被低估，但非常关键。

- 测试工具调用和输出结果
- 评估一致性
- 使用 LLM-as-a-judge 的方式做评测，是的，很 meta，但确实有用

目标：让 AI 系统变得可靠，而不只是看起来惊艳。

5. Monitoring 与 Observability

如果你看不到系统正在做什么，你就没法真正修好它。

![image.png](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/DBgMbNm2Aoxms4xGiWocXqZRnDb/?fallback_source=1&height=1280&mount_node_token=YgRwdin0hotG6mxaqmVcykUgnWe&mount_point=docx_image&policy=equal&width=1280)

- Tracing agent workflows
- 记录交互日志
- 跟踪成本
- 建立 feedback loops
- 做 dashboards，比如 Grafana、OpenTelemetry

真实世界里的意义：

这正是 demo 和 production system 之间的分水岭。

6. Evaluation

大多数工程师都会跳过这一步，而结果也往往很明显。

![image.png](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/WRFDb8isQotflExbNnCcAqcvn5g/?fallback_source=1&height=1280&mount_node_token=Vfwfd8r7YozKghxNGFHctVTUnoM&mount_point=docx_image&policy=equal&width=1280)

- 离线评测数据集
- 衡量 retrieval quality
- 合成数据生成
- 基于结果迭代优化 prompt

目标：从“感觉还不错”走向“可以被量化衡量”。

7. Production Systems

从这里开始，AI engineer 才真正具备高价值。

![image.png](https://internal-api-drive-stream.feishu.cn/space/api/box/stream/download/v2/cover/UmQOb0HzgoL4n0xuNbvcZ7oynkc/?fallback_source=1&height=1280&mount_node_token=JAD8djLeFoC36sxZ4GBcvziMnQh&mount_point=docx_image&policy=equal&width=1280)

- 把 notebook 变成真正的服务
- 部署能力，比如 Streamlit 用于快速原型
- 云平台：AWS / GCP / Azure
- Guardrails 和安全层
- 面向规模的并行处理

---

## 支撑技能：岗位描述里真正反复出现的部分

这些不是可选项，而是几乎到处都会出现。

### Python 与工程基础

- Python，大约出现在 80%+ 的岗位里
- Testing、CI/CD、code quality
- Git workflows

### Web 开发能力

这是构建真实产品所需的能力。

- FastAPI，AI 应用里非常常见的后端标准
- React / Next.js，前端层
- APIs：REST / GraphQL

### 云与基础设施

- 至少熟悉一个：AWS、GCP 或 Azure
- Docker，几乎是必选项
- Kubernetes，用于规模化
- Terraform，infra as code

### 数据库

- PostgreSQL，默认优先选择
- Vector DBs：Pinecone、Weaviate、Qdrant、pgvector
- Redis，用于缓存和 session

### ML 基础

你不需要成为 researcher，但你必须有足够的上下文理解。

- PyTorch 基础
- Embeddings，这部分非常重要
- Fine-tuning，在 API 不够用时会派上用场
- Model evaluation 基础

### 数据工程

- ETL pipelines
- Airflow、Spark、Kafka
- Databricks、Snowflake 这类工具

### Python 之外的语言

- TypeScript，对于 full-stack AI 非常重要
- SQL，真实数据工作里几乎是必修课
- Java / Go，偏重后端的岗位里会更常见

---

## 典型的 AI Engineering 技术栈

一个现代 AI 系统，通常会长成这样：

- Frontend：React / Next.js
- Backend：FastAPI
- AI orchestration：LangChain、LangGraph、PydanticAI
- LLMs：OpenAI、Anthropic、Groq、本地模型
- Vector DB：Pinecone / Weaviate / Qdrant
- Infra：Docker + Kubernetes + Cloud
- Monitoring：OpenTelemetry、Grafana
- Evaluation：LLM judges，以及 Evidently 这类工具

---

## 技能优先级：如果你的时间有限

Must-Have

- Python
- Prompt engineering
- RAG systems
- 一种云平台
- Docker

High-Value

- LangChain 或 PydanticAI
- FastAPI
- TypeScript
- CI/CD
- Kubernetes
- PyTorch 基础

Differentiators（能更快帮你拿到机会的东西）

- Agent frameworks，比如 LangGraph、CrewAI
- Fine-tuning 模型
- Evaluation systems
- Vector databases
- Multi-agent architectures

---

## 最后的判断

AI engineering 并不是追逐最新 hype 工具。

它的本质，是构建可靠的系统，而 LLM 只是其中的一个组件。

如果你把重点放在：

- RAG
- Agents
- Evaluation
- Production systems

你就已经会领先大多数候选人。

## Credit

这份路线图大量借鉴了 Alexey Grigorev 的原始工作：

https://github.com/alexeygrigorev/ai-engineering-field-guide
