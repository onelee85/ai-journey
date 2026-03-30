from typing import Dict, Any

class StyleManager:
    """写作风格管理器"""
    
    def __init__(self):
        """初始化风格管理器"""
        self.styles = {
            "academic": {
                "name": "学术风格",
                "description": "正式、严谨、逻辑清晰的学术写作风格",
                "prompt_template": "请以学术风格撰写一篇关于{topic}的文章。使用正式的语言，清晰的逻辑结构，适当的引用和论证。内容应具有深度和专业性，适合学术读者。"
            },
            "business": {
                "name": "商务风格",
                "description": "专业、简洁、目标明确的商务写作风格",
                "prompt_template": "请以商务风格撰写一篇关于{topic}的文章。使用专业、简洁的语言，重点突出核心观点和商业价值。内容应具有实用性和可操作性，适合商务人士阅读。"
            },
            "creative": {
                "name": "创意风格",
                "description": "富有想象力、生动形象的创意写作风格",
                "prompt_template": "请以创意风格撰写一篇关于{topic}的文章。使用生动、形象的语言，富有想象力的表达，创造引人入胜的阅读体验。内容应具有独特性和艺术感染力。"
            },
            "technical": {
                "name": "技术风格",
                "description": "准确、详细、专业的技术写作风格",
                "prompt_template": "请以技术风格撰写一篇关于{topic}的文章。使用准确、专业的术语，详细的步骤说明，清晰的技术逻辑。内容应具有可操作性和技术深度，适合技术人员阅读。"
            },
            "story": {
                "name": "故事风格",
                "description": "生动、感人、有情节的故事写作风格",
                "prompt_template": "请以故事风格撰写一篇关于{topic}的文章。使用生动的叙述，丰富的细节，有吸引力的情节。内容应具有情感共鸣和故事性，适合普通读者阅读。"
            }
        }
    
    def get_style(self, style_name: str) -> Dict[str, Any]:
        """获取风格配置
        
        Args:
            style_name: 风格名称
            
        Returns:
            风格配置
        """
        return self.styles.get(style_name, self.styles["creative"])
    
    def get_style_names(self) -> list:
        """获取所有风格名称
        
        Returns:
            风格名称列表
        """
        return list(self.styles.keys())
    
    def get_style_prompt(self, style_name: str, topic: str) -> str:
        """获取风格化的提示词
        
        Args:
            style_name: 风格名称
            topic: 文章主题
            
        Returns:
            风格化的提示词
        """
        style = self.get_style(style_name)
        return style["prompt_template"].format(topic=topic)

# 创建风格管理器实例
style_manager = StyleManager()