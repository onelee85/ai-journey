from unittest import expectedFailure
from fastapi import FastAPI
import openai
import os
from dotenv import load_dotenv
from requests import sessions
import redis
import logging
import uuid
from token_utils import TokenLimiter, TokenCounter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

load_dotenv()
# 本地启动命令：cd /Users/lijiao/Documents/AI/ai-journey && .venv/bin/python -m uvicorn main:app --reload --app-dir demos/chatAPI

# 配置 LM Studio 本地 API 端点
openai.api_base = os.getenv("LM_STUDIO_API_BASE")  # LM Studio 默认端口
# LM Studio 使用 "lm-studio" 作为 API key
openai.api_key = os.getenv("LM_STUDIO_API_KEY")

# 创建客户端
client = openai.OpenAI(
    base_url=openai.api_base,
    api_key=openai.api_key
)


app = FastAPI(
    title="Chat API",
    description="AI 聊天 API 服务",
    version="1.0.0"
)

# OpenRouter 免费模型列表
# 来源: https://openrouter.ai/collections/free-models
OPENROUTER_FREE_MODELS = [
    {
        "id": "arcee-ai/trinity-large-preview:free",
        "name": "Trinity Large",
        "provider": "Arcee AI",
        "description": "擅长创意写作、角色扮演和实时语音助手",
        "context_window": "131K tokens",
        "type": "通用对话与创意写作"
    },
    {
        "id": "meta-llama/llama-3.3-70b-instruct:free",
        "name": "Llama 3.3 70B",
        "provider": "Meta",
        "description": "Meta 的 Llama 3.3 70B 模型，支持 8 种语言",
        "context_window": "128K tokens",
        "type": "通用对话与创意写作"
    },
    {
        "id": "stepfun/step-3.5-flash:free",
        "name": "Step 3.5 Flash",
        "provider": "Stepfun",
        "description": "MoE 架构，激活参数仅 11B，速度极快",
        "context_window": "128K tokens",
        "type": "深度推理与数学逻辑"
    },
    {
        "id": "qwen/qwen3-coder:free",
        "name": "Qwen3 Coder",
        "provider": "Alibaba",
        "description": "阿里通义千问编程专用模型",
        "context_window": "262K tokens",
        "type": "编程与代码生成"
    },
    {
        "id": "nvidia/nemotron-3-super-120b-a12b:free",
        "name": "Nemotron 3 Super",
        "provider": "NVIDIA",
        "description": "英伟达出品，262K 上下文窗口，多智能体应用",
        "context_window": "262K tokens",
        "type": "编程与代码生成"
    },
    {
        "id": "openrouter/hunter-alpha",
        "name": "Hunter Alpha",
        "provider": "OpenRouter",
        "description": "1M 上下文窗口，长程规划和复杂智能体任务",
        "context_window": "1M tokens",
        "type": "长文本处理"
    },
    {
        "id": "nvidia/nemotron-3-nano-9b-v2",
        "name": "Nemotron 3 Nano",
        "provider": "NVIDIA",
        "description": "轻量级模型，兼顾推理与通用任务",
        "context_window": "128K tokens",
        "type": "长文本处理"
    },
    {
        "id": "openrouter/healer-alpha",
        "name": "Healer Alpha",
        "provider": "OpenRouter",
        "description": "全模态模型，医疗影像、多媒体内容生成",
        "context_window": "262K tokens",
        "type": "多模态任务"
    },
    {
        "id": "nvidia/nemotron-nano-12b-v2-vl:free",
        "name": "Nemotron Nano 12B VL",
        "provider": "NVIDIA",
        "description": "12B 多模态模型，视频理解和文档智能",
        "context_window": "128K tokens",
        "type": "多模态任务"
    }
]

# 本地模型列表（LM Studio）
LOCAL_MODELS = [
    {
        "id": "qwen2.5",
        "name": "Qwen2.5",
        "provider": "Qwen",
        "description": "通义千问2.5 模型",
        "type": "通用对话"
    },
    {
        "id": "llama-3.2",
        "name": "Llama 3.2",
        "provider": "Meta",
        "description": "Llama 3.2 模型",
        "type": "通用对话"
    },
    {
        "id": "mistral",
        "name": "Mistral",
        "provider": "Mistral AI",
        "description": "Mistral 模型",
        "type": "通用对话"
    }
]

# 合并所有模型
ALL_MODELS = OPENROUTER_FREE_MODELS + LOCAL_MODELS


class HistoryStore:
    def __init__(self, use_redis: bool = False):
        self.use_redis = use_redis
        self.history = {}
        if use_redis:
            # redis 连接发送异常 则使用本地内存存储
            try:
                self.redis_client = redis.Redis(
                    host="localhost", port=6379, db=0)
                self.redis_client.ping()
            except Exception as e:
                self.redis_client = None
                self.use_redis = False
                self.memory_store = {}
                logger.error(f"Redis 连接失败：{str(e)}")
        else:
            self.memory_store = {}

    def save_history(self, session_id, history, max_length=50):
        '''
          保持最近的 max_length 条对话记录
        '''
        if len(history) > max_length:
            history = history[-max_length:]
        if self.use_redis:
            self.redis_client.set(
                f"chat:session:{session_id}", json.dumps(history))
        else:
            self.memory_store[session_id] = history

    def get_history(self, session_id):
        if self.use_redis:
            history = self.redis_client.get(
                f"chat:session:{session_id}")
            return json.loads(history) if history else []
        else:
            return self.memory_store.get(session_id, [])

    def clear_history(self, session_id):
        if self.use_redis:
            self.redis_client.delete(
                f"chat:session:{session_id}")
        else:
            if session_id in self.memory_store:
                self.memory_store.pop(session_id, None)


