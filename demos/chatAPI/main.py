from fastapi import FastAPI
import openai
import os
from dotenv import load_dotenv

load_dotenv()


# 配置 LM Studio 本地 API 端点
openai.api_base = os.getenv("LM_STUDIO_API_BASE")  # LM Studio 默认端口
# LM Studio 使用 "lm-studio" 作为 API key
openai.api_key = os.getenv("LM_STUDIO_API_KEY")

# 创建客户端
client = openai.OpenAI(
    base_url=openai.api_base,
    api_key=openai.api_key
)


# 本地启动命令：cd /Users/lijiao/Documents/AI/ai-journey && .venv/bin/python -m uvicorn main:app --reload --app-dir demos/chatAPI


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


@app.get("/")
def read_root():
    return {
        "Hello": "Chat",
        "version": "1.0.0",
        "models_count": len(ALL_MODELS),
        "endpoints": {
            "/models": "获取所有模型列表",
            "/models/grouped": "按类型分组的模型列表",
            "/models/{model_id}": "获取模型详情",
            "/chat": "聊天接口"
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
def chat(model_name: str, message: str):
    """
    聊天接口

    - **model_name**: 模型名称
    - **message**: 用户消息
    """
    # 添加请求验证
    if not model_name or not message:
        return {"error": "模型名称和消息不能为空"}
    messages = [{"role": "user", "content": message}]
    # 模型名称是否在列表中
    if model_name not in [model["id"] for model in ALL_MODELS]:
        return {"error": f"模型 {model_name} 不存在"}

    try:
        response = llm_function_call(model_name, messages)
        response_content = response.choices[0].message.content
        return {"message": response_content}
    except Exception as e:
        return {"error": str(e)}


def llm_function_call(model_name, messages, tools=None):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=300,
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
