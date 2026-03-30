from typing import Optional, Generator, Dict, Any
from .openai_client import openai_client
from .style_manager import style_manager


class ArticleGenerator:
    """文章生成器"""

    def generate_title(self, topic: str, style: str = "general") -> Optional[str]:
        """生成文章标题

        Args:
            topic: 文章主题
            style: 写作风格

        Returns:
            生成的标题
        """
        prompt = f"为主题 '{topic}' 生成一个吸引人的文章标题，风格为 {style}。"
        return openai_client.generate_content(prompt, max_tokens=50)

    def generate_content(
        self,
        topic: str,
        style: str = "general",
        length: str = "medium",
        title: Optional[str] = None
    ) -> Optional[str]:
        """生成文章内容

        Args:
            topic: 文章主题
            style: 写作风格
            length: 文章长度 (short/medium/long)
            title: 文章标题

        Returns:
            生成的文章内容
        """
        # 根据长度确定内容长度
        length_mapping = {
            "short": "约200字",
            "medium": "约500字",
            "long": "约1000字"
        }
        content_length = length_mapping.get(length, "约500字")

        # 获取风格化的提示词
        if style in style_manager.get_style_names():
            base_prompt = style_manager.get_style_prompt(style, topic)
        else:
            base_prompt = f"以 {style} 风格，围绕主题 '{topic}' 生成一篇文章。"

        # 构建完整提示词
        if title:
            prompt = f"{base_prompt} 文章标题为 '{title}'，长度为{content_length}。"
        else:
            prompt = f"{base_prompt} 长度为{content_length}。"

        return openai_client.generate_content(prompt)

    def stream_content(
        self,
        topic: str,
        style: str = "general",
        length: str = "medium",
        title: Optional[str] = None
    ) -> Generator[str, None, None]:
        """流式生成文章内容

        Args:
            topic: 文章主题
            style: 写作风格
            length: 文章长度 (short/medium/long)
            title: 文章标题

        Yields:
            生成的内容片段
        """
        # 根据长度确定内容长度
        length_mapping = {
            "short": "约200字",
            "medium": "约500字",
            "long": "约1000字"
        }
        content_length = length_mapping.get(length, "约500字")

        # 获取风格化的提示词
        if style in style_manager.get_style_names():
            base_prompt = style_manager.get_style_prompt(style, topic)
        else:
            base_prompt = f"以 {style} 风格，围绕主题 '{topic}' 生成一篇文章。"

        # 构建完整提示词
        if title:
            prompt = f"{base_prompt} 文章标题为 '{title}'，长度为{content_length}。"
        else:
            prompt = f"{base_prompt} 长度为{content_length}。"

        yield from openai_client.stream_content(prompt)


# 创建生成器实例
article_generator = ArticleGenerator()
