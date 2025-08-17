"""
任务复杂度分析器 - 共享库
"""


class ComplexityAnalyzer:
    """任务复杂度分析器"""
    
    SIMPLE_KEYWORDS = [
        "什么是", "如何", "为什么", "解释", "介绍", "定义", 
        "简单", "快速", "直接", "基础", "概念"
    ]
    
    COMPLEX_KEYWORDS = [
        "开发", "实现", "设计", "构建", "创建", "部署", "优化",
        "系统", "架构", "集成", "自动化", "多步骤", "复杂",
        "项目", "流程", "策略", "计划", "方案"
    ]
    
    @classmethod
    def analyze_complexity(cls, user_input: str) -> str:
        """
        分析用户输入的复杂度
        
        Args:
            user_input: 用户输入的任务描述
            
        Returns:
            "simple" 或 "complex"
        """
        user_input_lower = user_input.lower()
        
        # 检查简单关键词
        simple_score = sum(1 for keyword in cls.SIMPLE_KEYWORDS 
                          if keyword in user_input_lower)
        
        # 检查复杂关键词
        complex_score = sum(1 for keyword in cls.COMPLEX_KEYWORDS 
                           if keyword in user_input_lower)
        
        # 长度判断 - 超过100字符可能是复杂任务
        length_factor = len(user_input) > 100
        
        # 多个句子或步骤判断
        multiple_steps = any(marker in user_input_lower 
                           for marker in ["然后", "接着", "同时", "另外", "并且", "以及"])
        
        # 综合判断
        if complex_score > simple_score or length_factor or multiple_steps:
            return "complex"
        elif simple_score > 0 and complex_score == 0:
            return "simple"
        else:
            # 默认情况，如果不确定，当作复杂任务处理
            return "complex"