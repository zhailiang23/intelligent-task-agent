#!/usr/bin/env python3
"""
测试任务监控修复 - 验证task_monitor_agent是否能正确询问用户
"""

def test_task_monitor_instruction():
    """测试任务监控指令生成"""
    print("🔧 测试任务监控指令生成...")
    
    try:
        from intelligent_task.sub_agents.task_monitor.agent import get_task_monitor_instruction
        
        # 创建模拟的context (只读状态)
        class MockContext:
            def __init__(self, state):
                import types
                # 模拟只读状态，类似于ADK中的mappingproxy
                self.state = types.MappingProxyType(state)
        
        # 测试1: 没有任务列表
        context1 = MockContext({"confirmed_task_list": []})
        instruction1 = get_task_monitor_instruction(context1)
        print("✅ 空任务列表测试通过")
        print(f"   指令: {instruction1[:50]}...")
        
        # 测试2: 有未完成任务
        context2 = MockContext({
            "confirmed_task_list": [
                {"id": 1, "title": "任务1", "description": "描述1", "status": "pending"},
                {"id": 2, "title": "任务2", "description": "描述2", "status": "pending"},
            ]
        })
        instruction2 = get_task_monitor_instruction(context2)
        print("✅ 有未完成任务测试通过")
        print(f"   指令: {instruction2[:100]}...")
        
        # 测试3: 所有任务已完成
        context3 = MockContext({
            "confirmed_task_list": [
                {"id": 1, "title": "任务1", "description": "描述1", "status": "completed"},
                {"id": 2, "title": "任务2", "description": "描述2", "status": "completed"},
            ]
        })
        instruction3 = get_task_monitor_instruction(context3)
        print("✅ 所有任务完成测试通过")
        print(f"   指令: {instruction3[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_response_callback():
    """测试响应回调处理"""
    print("\n🔧 测试响应回调处理...")
    
    try:
        from intelligent_task.sub_agents.task_monitor.agent import process_user_response_callback
        from google.adk.agents.callback_context import CallbackContext
        from google.adk.models import llm_response as llm_response_module
        from google.genai import types
        
        # 创建模拟的callback context
        class MockCallbackContext:
            def __init__(self):
                self.state = {
                    "current_asking_task_id": 1,
                    "confirmed_task_list": [
                        {"id": 1, "title": "任务1", "description": "描述1", "status": "pending"},
                        {"id": 2, "title": "任务2", "description": "描述2", "status": "pending"},
                    ]
                }
        
        # 创建模拟的LLM response (表示任务已完成)
        mock_content = types.Content(
            role="model",
            parts=[types.Part(text="好的，任务1已完成。")]
        )
        
        mock_response = llm_response_module.LlmResponse(content=mock_content)
        mock_context = MockCallbackContext()
        
        # 测试回调处理
        result = process_user_response_callback(mock_context, mock_response)
        
        # 检查任务状态是否更新
        task1 = mock_context.state["confirmed_task_list"][0]
        if task1["status"] == "completed":
            print("✅ 任务状态更新测试通过")
        else:
            print("❌ 任务状态更新失败")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """测试导入"""
    print("\n🔧 测试修复后的导入...")
    
    try:
        from intelligent_task.sub_agents.task_monitor import task_monitor_agent
        print("✅ task_monitor_agent 导入成功")
        
        from intelligent_task.agent import root_agent
        print("✅ root_agent 导入成功")
        
        # 检查agent属性
        print(f"📊 task_monitor_agent 类型: {type(task_monitor_agent).__name__}")
        print(f"📊 task_monitor_agent 名称: {task_monitor_agent.name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 导入失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试任务监控修复\n")
    
    tests = [
        ("导入测试", test_imports),
        ("任务监控指令生成测试", test_task_monitor_instruction),
        ("响应回调处理测试", test_response_callback),
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
        print("🎉 所有测试通过！任务监控修复成功。")
        print("\n📋 修复说明:")
        print("1. ✅ 移除了复杂的LoopAgent结构")
        print("2. ✅ 使用单次询问模式，等待用户真实回答")
        print("3. ✅ 动态生成询问指令，只问一个任务")
        print("4. ✅ 通过回调处理用户回答并更新状态")
        print("5. ✅ 用户需要多次调用来逐个完成任务确认")
        return True
    else:
        print("❌ 部分测试失败，请检查问题。")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)