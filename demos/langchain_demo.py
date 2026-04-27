# 基于本地 LLM langchain demo
from typing import Any


import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableLambda

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

str_output_parser = StrOutputParser()
json_output_parser = JsonOutputParser()
runnable_lambda = RunnableLambda[Any, Any](lambda x: {"reasoning": x.content})


prompt_template = PromptTemplate.from_template(
    "你好， 我口腔张不开了，你是一个专业的{system_prompt}, 我想知道什么病症的名称？ 并返回 JSON 格式返回，key 是 reasoning，value 是病症")

prompt_template2 = PromptTemplate.from_template(
    "我的病症是 {reasoning}, 为我开药建议")


# prompt_text = prompt_template.format(system_prompt="医生")
# response = llm.invoke(prompt_text)
# print(response.content)

# 原理： Runnable 是一个可调用的对象，它接受一个输入并返回一个输出
chain = prompt_template | llm | runnable_lambda | prompt_template2 | llm | str_output_parser
response: str = chain.stream({"system_prompt": "医生"})
for chunk in response:
    print(chunk, end="", flush=True)
