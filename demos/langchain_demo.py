# 基于本地 LLM langchain demo
import openai
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate

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
# messages = [
#     SystemMessage(content="你是一个专业的医生"),
#     HumanMessage(content="你好， 我口腔张不开了"),
#     AIMessage(content="你好，有什么我可以帮助你的吗？"),
#     HumanMessage(content="我想知道什么是原因")
# ]

messages = [
    ("system", "你是一个专业的医生"),
    ("human", "你好， 我口腔张不开了"),
    ("ai", "你好，有什么我可以帮助你的吗？"),
    ("human", "我想知道什么是原因")
]

prompt_template = PromptTemplate.from_template("你是一个专业的{system_prompt}")

prompt_text = prompt_template.format(system_prompt="医生")
response = llm.invoke(prompt_text)
print(response.content)
