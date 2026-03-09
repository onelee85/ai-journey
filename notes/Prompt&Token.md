# Prompt & Token

## Token的定义和工作原理

### 什么是Token？
Token是大型语言模型(LLM)中处理文本的基本单位。它不是简单的字符或单词，而是文本的一种分割方式，由模型的分词器(tokenizer)决定。

### Token的工作原理
1. **分词过程**：当文本输入到LLM时，首先会被分词器分解成一系列Token。
2. **Token ID**：每个Token都被映射到一个唯一的ID，这个ID在模型的词汇表中对应一个向量表示。
3. **模型处理**：LLM通过处理这些Token ID来理解和生成文本。
4. **生成过程**：模型生成文本时，会先生成Token ID，然后再转换回可读的文本。

### Token的特点
- **英文Token**：通常是单词或单词的一部分，例如"hello"可能是一个Token，"unbelievable"可能被分解为"un"、"believable"等。
- **中文Token**：通常是单个汉字或词语，因为中文没有明确的词边界。
- **Token长度**：不同的模型有不同的Token长度限制，例如GPT-3.5是4096个Token，GPT-4是8192个Token（长上下文版本可达32768个）。

### Token计算示例

| 文本 | Token数量 | 说明 |
|------|-----------|------|
| "Hello" | 1 | 单个英文单词 |
| "Hello world" | 2 | 两个英文单词 |
| "你好" | 2 | 两个中文字符 |
| "机器学习" | 2 | 两个中文词语 |
| "I'm happy" | 3 | "I", "'m", "happy" |

![Token分词示例](https://i.imgur.com/example_tokenization.png)

## Prompt的定义和工作原理

### 什么是Prompt？
Prompt是用户输入给LLM的文本指令，用于引导模型生成特定的输出。它是用户与LLM交互的桥梁。

### Prompt的工作原理
1. **输入处理**：Prompt被分词器分解成Token，然后输入到模型中。
2. **上下文理解**：模型根据Prompt中的上下文信息理解用户的意图。
3. **输出生成**：模型基于理解生成相关的响应。
4. **Token限制**：Prompt和生成的输出总和不能超过模型的Token长度限制。

### Prompt的基本结构
一个有效的Prompt通常包含以下部分：
1. **指令**：明确告诉模型要做什么。
2. **上下文**：提供相关的背景信息。
3. **输入数据**：需要模型处理的数据。
4. **输出格式**：指定期望的输出格式。

### Prompt的类型

| 类型 | 描述 | 示例 |
|------|------|------|
| 零样本(Zero-shot) | 不提供示例，直接让模型完成任务 | "将以下中文翻译成英文：你好世界" |
| 少样本(Few-shot) | 提供少量示例，帮助模型理解任务 | "翻译示例：中文：你好 英文：Hello|
| 思维链(Chain-of-thought) | 引导模型逐步思考，适合复杂问题 | "我有10个苹果，吃了3个，又买了5个，现在有几个？请逐步思考：1. 初始有10个苹果2. 吃了3个后，剩下10-3=7个3. 又买了5个，现在有7+5=12个4. 所以答案是12个" |
| 指令型(Instruction) | 明确给出任务指令 | "请总结以下文章的主要内容，不超过100字：[文章内容]" |
| 对话型(Conversation) | 模拟对话场景 | "用户：你好，你是谁？助手：我是一个AI助手，有什么可以帮助你的吗？用户：[用户问题]" |

![Prompt类型示例](https://i.imgur.com/example_prompt_types.png)

## 相关权威文档链接

### Token相关
- [OpenAI Tokenizer](https://platform.openai.com/tokenizer) - OpenAI官方的Token计算器
- [OpenAI API文档 - Token使用](https://platform.openai.com/docs/guides/text-generation/managing-tokens) - 关于Token使用的官方指南
- [Hugging Face Tokenizers库](https://huggingface.co/docs/tokenizers/index) - 流行的Tokenization库

### Prompt相关
- [OpenAI Prompt工程指南](https://platform.openai.com/docs/guides/prompt-engineering) - OpenAI官方的Prompt工程指南
- [LangChain Prompt模板文档](https://python.langchain.com/docs/modules/model_io/prompts/) - LangChain的Prompt模板使用指南
- [Prompt Engineering Guide](https://www.promptingguide.ai/) - 全面的Prompt工程指南
- [Google Prompt Engineering for Developers](https://developers.google.com/machine-learning/problem-solving/prompt-engineering) - Google的开发者Prompt工程指南

## 最佳实践

### Token使用最佳实践
- **控制Token长度**：确保输入和输出的Token总数不超过模型限制
- **优化输入**：精简输入内容，去除无关信息
- **监控Token使用**：使用Token计算器预估API调用成本

### Prompt设计最佳实践
- **明确指令**：使用清晰、具体的指令
- **提供上下文**：根据需要提供足够的背景信息
- **使用格式**：为复杂任务指定输出格式
- **少样本学习**：对于复杂任务，提供少量高质量示例
- **迭代优化**：根据模型反馈不断调整Prompt

## 常见问题

### Token相关
- **Token计算**：使用OpenAI的Token计算器或Hugging Face的tokenizers库来计算Token数量
- **Token限制**：不同模型有不同的Token限制，使用前需了解
- **Token成本**：API调用通常按Token数量收费，需注意控制使用量

### Prompt相关
- **Prompt长度**：过长的Prompt会占用更多Token，减少可用于输出的空间
- **Prompt质量**：高质量的Prompt能显著提高模型输出质量
- **模型特定性**：不同模型对Prompt的响应可能不同，需要针对特定模型调整