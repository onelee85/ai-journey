
from string import Template

from utils.llm_api_client import llm


# 文章摘要模版


class ArticleSummaryPrompt:
    def __init__(self):
        self.template = Template("""请为以下文章生成摘要：
文章内容：
${article}

请遵循以下要求：
- 摘要长度：${length}字
- 输出格式：纯文本
- 重点：保留核心观点和关键信息

摘要：""")

    def format(self, article, length=100):
        return self.template.substitute(article=article, length=length)

# 通用模版


class PromptTemplate:

    def __init__(self, template):
        self.template = Template(template)

    def format(self, **kwargs):
        return self.template.substitute(kwargs)


article_summary_prompt = ArticleSummaryPrompt().format(article="这是一篇关于AI的文章")
print(article_summary_prompt)
response = llm("qwen3.5-2b", article_summary_prompt)
print(response)

template = PromptTemplate("""
You are a $role.

Explain $topic.
""")

prompt = template.format(
    role="AI expert",
    topic="neural networks"
)
print(prompt)
# 调用
response = llm("qwen3.5-2b", prompt)
print(response)
