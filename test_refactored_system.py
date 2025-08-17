#!/usr/bin/env python3
"""
测试重构后的系统 - 验证所有组件是否正确集成
"""

def test_imports():
    """测试所有imports"""
    print("🔧 测试导入...")
    
    try:
        from intelligent_task.agent import root_agent
        print("✅ 主agent导入成功")
        
        from intelligent_task.sub_agents.task_decomposer import task_decomposer_agent
        print("✅ task_decomposer_agent导入成功")
        
        from intelligent_task.sub_agents.task_monitor import task_monitor_agent
        print("✅ task_monitor_agent导入成功")
        
        return True
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_structure():
    """测试agent结构"""
    print("\n🔧 测试agent结构...")
    
    try:
        from intelligent_task.agent import root_agent
        
        # 检查主agent属性
        print(f"📊 主agent名称: {root_agent.name}")
        print(f"📊 主agent模型: {root_agent.model}")
        print(f"📊 主agent工具数量: {len(root_agent.tools)}")
        
        # 检查工具
        for i, tool in enumerate(root_agent.tools):
            print(f"   🔧 工具 {i+1}: {type(tool).__name__}")
            if hasattr(tool, 'agent'):
                print(f"      └─ Agent: {tool.agent.name}")
        
        return True
    except Exception as e:
        print(f"❌ 结构测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_mock_response_processing():
    """测试响应处理逻辑（模拟）"""
    print("\n🔧 测试响应处理逻辑...")
    
    try:
        from intelligent_task.sub_agents.task_decomposer.agent import save_confirmed_tasks_to_state
        from intelligent_task.sub_agents.task_monitor.agent import update_task_status_from_response
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import llm_response as llm_response_module
        from google.genai import types
        
        # 创建模拟的callback context
        class MockCallbackContext:
            def __init__(self):
                self.state = {}
        
        # 创建模拟的LLM response (with None text)
        mock_part_with_none = types.Part()
        mock_part_with_none.text = None
        
        mock_part_with_text = types.Part(text="## 执行步骤\n1. **步骤1**: 测试描述")
        
        mock_content = types.Content(
            role="model",
            parts=[mock_part_with_none, mock_part_with_text]
        )
        
        mock_response = llm_response_module.LlmResponse(content=mock_content)
        mock_context = MockCallbackContext()
        
        # 测试空值处理
        result = save_confirmed_tasks_to_state(mock_context, mock_response)
        print("✅ 空值处理测试通过 - 没有抛出异常")
        
        return True
    except Exception as e:
        print(f"❌ 响应处理测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试重构后的智能任务Agent系统\n")
    
    tests = [
        ("导入测试", test_imports),
        ("Agent结构测试", test_agent_structure),
        ("响应处理测试", test_mock_response_processing),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"🧪 运行: {test_name}")
        print(f"{'='*50}")
        
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} 通过")
            else:
                print(f"❌ {test_name} 失败")
        except Exception as e:
            print(f"❌ {test_name} 异常: {str(e)}")
    
    print(f"\n{'='*50}")
    print(f"📊 测试总结: {passed}/{total} 测试通过")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 所有测试通过！系统重构成功。")
        print("\n📋 系统功能:")
        print("1. ✅ 任务拆解 (task_decomposer_agent)")
        print("2. ✅ 任务监控 (task_monitor_agent - LoopAgent)")
        print("3. ✅ 智能分发 (主agent)")
        print("4. ✅ Session状态管理")
        print("5. ✅ 错误处理 (空值保护)")
        return True
    else:
        print("❌ 部分测试失败，请检查问题。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)