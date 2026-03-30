import pytest
from src.article_generator import article_generator
from src.style_manager import style_manager

class TestArticleGenerator:
    """测试文章生成器"""
    
    def test_generate_title(self):
        """测试生成标题"""
        topic = "人工智能的未来"
        title = article_generator.generate_title(topic, "creative")
        assert title is not None
        assert len(title) > 0
    
    def test_generate_content(self):
        """测试生成内容"""
        topic = "人工智能的未来"
        style = "creative"
        length = "short"
        content = article_generator.generate_content(topic, style, length)
        assert content is not None
        assert len(content) > 0
    
    def test_stream_content(self):
        """测试流式生成内容"""
        topic = "人工智能的未来"
        style = "creative"
        length = "short"
        chunks = []
        for chunk in article_generator.stream_content(topic, style, length):
            chunks.append(chunk)
        content = "".join(chunks)
        assert content is not None
        assert len(content) > 0

class TestStyleManager:
    """测试风格管理器"""
    
    def test_get_style(self):
        """测试获取风格"""
        style = style_manager.get_style("academic")
        assert style is not None
        assert style["name"] == "学术风格"
    
    def test_get_style_names(self):
        """测试获取风格名称列表"""
        style_names = style_manager.get_style_names()
        assert isinstance(style_names, list)
        assert len(style_names) >= 5
        assert "academic" in style_names
        assert "business" in style_names
        assert "creative" in style_names
        assert "technical" in style_names
        assert "story" in style_names
    
    def test_get_style_prompt(self):
        """测试获取风格化的提示词"""
        topic = "人工智能的未来"
        prompt = style_manager.get_style_prompt("academic", topic)
        assert prompt is not None
        assert len(prompt) > 0
        assert "人工智能的未来" in prompt