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

# 调用不同模型的函数


def llm(model_name, prompt):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
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


def llm_json_schema(model_name, prompt, schema):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150,
            response_format={"type": "json_schema", "json_schema": schema}
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
