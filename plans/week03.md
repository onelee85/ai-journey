# 第 3 周：API 服务构建

| 天数 | 任务         | 状态 |
| -- | ---------- | -- |
| 1  | 学习FastAPI  |      |
| 2  | 构建/chat接口  |      |
| 3  | 多轮对话上下文    |      |
| 4  | Token统计功能  |      |
| 5  | 提交AI API服务 |      |

## 详细任务说明

### Day 1: 学习FastAPI

**学习目标**
- 理解FastAPI的核心概念和优势
- 学习路由、请求和响应的基本用法
- 掌握FastAPI的异步处理能力

**任务清单**
- [ ] 安装FastAPI和uvicorn
- [ ] 学习FastAPI基础概念：
  - 路由（Routes）
  - 请求方法（GET, POST, PUT, DELETE）
  - 请求体（Request Body）
  - 响应模型（Response Model）
- [ ] 创建第一个FastAPI应用
- [ ] 实现基本的CRUD接口
- [ ] 学习FastAPI自动文档生成（/docs）

**参考资源**
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [FastAPI中文文档](https://fastapi.tiangolo.com/zh/)

---

### Day 2: 构建/chat接口

**学习目标**
- 理解聊天API的设计模式
- 掌握如何集成LLM API到FastAPI
- 学习错误处理和异常管理

**任务清单**
- [ ] 设计/chat接口的数据结构：
  - 请求参数（messages, model, temperature等）
  - 响应格式（content, usage等）
- [ ] 实现/chat接口：
  - 接收用户消息
  - 调用LLM API
  - 返回响应结果
- [ ] 添加请求验证
- [ ] 实现错误处理
- [ ] 测试接口功能

**参考资源**
- OpenAI API文档
- FastAPI请求体文档

---

### Day 3: 多轮对话上下文

**学习目标**
- 理解多轮对话的实现原理
- 掌握对话历史的管理方法
- 学习会话ID和用户ID的设计

**任务清单**
- [ ] 设计对话历史存储方案：
  - 内存存储（简单场景）
  - Redis存储（生产环境）
- [ ] 实现会话管理：
  - 生成唯一会话ID
  - 存储和检索对话历史
  - 限制对话历史长度
- [ ] 修改/chat接口支持多轮对话
- [ ] 实现对话清除功能
- [ ] 测试多轮对话场景

**参考资源**
- OpenAI多轮对话文档
- FastAPI Cookie和Header文档

---

### Day 4: Token统计功能

**学习目标**
- 理解Token统计的重要性
- 掌握Token计算方法
- 学习如何限制输入和输出长度

**任务清单**
- [ ] 学习Token计算方法：
  - 使用tiktoken库
  - 使用tokenizer API
- [ ] 实现Token统计功能：
  - 统计输入Token数量
  - 统计输出Token数量
  - 统计总Token数量
- [ ] 添加Token限制检查：
  - 最大输入长度
  - 最大输出长度
  - 模型Token限制
- [ ] 在响应中返回Token使用情况
- [ ] 测试不同长度的输入输出

**参考资源**
- tiktoken官方文档
- OpenAI Token使用指南

---

### Day 5: 提交AI API服务

**学习目标**
- 复习本周学习内容
- 优化已实现的功能
- 整理和提交代码

**任务清单**
- [ ] 代码重构和优化：
  - 代码结构整理
  - 错误处理完善
  - 日志记录添加
- [ ] 添加配置管理：
  - 环境变量配置
  - API密钥管理
  - 模型配置
- [ ] 编写项目文档：
  - README说明
  - API接口文档
  - 部署说明
- [ ] 提交代码到GitHub
- [ ] 总结本周学习心得

**提交要求**
- 代码结构清晰
- 文档完整
- 支持多轮对话
- Token统计准确

---

## 学习资源汇总

### 官方文档
- [FastAPI官方文档](https://fastapi.tiangolo.com/)
- [OpenAI API文档](https://platform.openai.com/docs/)

### 第三方资源
- [FastAPI中文文档](https://fastapi.tiangolo.com/zh/)
- [tiktoken GitHub](https://github.com/openai/tiktoken)

---

## 学习目标

- 掌握FastAPI的基础用法
- 能够构建完整的聊天API服务
- 实现多轮对话功能
- 添加Token统计功能
- 具备API服务部署能力