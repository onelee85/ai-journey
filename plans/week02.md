# 第 2 周：Prompt 优化与外部 API

| 天数 | 任务               | 状态 |
| -- | ---------------- | -- |
| 1  | Prompt模板设计       |      |
| 2  | JSON结构化输出        |      |
| 3  | Function Calling |      |
| 4  | 接入外部API(天气)      |      |
| 5  | 优化Prompt并提交      |      |

## 详细任务说明

### Day 1: Prompt模板设计

**学习目标**
- 理解Prompt模板的概念和作用
- 学习如何设计可复用的Prompt模板
- 掌握不同场景下的Prompt模板设计模式

**任务清单**
- [ ] 学习PromptTemplate的概念和基本用法
  - 理解Prompt模板的作用和优势
  - 学习模板变量和占位符的概念
  - 掌握模板字符串的基本语法
- [ ] 设计3个不同场景的Prompt模板：
  - **文章摘要模板**：包含输入原文、指定摘要长度、输出格式要求
  - **代码解释模板**：包含代码片段、解释级别（初学者/进阶）、需要强调的重点
  - **问答对话模板**：包含上下文信息、问题描述、回答风格要求
- [ ] 实现模板参数化功能
  - 使用字符串格式化或模板引擎实现参数替换
  - 支持动态传入不同参数值
  - 处理缺失参数的默认情况
- [ ] 测试模板的灵活性和可复用性
  - 为每个模板准备2-3组测试数据
  - 验证参数替换的正确性
  - 评估模板的通用性和可复用性

**实现要求**
- 使用Python实现模板系统
- 代码应包含清晰的函数封装
- 每个模板应有对应的使用示例
- 添加错误处理机制

**参考资源**
- LangChain PromptTemplate文档
- OpenAI Prompt工程指南

---

### Day 2: JSON结构化输出

**学习目标**
- 学习如何引导模型输出JSON格式
- 掌握JSON Schema的设计
- 理解结构化输出的应用场景

**任务清单**
- [ ] 学习JSON结构化输出的基本方法
- [ ] 设计JSON Schema模板
- [ ] 实现3个不同的JSON输出场景：
  - 产品信息提取
  - 事件时间解析
  - 用户反馈分类
- [ ] 处理JSON解析错误
- [ ] 优化输出格式的准确性

**参考资源**
- OpenAI JSON模式文档
- LangChain Output Parsers

---

### Day 3: Function Calling

**学习目标**
- 理解Function Calling的工作原理
- 学习如何定义函数描述
- 掌握Function Calling的应用场景

**任务清单**
- [ ] 学习Function Calling的基本概念
- [ ] 设计3个不同的函数描述：
  - 天气查询函数
  - 计算器函数
  - 搜索函数
- [ ] 实现Function Calling调用流程
- [ ] 处理函数调用结果
- [ ] 测试不同场景下的Function Calling

**参考资源**
- OpenAI Function Calling文档
- LangChain Tools文档

---

### Day 4: 接入外部API(天气)

**学习目标**
- 学习如何结合LLM和外部API
- 掌握API调用的流程设计
- 理解工具调用的实际应用

**任务清单**
- [ ] 选择天气API（推荐OpenWeatherMap或和风天气）
- [ ] 注册API密钥并了解API文档
- [ ] 设计天气查询的Prompt和Function
- [ ] 实现完整的天气查询流程：
  - 用户输入解析
  - Function调用
  - API请求
  - 结果格式化
- [ ] 测试不同城市的天气查询

**参考资源**
- OpenWeatherMap API文档
- LangChain Tools文档

---

### Day 5: 优化Prompt并提交

**学习目标**
- 复习本周学习内容
- 优化已实现的功能
- 整理和提交代码

**任务清单**
- [ ] 代码重构和优化
- [ ] 添加错误处理和日志记录
- [ ] 编写项目文档：
  - README说明
  - 使用示例
  - API密钥配置说明
- [ ] 提交代码到GitHub
- [ ] 总结本周学习心得

**提交要求**
- 代码结构清晰
- 文档完整
- 示例可运行

---

## 学习资源汇总

### 官方文档
- [OpenAI Prompt工程指南](https://platform.openai.com/docs/guides/prompt-engineering)
- [OpenAI JSON模式](https://platform.openai.com/docs/guides/text-generation/json-mode)
- [OpenAI Function Calling](https://platform.openai.com/docs/guides/function-calling)

### 第三方资源
- [LangChain文档](https://python.langchain.com/)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

## 学习目标

- 掌握Prompt模板的设计方法
- 能够实现JSON结构化输出
- 理解并应用Function Calling
- 能够结合外部API实现完整功能
- 具备优化Prompt和代码的能力