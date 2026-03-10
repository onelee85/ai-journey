# 简单的 编写基本的API调用代码，调用本地 LM Studio 的 qwen3.5-4b 模型

import os
from dotenv import load_dotenv

load_dotenv()

import openai

# 配置 LM Studio 本地 API 端点
openai.api_base = os.getenv("LM_STUDIO_API_BASE")  # LM Studio 默认端口
openai.api_key = os.getenv("LM_STUDIO_API_KEY")  # LM Studio 使用 "lm-studio" 作为 API key

# 创建客户端
client = openai.OpenAI(
    base_url=openai.api_base,
    api_key=openai.api_key
)

# 模型列表 - 支持多种模型
MODEL_LIST = [
    "qwen3.5-2b",
    "qwen3.5-4b",        
]

def call_llm(model_name, user_content):
    """
    调用不同模型的函数
    
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
            max_tokens=150
        )
        print(f"模型 {model_name} 回复：", response.choices[0].message.content)
        return response
    
    except openai.APIConnectionError as e:
        print(f"网络错误：连接失败 - {e}")
    except openai.AuthenticationError as e:
        print(f"认证错误：API密钥无效 - {e}")
    except openai.APIError as e:
        print(f"API错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")


def call_llm_advanced(model_name, user_content, system_prompt=None, temperature=0.7, 
                      max_tokens=150, top_p=1.0, frequency_penalty=0.0, presence_penalty=0.0):
    """
    高级API调用函数，支持更多参数配置
    
    Args:
        model_name: 模型名称
        user_content: 用户输入内容
        system_prompt: 系统提示（可选），用于设定模型角色和行为
        temperature: 温度参数（0-2），控制输出随机性，越高越随机
        max_tokens: 最大生成token数
        top_p: 核采样参数，控制多样性
        frequency_penalty: 频率惩罚，减少重复
        presence_penalty: 存在惩罚，鼓励新话题
    """
    messages = []
    
    # 添加系统提示
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    # 添加用户消息
    messages.append({"role": "user", "content": user_content})
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stream=False  # 可设置为True实现流式输出
        )
        print(f"\n【高级调用】模型 {model_name} 回复：", response.choices[0].message.content)
        
        # 显示使用详情
        print(f"   - Token使用: 输入 {response.usage.prompt_tokens} + 输出 {response.usage.completion_tokens} = 总计 {response.usage.total_tokens}")
        print(f"   - 参数配置: temp={temperature}, max_tokens={max_tokens}, top_p={top_p}")
        
        return response
    
    except openai.APIConnectionError as e:
        print(f"网络错误：连接失败 - {e}")
    except openai.AuthenticationError as e:
        print(f"认证错误：API密钥无效 - {e}")
    except openai.APIError as e:
        print(f"API错误：{e}")
    except Exception as e:
        print(f"未知错误：{e}")

# 示例：调用不同模型
if __name__ == "__main__":
    
    # 基本调用
    print("\n" + "="*50)
    print("基本API调用示例")
    print("="*50)
    call_llm("qwen3.5-2b", "1+1=？")
    
    # 高级调用示例
    print("\n" + "="*50)
    print("高级API调用示例")
    print("="*50)
    
    # 示例1: 带系统提示的调用（设定角色）
    system_prompt = "你是一个专业的数学老师，擅长用清晰的方式解释数学问题。"
    call_llm_advanced(
        model_name="qwen3.5-2b",
        user_content="解释一下什么是质数",
        system_prompt=system_prompt,
        temperature=0.8,
        max_tokens=200
    )
    
    # 示例2: 代码生成（降低随机性）
    call_llm_advanced(
        model_name="qwen3.5-2b",
        user_content="写一个Python函数，计算斐波那契数列的第n项",
        system_prompt="你是一个经验丰富的Python程序员，代码简洁高效。",
        temperature=0.2,  # 低温度确保代码准确性
        max_tokens=300
    )
    
    # 示例3: 创意写作（高随机性）
    call_llm_advanced(
        model_name="qwen3.5-2b",
        user_content="写一个关于人工智能的短故事开头",
        system_prompt="你是一个富有创造力的科幻作家，想象力丰富。",
        temperature=1.2,  # 高温度增加创意性
        top_p=0.9,
        presence_penalty=0.5
    )
