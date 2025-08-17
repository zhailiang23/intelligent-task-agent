#!/usr/bin/env python3
"""
智能任务Agent部署脚本
"""

import os
import sys

# 添加路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置警告过滤器以获得更清洁的输出
from intelligent_task.shared_libraries.warning_config import setup_clean_environment
setup_clean_environment()

from intelligent_task.agent import root_agent, intelligent_task_coordinator
from intelligent_task.sub_agents.task_decomposer.agent import task_decomposer_agent


def deploy_agent():
    """部署智能任务Agent"""
    print("=== 部署智能任务Agent系统 ===")
    
    # 主Agent信息
    print(f"\n主Agent:")
    print(f"  名称: {intelligent_task_coordinator.name}")
    print(f"  描述: {intelligent_task_coordinator.description}")
    print(f"  模型: {intelligent_task_coordinator.model}")
    
    # 子Agent信息
    print(f"\n子Agent:")
    print(f"  名称: {task_decomposer_agent.name}")
    print(f"  描述: {task_decomposer_agent.description}")
    print(f"  模型: {task_decomposer_agent.model}")
    
    # 工具信息
    tools_count = len(intelligent_task_coordinator.tools)
    print(f"\n工具集成:")
    print(f"  AgentTool数量: {tools_count}")
    print(f"  子Agent工具: task_decomposer_agent")
    
    return root_agent


def test_agent_structure():
    """测试Agent结构"""
    print("\n=== 测试Agent结构 ===")
    
    # 测试导入
    try:
        from intelligent_task.shared_libraries.complexity_analyzer import ComplexityAnalyzer
        print("✅ 复杂度分析器导入成功")
        
        # 简单测试
        simple_task = "什么是Python?"
        complex_task = "开发一个完整的电商网站系统"
        
        simple_result = ComplexityAnalyzer.analyze_complexity(simple_task)
        complex_result = ComplexityAnalyzer.analyze_complexity(complex_task)
        
        print(f"  简单任务测试: '{simple_task}' -> {simple_result}")
        print(f"  复杂任务测试: '{complex_task}' -> {complex_result}")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")


if __name__ == "__main__":
    print("开始部署智能任务Agent...")
    
    # 部署Agent
    agent = deploy_agent()
    
    # 测试结构
    test_agent_structure()
    
    print(f"\n✅ 部署完成! 根Agent '{agent.name}' 已就绪")
    print("\n🎯 架构特点:")
    print("1. ✅ 标准ADK多agent架构")
    print("2. ✅ AgentTool模式调用子agent")
    print("3. ✅ 清晰的模块化结构")
    print("4. ✅ LLM驱动的智能任务分发")
    print("5. ✅ 专业的任务拆解能力")
    
    print("\n📋 使用方式:")
    print("- 简单任务: 主Agent直接回答")
    print("- 复杂任务: 自动调用task_decomposer_agent进行拆解")
    print("- 基于LLM自然语言理解进行智能分发")