# 初始化历史存储对象
history_store = HistoryStore(use_redis=True)


@app.get("/")
def read_root():
    return {
        "Hello": "Chat",
        "version": "1.0.0",
        "models_count": len(ALL_MODELS),
        "storage": "Redis" if history_store.use_redis else "Memory",
        "endpoints": {
            "/models": "获取所有模型列表",
            "/models/grouped": "按类型分组的模型列表",
            "/models/{model_id}": "获取模型详情",
            "/chat": "聊天接口(支持多轮对话)",
            "/chat/clear": "清除对话历史",
            "/chat/history": "获取对话历史"
        }
    }


# 获取模型列表
@app.get("/models")
def get_models():
    """
    获取所有可用模型列表

    - **type**: 可选，按类型过滤模型
    """
    return {"models": ALL_MODELS}


# 获取模型列表（按类型分组）
@app.get("/models/grouped")
def get_models_grouped():
    """
    获取按类型分组的模型列表
    """
    grouped = {}
    for model in ALL_MODELS:
        model_type = model.get("type", "其他")
        if model_type not in grouped:
            grouped[model_type] = []
        grouped[model_type].append(model)
    return {"models": grouped}


# 获取模型详情
@app.get("/models/{model_id}")
def get_model(model_id: str):
    """
    获取指定模型的详细信息

    - **model_id**: 模型 ID
    """
    for model in ALL_MODELS:
        if model["id"] == model_id:
            return model
    return {"error": f"Model {model_id} not found"}


@app.post("/chat")
def chat(model_name: str, content: str, session_id: str = None):
    """
    聊天接口

    - **model_name**: 模型名称
    - **content**: 用户消息
    - **session_id**: 可选，会话 ID，用于保持对话历史
    """
    # 添加请求验证
    if not model_name or not content:
        return {"error": "模型名称和消息不能为空"}

    # 模型名称是否在列表中
    if model_name not in [model["id"] for model in ALL_MODELS]:
        return {"error": f"模型 {model_name} 不存在"}

    # 生成会话 ID
    if not session_id:
        session_id = str(uuid.uuid4())
    # 获取历史对话
    history = history_store.get_history(session_id)
    messages = {"role": "user", "content": content}
    history.append(messages)
    # 检查 token 数量
    counter = TokenCounter(model_name)
    limiter = TokenLimiter(max_input_tokens=100,
                           max_output_tokens=200, model_limit=128000)
    count_input_tokens = counter.count_messages(history)
    limiter.check_input(count_input_tokens)

    try:
        response = llm_function_call(model_name, history)
        logger.info(f"模型响应：{response}")

        # 尝试从content字段获取响应内容
        message = response.choices[0].message
        response_content = message.content

        # 如果content为None，尝试从reasoning字段获取
        if response_content is None:
            response_content = message.reasoning

        # 确保有响应内容
        if response_content is None:
            response_content = "抱歉，未能生成响应"

        output_tokens = counter.count_tokens(response_content)
        limiter.check_total(count_input_tokens, output_tokens)
        # 添加助手回复
        history.append({"role": "assistant", "content": response_content})
        # 保存历史对话
        history_store.save_history(session_id, history)
        return {"message": response_content,
                "session_id": session_id,
                "history_length": len(history),
                "usage": {
                    "input_tokens": count_input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": count_input_tokens + output_tokens
                }
                }
    except Exception as e:
        return {"error": str(e)}


def get_chat_history(session_id: str):
    """
    获取指定会话的对话历史

    - **session_id**: 会话 ID
    """
    if not session_id:
        return {"error": "会话 ID 不能为空"}
    history = history_store.get_history(session_id)
    return {"history": history, "history_length": len(history)}


@app.post("/chat/clear")
def clear_history(session_id: str):
    """
    清除指定会话的对话历史

    - **session_id**: 会话 ID
    """
    history_store.clear_history(session_id)
    return {"message": f"会话 {session_id} 的历史记录已清除"}


@app.post("/chat/history")
def get_history(session_id: str):
    """
    获取指定会话的对话历史

    - **model_name**: 模型名称
    - **session_id**: 会话 ID
    """
    return {"history": history_store.get_history(session_id)}


def llm_function_call(model_name, messages, tools=None):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1024*4,
            tools=tools
        )
        return response

    except openai.APIConnectionError as e:
        print(f"网络错误：连接失败 - {e}")
    except openai.AuthenticationError as e:
        print(f"认证错误：API密钥无效 - {e}")
    except openai.APIError as e:
        print(f"API错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")
