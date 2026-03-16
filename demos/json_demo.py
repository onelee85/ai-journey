"""
JSON 数据提取演示 Demo
========================

本演示展示了如何使用 LLM 从非结构化文本中提取结构化 JSON 数据。
包含两种方法：
1. 基础方法：使用普通 LLM 调用，手动解析 JSON 输出
2. Schema 方法：使用 JSON Schema 约束，强制 LLM 返回格式化 JSON

作者: Lijiao
日期: 2026
"""

from utils.llm_api_client import llm, llm_json_schema
import json
import re
from typing import Dict, Any


class ProductInfoExtractor:
    """
    产品信息提取器类

    封装了从文本中提取产品信息的功能，支持两种提取方式：
    - 基础 JSON 解析
    - Schema 约束的 JSON 提取
    """

    def __init__(self, model_name: str = "qwen3.5-2b"):
        """
        初始化提取器

        Args:
            model_name: 使用的 LLM 模型名称
        """
        self.model_name = model_name

    def extract_with_basic_method(self, text: str) -> Dict[str, Any]:
        """
        使用基础方法提取产品信息（手动解析 JSON）

        这种方法通过提示词引导 LLM 返回 JSON，然后手动解析响应内容。
        需要处理多种可能的输出格式（纯 JSON、代码块格式等）。

        Args:
            text: 包含产品信息的原始文本

        Returns:
            dict: 提取的产品信息，包含 product_name、price、currency

        Raises:
            ValueError: 当无法从响应中解析出有效 JSON 时
            Exception: 其他运行时错误
        """
        # 构建提示词
        prompt = self._build_extraction_prompt(text)

        print("=" * 60)
        print("方法一：基础 JSON 解析法")
        print("=" * 60)

        # 调用 LLM 获取响应
        response = llm(self.model_name, prompt)
        content = response.choices[0].message.content

        print("\n模型原始输出:")
        print(content)
        print("\n" + "-" * 60)

        # 尝试直接解析 JSON
        try:
            product_info = json.loads(content)
            print("✓ 成功解析 JSON（直接解析）")
        except json.JSONDecodeError:
            # 如果直接解析失败，尝试从代码块中提取
            print("✗ 直接解析失败，尝试从代码块提取...")

            # 尝试匹配 ```json ... ``` 格式
            json_match = re.search(
                r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                product_info = json.loads(json_match.group(1))
                print("✓ 成功从 JSON 代码块解析")
            else:
                # 尝试匹配任意 JSON 对象
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    product_info = json.loads(json_match.group())
                    print("✓ 成功从文本中提取 JSON 对象")
                else:
                    raise ValueError("无法解析 JSON - 响应中不包含有效的 JSON 格式")

        print("\n提取的产品信息:")
        print(json.dumps(product_info, indent=2, ensure_ascii=False))
        print("=" * 60 + "\n")

        return product_info

    def extract_with_schema(self, text: str) -> Dict[str, Any]:
        """
        使用 JSON Schema 约束提取产品信息

        这种方法使用 JSON Schema 定义输出格式，强制 LLM 返回符合
        预定义结构的 JSON，提高输出的可靠性和一致性。

        Args:
            text: 包含产品信息的原始文本

        Returns:
            dict: 提取的产品信息，包含 product_name、price、currency

        Raises:
            Exception: LLM 调用或解析失败时
        """
        # 定义 JSON Schema，约束输出格式
        schema = {
            "type": "object",
            "properties": {
                "product_name": {
                    "type": "string",
                    "description": "产品名称"
                },
                "price": {
                    "type": "number",
                    "description": "产品价格"
                },
                "currency": {
                    "type": "string",
                    "description": "货币单位（USD, CNY等）"
                }
            },
            "required": ["product_name", "price", "currency"],
            "additionalProperties": False
        }

        # 构建 OpenAI 兼容的 schema 格式
        openai_schema = {
            "name": "product_info",
            "schema": schema
        }

        # 构建提示词
        prompt = self._build_extraction_prompt(text)

        print("=" * 60)
        print("方法二：JSON Schema 约束法")
        print("=" * 60)

        # 调用 LLM，使用 JSON Schema 约束输出格式
        response = llm_json_schema(self.model_name, prompt, openai_schema)

        # 解析响应
        content = response.choices[0].message.content
        product_info = json.loads(content)

        print("\n模型输出 (受 Schema 约束):")
        print(json.dumps(product_info, indent=2, ensure_ascii=False))
        print("=" * 60 + "\n")

        return product_info

    def _build_extraction_prompt(self, text: str) -> str:
        """
        构建数据提取提示词

        Args:
            text: 原始文本

        Returns:
            str: 完整的提示词
        """
        return f"""你是一个专业的数据提取助手。请从以下文本中提取产品信息，返回 JSON 格式。

要求：
1. 从文本中提取实际的产品名称、价格和货币单位
2. 如果文本中没有明确信息，使用合理的推断值
3. 返回有效的 JSON 对象，不要包含其他内容
4. 不要返回空值或占位符

JSON Schema:
{{
  "product_name": "string - 产品名称",
  "price": "number - 产品价格",
  "currency": "string - 货币单位（USD, CNY等）"
}}

原始文本:
{text}

请严格按 JSON 格式输出提取的信息："""


def demo_basic_extraction():
    """
    演示基础提取方法
    """
    # 示例文本
    text = """
这款 iPhone 15 Pro 是一款高端智能手机，售价 999 美元。
它配备了 A17 Pro 芯片和 4800 万像素主摄。
"""

    extractor = ProductInfoExtractor()
    result = extractor.extract_with_basic_method(text)

    return result


def demo_schema_extraction():
    """
    演示 Schema 约束提取方法
    """
    # 示例文本
    text = """
这款 iPhone 15 Pro 是一款高端智能手机，售价 999 美元。
它配备了 A17 Pro 芯片和 4800 万像素主摄。
"""

    extractor = ProductInfoExtractor()
    result = extractor.extract_with_schema(text)

    return result


def demo_with_custom_text(custom_text: str):
    """
    使用自定义文本进行提取演示

    Args:
        custom_text: 用户自定义的输入文本
    """
    extractor = ProductInfoExtractor()

    print("\n" + "#" * 60)
    print("# 自定义文本提取演示")
    print("#" * 60)
    print(f"\n输入文本:\n{custom_text}\n")

    # 使用两种方法提取
    result1 = extractor.extract_with_basic_method(custom_text)
    result2 = extractor.extract_with_schema(custom_text)

    print("\n结果对比:")
    print(f"基础方法结果:  {result1}")
    print(f"Schema方法结果: {result2}")

    return result1, result2


if __name__ == "__main__":
    """
    主函数：运行所有演示
    """
    print("\n" + "=" * 60)
    print("JSON 数据提取演示")
    print("=" * 60)

    # 演示方法一：基础 JSON 解析
    result1 = demo_basic_extraction()

    # 演示方法二：JSON Schema 约束
    result2 = demo_schema_extraction()

    # 测试自定义文本（可选）
    custom_text = "这台 MacBook Pro 售价 12999 元人民币，配备 M3 芯片。"
    demo_with_custom_text(custom_text)

    print("\n演示完成！")
