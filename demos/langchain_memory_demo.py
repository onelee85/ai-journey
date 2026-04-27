# 基于本地 LLM langchain demo
from typing import Any
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

load_dotenv()

MODEL_LIST = [
    "qwen3.5-2b",
    "qwen3.5-4b",
]
llm = ChatOpenAI(
    base_url=os.getenv("LM_STUDIO_API_BASE"),
    api_key=os.getenv("LM_STUDIO_API_KEY"),
    model=MODEL_LIST[0],
    temperature=0.7,
    max_tokens=150,
)


str_output_parser = StrOutputParser()


def print_prompt(full_prompt):
    print("="*50)
    print(f"full_prompt: {full_prompt.to_string()}")
    return full_prompt


prompt_template = ChatPromptTemplate.from_messages(
    [
        ("system", "你需要根据历史回应用户问题"),
        ("human", "{user_input}"),
    ]
)

base_chain = prompt_template | print_prompt | llm | str_output_parser

history_store = {}


# 定义历史获取函数
def get_history(session_id: str = None):
    if session_id not in history_store:
        history_store[session_id] = InMemoryChatMessageHistory()
    return history_store[session_id]


# 定义当前链
current_chain = RunnableWithMessageHistory(
    base_chain,
    get_session_history=get_history,
    input_messages_key="user_input",
)

if __name__ == "__main__":
    session_config = {
        "configurable": {
            "session_id": "123",
        }
    }
    # 调用当前链
    response = current_chain.invoke({"user_input": "张三有 3 只猫"}, session_config)
    print(f"回答：{response}")
    # 调用当前链
    response = current_chain.invoke({"user_input": "李四有 4 只狗"}, session_config)
    print(f"回答：{response}")

    response = current_chain.invoke({"user_input": "一共有几只宠物"}, session_config)
    print(f"回答：{response}")
