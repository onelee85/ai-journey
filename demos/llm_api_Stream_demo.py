import openai
import os
from dotenv import load_dotenv


load_dotenv()

client = openai.OpenAI(
    base_url=os.getenv("LM_STUDIO_API_BASE"),
    api_key=os.getenv("LM_STUDIO_API_KEY")
)
MODEL_LIST = [
    "qwen3.5-2b",
    "qwen3.5-4b",
]


def call_llm_stream(model_name, user_content):
    """
    调用不同模型的函数，支持流式输出

    Args:
        model_name: 模型名称
        user_content: 用户输入内容
    """
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=150,
            stream=True
        )
        print(f"模型 {model_name} 的Streaming输出：", end="", flush=True)
        full_response = ""

        for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content

        print("\n")
        print(f"完整回复：{full_response}")
        return full_response

    except openai.APIConnectionError as e:
        print(f"网络错误：连接失败 - {e}")
    except openai.AuthenticationError as e:
        print(f"认证错误：API密钥无效 - {e}")
    except openai.APIError as e:
        print(f"API错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")


def call_llm_streaming_with_timing(model_name, user_content):
    """
    带性能测试的Streaming输出

    Args:
        model_name: 模型名称
        user_content: 用户输入内容
    """
    import time

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=200,
            stream=True
        )

        print(f"模型 {model_name} 的Streaming输出：", end="", flush=True)
        full_response = ""
        first_token_time = None
        token_count = 0

        for chunk in response:
            if chunk.choices[0].delta.content:
                if first_token_time is None:
                    first_token_time = time.time()
                    ttft = first_token_time - start_time
                    print(f"\n[首Token延迟: {ttft:.3f}秒]", end="", flush=True)

                content = chunk.choices[0].delta.content
                print(content, end="", flush=True)
                full_response += content
                token_count += 1

        end_time = time.time()
        total_time = end_time - start_time
        tokens_per_second = token_count / total_time if total_time > 0 else 0

        print("\n")
        print(f"完整回复：{full_response}")
        print(f"性能指标:")
        print(f"  - 总耗时: {total_time:.3f}秒")
        print(f"  - 生成Token数: {token_count}")
        print(f"  - 速度: {tokens_per_second:.2f} tokens/秒")

        return full_response

    except openai.APIConnectionError as e:
        print(f"网络错误：连接失败 - {e}")
    except openai.AuthenticationError as e:
        print(f"认证错误：API密钥无效 - {e}")
    except openai.APIError as e:
        print(f"API错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")


if __name__ == "__main__":
    # 示例1: 基本Streaming输出
    print("\n" + "="*60)
    print("示例1: 基本Streaming输出")
    print("="*60)
    call_llm_stream("qwen3.5-4b", "什么是机器学习？")

    # 示例2: 带性能测试的Streaming输出
    print("\n" + "="*60)
    print("示例2: 带性能测试的Streaming输出")
    print("="*60)
    call_llm_streaming_with_timing("qwen3.5-2b", "解释一下什么是质数")
