#!/usr/bin/env python3
"""
测试连接脚本 - 验证agent是否可以正常工作
"""

import asyncio
from intelligent_task.agent import root_agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types

async def test_basic_connection():
    """测试基本连接功能"""
    print("🔧 开始测试agent基本功能...")
    
    try:
        # 创建session service和runner
        session_service = InMemorySessionService()
        runner = Runner(
            agent=root_agent,
            app_name="test_app",
            session_service=session_service
        )
        
        # 创建测试会话
        session_id = "test_session_001"
        user_id = "test_user"
        
        await session_service.create_session(
            app_name="test_app",
            user_id=user_id,
            session_id=session_id
        )
        
        print("✅ Session创建成功")
        
        # 测试简单问题
        test_message = types.Content(
            role="user",
            parts=[types.Part(text="你好，你是什么？")]
        )
        
        print("📤 发送测试消息...")
        
        # 运行agent
        events_count = 0
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=test_message
        ):
            events_count += 1
            if event.is_final_response() and event.content:
                print(f"✅ 收到最终响应，共处理{events_count}个事件")
                print(f"📝 响应内容: {event.content.parts[0].text[:100]}...")
                break
            elif event.is_error():
                print(f"❌ 出现错误: {event.error_details}")
                return False
        
        print("🎉 基本连接测试成功！")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_basic_connection())
    if success:
        print("\n✅ 所有测试通过！Agent可以正常工作。")
    else:
        print("\n❌ 测试失败！请检查配置。")