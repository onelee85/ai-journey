import openai
import os
from dotenv import load_dotenv
import time

load_dotenv()

# ANSI 颜色代码


class Colors:
    RESET = "\033[0m"
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"
    RED = "\033[31m"


# 配置 LM Studio 本地 API 端点
openai.api_base = os.getenv("LM_STUDIO_API_BASE")  # LM Studio 默认端口
# LM Studio 使用 "lm-studio" 作为 API key
openai.api_key = os.getenv("LM_STUDIO_API_KEY")

# 创建客户端
client = openai.OpenAI(
    base_url=openai.api_base,
    api_key=openai.api_key
)

# 模型列表 - 支持多种模型
MODEL_LIST = [
    "qwen3.5-0.8b",
    "qwen3.5-2b",
    "qwen3.5-4b",
]


def get_available_models():
    """
    从服务器获取可用模型列表

    Returns:
        list: 可用模型列表
    """
    try:
        response = client.models.list()
        model_ids = [model.id for model in response.data]
        if model_ids:
            return model_ids
        else:
            print("服务器返回的可用模型列表为空")
            return MODEL_LIST
    except openai.APIError as e:
        print(f"获取可用模型列表失败：{e}")
        return MODEL_LIST


def call_llm(model_name, messages):
    """
    调用不同模型的函数

    Args:
        model_name: 模型名称
        messages: 消息列表，包含用户输入和系统提示
    """
    try:
        print(Colors.MAGENTA + "AI 正在思考..." + Colors.RESET, end="\r")
        start_time = time.time()
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=150
        )
        end_time = time.time()
        assistant_response = response.choices[0].message.content
        print(" " * 50)
        print(Colors.MAGENTA + f"[{model_name}] AI: " +
              Colors.WHITE + assistant_response)
        print(Colors.MAGENTA + f"耗时：{end_time - start_time:.2f}秒" +
              Colors.RESET)
        # 将AI的回复添加到消息列表中
        messages.append({"role": "assistant", "content": assistant_response})
        return response

    except openai.APIConnectionError as e:
        print(f"网络错误：连接失败 - {e}")
    except openai.AuthenticationError as e:
        print(f"认证错误：API密钥无效 - {e}")
    except openai.APIError as e:
        print(f"API错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")


def chat_client():
    """
    聊天客户端函数
    """

    print(Colors.CYAN + "=" * 50)
    print(Colors.CYAN + "欢迎使用 LLM 聊天客户端")
    print(Colors.CYAN + "=" * 50)
    # 获取可用模型列表
    available_models = get_available_models()
    # 打印可用模型列表
    print(Colors.GREEN + "可用模型：", ", ".join(available_models))
    print(Colors.YELLOW + "输入 /exit 退出")
    print(Colors.YELLOW + "输入 /models 查看可用模型列表")
    print(Colors.YELLOW + "输入 /model <模型名称> 切换模型")
    print(Colors.YELLOW + "输入 /reset 重置对话")
    print(Colors.CYAN + "\n" + "-" * 50)

    current_model = available_models[0]
    print(Colors.GREEN + f"当前模型：{current_model}")

    # 初始化消息列表
    messages = []

    while True:
        user_input = input(Colors.BLUE + ">：")
        if user_input == "/exit":
            break
        elif user_input == "/models":
            available_models = get_available_models()
            print(Colors.GREEN + "可用模型：", ", ".join(available_models))
            continue
        elif user_input.startswith("/model"):
            model_name = user_input.split(" ")[1]
            # 输入是否为空
            if not model_name.strip():
                print(Colors.RED + "请输入模型名称")
                continue
            if model_name in available_models:
                current_model = model_name
                print(Colors.GREEN + f"当前模型：{current_model}")
            else:
                print(Colors.RED + f"模型 {model_name} 不存在")
            continue
        elif user_input == "/reset":
            # 重置对话
            messages.clear()
            print(Colors.GREEN + "对话已重置")
            continue

        # 处理用户输入
        if not user_input.strip():
            print(Colors.RED + "请输入内容")
            continue

        # 将用户输入添加到消息列表中
        messages.append({"role": "user", "content": user_input})

        # 调用模型
        call_llm(current_model, messages)


if __name__ == "__main__":
    chat_client()
