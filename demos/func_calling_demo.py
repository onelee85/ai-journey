
from utils.llm_api_client import llm_function_call
import json
import requests
import logging
from bs4 import BeautifulSoup
from utils.weather_app import WeatherApp


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


# 1. 定义真实天气查询函数（模拟API）
def get_weather(city: str) -> str:
    """模拟天气API：查询城市天气"""
    logger.info(f"查询天气：{city}")
    weather_data = {
        "北京": "晴，15℃，微风",
        "上海": "小雨，20℃，湿度70%",
        "广州": "多云，25℃，适宜出行"
    }
    result = weather_data.get(city, "暂未查询到该城市天气")
    logger.info(f"天气查询结果：{result}")
    return result


# 1.1 通过天气API查询函数获取天气信息
def get_weather_by_api(city: str) -> str:
    logger.info(f"通过API查询天气：{city}")
    try:
        app = WeatherApp()
        weather_data = app.get_weather(city)
        logger.info(f"API天气查询成功：{weather_data}")
        return weather_data
    except Exception as e:
        logger.error(f"天气API调用失败：{str(e)}")
        return f"天气查询失败：{str(e)}"


# 2. 计算器 calculate 函数
def calculate(a: float, b: float) -> float:
    """计算两个整数的和
    - 参数：数学表达式或操作数、运算符
- 返回：计算结果
    """
    logger.info(f"计算：{a} + {b}")
    try:
        result = a + b
        logger.info(f"计算结果：{result}")
        return result
    except Exception as e:
        logger.error(f"计算失败：{str(e)}")
        raise


# 3.搜索函数 search
def search(keyword: str, scope: str = "网页") -> list:
    """
    调用百度搜索接口，返回结构化搜索结果
    :param keyword: 查询关键词
    :param scope: 搜索范围（网页/百科/新闻/知道）
    :return: 搜索结果列表 [{"title":"标题", "url":"链接", "summary":"摘要"}, ...]
    """
    # 百度搜索域名映射
    scope_url = {
        "网页": "https://www.baidu.com/s",
        "百科": "https://www.baidu.com/s",
        "新闻": "https://www.baidu.com/s",
        "知道": "https://www.baidu.com/s"
    }

    # 请求头（模拟真实浏览器）
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }

    # 请求参数
    params = {"wd": keyword, "pn": 0}  # wd=关键词，pn=页码
    base_url = scope_url.get(scope, scope_url["网页"])

    try:
        # 发送百度搜索请求
        logger.info(f"发送搜索请求：{base_url}")
        response = requests.get(base_url, params=params,
                                headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        results = []

        # 取前3条结果 - 使用更通用的选择器
        # 百度搜索结果通常包含 h3 标题
        h3_elements = soup.find_all("h3", limit=10)
        logger.info(f"找到 {len(h3_elements)} 个搜索结果")

        # 使用更简单的提取逻辑
        for h3 in h3_elements:
            # 获取标题
            title = h3.get_text(strip=True)
            if not title:
                continue

            # 获取链接
            link = h3.find_parent("a")
            if not link:
                link = h3.find("a")
            url = link["href"] if link and link.has_attr("href") else ""
            if not url:
                continue

            # 获取摘要 - 从父元素中查找
            parent = h3.find_parent("div")
            summary = ""
            if parent:
                # 查找所有 p 标签和 div 标签作为摘要
                summary_tags = parent.find_all(["p", "div", "span"])
                for tag in summary_tags:
                    text = tag.get_text(strip=True)
                    # 摘要通常在 30-150 字符之间
                    if 30 < len(text) < 150:
                        summary = text
                        break

            results.append({"title": title, "url": url, "summary": summary})
            logger.debug(f"提取结果：{title}")

            if len(results) >= 3:
                break

        logger.info(f"返回 {len(results)} 条搜索结果")
        return results if results else [{"error": "未找到搜索结果"}]

    except requests.exceptions.Timeout:
        logger.error(f"搜索请求超时：{keyword}")
        return [{"error": "搜索请求超时"}]
    except requests.exceptions.RequestException as e:
        logger.error(f"搜索请求失败：{str(e)}")
        return [{"error": f"搜索失败：{str(e)}"}]
    except Exception as e:
        logger.error(f"搜索过程发生未知错误：{str(e)}")
        return [{"error": f"搜索失败：{str(e)}"}]


functions = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "查询指定城市的实时天气情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "要查询天气的城市名称，如：北京、上海"
                    }
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "计算两个数字的和",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "第一个数字"
                    },
                    "b": {
                        "type": "number",
                        "description": "第二个数字"
                    }
                },
                "required": ["a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search",
            "description": "调用百度搜索接口,搜索指定关键词的网页、百科、新闻、知道",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "搜索查询关键词，例如: 人工智能、Python教程"
                    },
                    "scope": {
                        "type": "string",
                        "description": "搜索范围，可选值：网页、百科、新闻、知道",
                        "enum": ["网页", "百科", "新闻", "知道"]  # 限定参数值，避免LLM传错
                    }
                },
                "required": ["keyword"]
            }
        }
    }
]


def call_llm(prompt):
    logger.info(f"调用LLM：{prompt[:50]}...")
    messages = [{"role": "user", "content": prompt}]
    try:
        # 调用
        logger.info("发送Function Calling请求")
        response = llm_function_call(
            "stepfun/step-3.5-flash:free", messages, functions)
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        if tool_calls:
            func_name = tool_calls[0].function.name
            func_args = tool_calls[0].function.arguments
            func_args_dict = json.loads(func_args)
            logger.info(f"tool_calls 调用函数：{func_name} 参数：{func_args_dict}")
            result = None
            try:
                if func_name == "get_weather":
                    result = get_weather_by_api(**func_args_dict)
                elif func_name == "calculate":
                    result = calculate(**func_args_dict)
                elif func_name == "search":
                    result = search(**func_args_dict)
                else:
                    logger.error(f"未知函数：{func_name}")
                    result = f"错误：未知函数 {func_name}"
            except Exception as e:
                logger.error(f"函数执行失败：{func_name} - {str(e)}")
                result = f"函数执行失败：{str(e)}"

            messages.append(response_message)
            messages.append(
                {"role": "tool", "tool_call_id": tool_calls[0].id, "name": func_name, "content": str(result)})
            logger.info("发送Function Calling结果")
            response = llm_function_call(
                "stepfun/step-3.5-flash:free", messages, functions)
            final_result = response.choices[0].message.content
            logger.info(f"Function Calling完成，结果长度：{len(final_result)}")
            print(final_result)
        else:
            logger.info("LLM直接返回内容")
            print(response_message.content)
    except Exception as e:
        logger.error(f"LLM调用失败：{str(e)}")
        print(f"错误：LLM调用失败 - {str(e)}")


if __name__ == "__main__":
    logger.info("开始运行Function Calling演示")
    # call_llm("3加 2 等于多少?")
    # call_llm("你是什么模型?")
    # call_llm("长沙适合穿什么衣服?")
    # call_llm("帮我搜索下最近的中超新闻？")
    # print(search("人工智能"))
    call_llm("写一篇简单的西游记文章")
    logger.info("Function Calling演示结束")
