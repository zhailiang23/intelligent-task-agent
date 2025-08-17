"""
警告配置管理 - 抑制已知的无害警告
"""

import warnings
import logging


def configure_warnings():
    """配置警告过滤器，抑制已知的无害警告"""
    
    # 抑制pydantic字段名冲突警告
    warnings.filterwarnings(
        "ignore",
        message="Field name.*shadows an attribute in parent.*",
        category=UserWarning,
        module="pydantic._internal._fields"
    )
    
    # 抑制ADK实验性功能警告
    warnings.filterwarnings(
        "ignore", 
        message=".*EXPERIMENTAL.*",
        category=UserWarning,
        module="google.adk.*"
    )
    
    # 配置日志级别，减少不必要的信息
    logging.getLogger("google.adk").setLevel(logging.WARNING)


def setup_clean_environment():
    """设置清洁的运行环境"""
    configure_warnings()
    print("✅ 已配置警告过滤器，输出将更加清洁")