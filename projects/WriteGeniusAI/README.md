# WriteGeniusAI - AI写作助手

一个功能完整的AI写作助手，支持多种写作风格，提供Web界面，并成功发布项目。

## 🎯 项目目标

构建一个功能完整的AI写作助手，支持多种写作风格，提供Web界面，并成功发布项目。

## 📋 功能特性

- **多种写作风格**：支持学术、商务、创意、技术、故事五种风格
- **智能文章生成**：根据主题自动生成文章标题和内容
- **自定义长度**：支持短篇、中篇、长篇三种文章长度
- **实时流式输出**：生成过程实时展示，提升用户体验
- **用户友好界面**：美观易用的Web界面，支持参数调整

## 🛠 技术栈

- **后端**：Python + FastAPI
- **前端**：HTML + CSS + JavaScript + Jinja2
- **AI模型**：OpenAI API (GPT-3.5-turbo)
- **依赖管理**：pip

## 📁 项目结构

```
WriteGeniusAI/
├── app.py              # FastAPI应用入口
├── requirements.txt    # 依赖包列表
├── .env                # 环境变量配置
├── src/                # 源代码目录
│   ├── config.py       # 配置管理
│   ├── openai_client.py # OpenAI API客户端
│   ├── article_generator.py # 文章生成器
│   └── style_manager.py # 风格管理器
├── frontend/           # 前端目录
│   └── templates/      # 模板文件
│       └── index.html  # 主页面
└── tests/              # 测试目录
    └── test_article_generator.py # 测试文件
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <项目地址>
cd WriteGeniusAI

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `.env` 文件，填入你的OpenAI API密钥：

```
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# System Configuration
APP_NAME=WriteGeniusAI
APP_VERSION=1.0.0
DEBUG=True

# API Configuration
API_TIMEOUT=30
API_RETRY_COUNT=3
```

### 3. 启动应用

```bash
# 启动开发服务器
python app.py

# 或使用uvicorn
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. 访问应用

打开浏览器，访问 `http://localhost:8000` 即可使用AI写作助手。

## 📚 使用指南

1. **输入主题**：在「文章主题」输入框中输入你想要生成的文章主题
2. **选择风格**：从「写作风格」下拉菜单中选择适合的写作风格
3. **选择长度**：从「文章长度」下拉菜单中选择文章长度
4. **输入标题**：（可选）在「文章标题」输入框中输入自定义标题，不填写则系统自动生成
5. **生成文章**：点击「生成文章」按钮，等待生成完成
6. **查看结果**：生成完成后，在页面下方查看生成的文章

## 🎨 支持的写作风格

- **学术风格**：正式、严谨、逻辑清晰的学术写作风格
- **商务风格**：专业、简洁、目标明确的商务写作风格
- **创意风格**：富有想象力、生动形象的创意写作风格
- **技术风格**：准确、详细、专业的技术写作风格
- **故事风格**：生动、感人、有情节的故事写作风格

## 🔧 API接口

### POST /generate

生成文章（非流式）

**请求体**：
```json
{
  "topic": "文章主题",
  "style": "写作风格",
  "length": "文章长度",
  "title": "文章标题（可选）"
}
```

**响应**：
```json
{
  "title": "生成的标题",
  "content": "生成的内容"
}
```

### POST /stream

流式生成文章

**请求体**：
```json
{
  "topic": "文章主题",
  "style": "写作风格",
  "length": "文章长度",
  "title": "文章标题（可选）"
}
```

**响应**：
```json
{
  "title": "生成的标题",
  "content": "生成的内容"
}
```

## 🧪 运行测试

```bash
# 运行测试
pytest tests/test_article_generator.py
```

## 📝 项目文档

- **技术文档**：详见代码注释
- **API文档**：启动应用后访问 `http://localhost:8000/docs`

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [OpenAI API](https://platform.openai.com/docs/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Jinja2](https://jinja.palletsprojects.com/)

---

**WriteGeniusAI** - 让写作变得更简单！