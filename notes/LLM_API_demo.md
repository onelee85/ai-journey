
## Demo 文件说明

### 1. llm_api_demo.py

使用 OpenAI SDK 直接调用 LLM API 的示例，包含：
- 基本API调用
- 流式API调用
- 调用不同模型
- 高级API调用（带系统提示和参数）
- 错误处理

### 2. LLM_API_Stream_demo.py

专门用于演示流式输出功能的示例，包含：
- 基本流式输出实现
- 实时响应展示
- 错误处理机制
- 交互式聊天功能

运行：
```bash
pip3 install -r requirements.txt

# 配置 API_BASE 和 API_KEY
copy .env.example .env

# 运行基本API调用示例
python llm_api_demo.py

# 运行流式输出示例
python LLM_API_Stream_demo.py
```

## 学习要点

### API 密钥设置
- 使用环境变量存储 API 密钥，避免硬编码
- 使用 `.env` 文件管理配置（记得添加到 `.gitignore`）
- 使用 `python-dotenv` 库加载环境变量

### 基本API调用
- 创建 OpenAI 客户端实例
- 使用 `chat.completions.create()` 方法
- 设置 messages、model、temperature 等
- 参数 temperature、top_p、presence_penalty 的含义
  - temperature（0-2）：控制输出随机性，越高越随机
  - top_p（0-1）：控制多样性，越高越随机
  - presence_penalty（0-1）：控制存在惩罚，越高越鼓励新话题

### 错误处理
- 使用 try-except 捕获异常
- 处理网络错误、API错误、认证错误等
- 提供友好的错误提示

### 不同模型调用
- 支持多种模型：qwen3.5-2b, qwen3.5-4b
- 根据需求选择合适的模型
- 注意不同模型的成本和性能差异

### 流式响应
- 设置 `stream=True` 参数
- 逐块接收和处理响应
- **基本实现**：设置 `stream=True` 参数启用流式输出
- **逐块处理**：使用 for 循环逐块接收和处理响应
- **实时展示**：通过 `print(content, end="", flush=True)` 实现实时输出

## 常见问题

### API 密钥无效
- 检查 `.env` 文件中的密钥是否正确
- 确认密钥是否已激活且有余额

### 网络连接问题
- 检查网络连接
- 如果使用代理，需要配置代理设置

### 模型不可用
- 检查模型名称是否正确
- 确认账户是否有该模型的使用权限