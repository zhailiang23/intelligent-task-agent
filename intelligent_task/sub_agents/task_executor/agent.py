"""
任务执行子Agent - 基于Think-Act-Observe模式执行具体任务
"""

import json
import re
from typing import Optional
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import llm_response as llm_response_module
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams, StdioServerParameters

from . import prompt

MODEL = "gemini-2.0-flash"


def update_task_execution_status(
    callback_context: CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """
    更新任务执行状态和结果
    """
    if not llm_response.content or not llm_response.content.parts:
        return None
        
    response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, 'text') and part.text is not None:
            response_text += part.text
    
    # 检查是否包含任务完成标识
    if "任务完成" in response_text or "任务已完成" in response_text or "✅" in response_text:
        # 获取当前正在执行的任务ID
        current_task_id = callback_context.state.get("current_executing_task_id")
        task_list = callback_context.state.get("confirmed_task_list", [])
        
        if current_task_id and task_list:
            # 更新对应任务的状态
            for task in task_list:
                if task["id"] == current_task_id:
                    task["status"] = "completed"
                    task["execution_result"] = response_text[:500]  # 保存前500字符的执行结果
                    print(f"任务 {current_task_id} 执行完成")
                    break
            
            # 更新session.state
            callback_context.state["confirmed_task_list"] = task_list
            # 清除当前执行任务ID
            callback_context.state["current_executing_task_id"] = None
    
    return None


# 创建MCP工具集
def create_mcp_toolsets():
    """创建所有MCP工具集"""
    toolsets = []
    
    # BraveSearch工具
    try:
        brave_search_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@modelcontextprotocol/server-brave-search"]
                )
            )
        )
        toolsets.append(brave_search_toolset)
    except Exception as e:
        print(f"BraveSearch工具初始化失败: {e}")
    
    # Fetch工具
    try:
        fetch_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@modelcontextprotocol/server-fetch"]
                )
            )
        )
        toolsets.append(fetch_toolset)
    except Exception as e:
        print(f"Fetch工具初始化失败: {e}")
    
    # FileSystem工具
    try:
        filesystem_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@modelcontextprotocol/server-filesystem"]
                )
            )
        )
        toolsets.append(filesystem_toolset)
    except Exception as e:
        print(f"FileSystem工具初始化失败: {e}")
    
    # Time工具
    try:
        time_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@modelcontextprotocol/server-time"]
                )
            )
        )
        toolsets.append(time_toolset)
    except Exception as e:
        print(f"Time工具初始化失败: {e}")
    
    # Office Word工具
    try:
        office_word_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@modelcontextprotocol/server-office-word"]
                )
            )
        )
        toolsets.append(office_word_toolset)
    except Exception as e:
        print(f"Office Word工具初始化失败: {e}")
    
    # Office Excel工具
    try:
        office_excel_toolset = MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=["@modelcontextprotocol/server-office-excel"]
                )
            )
        )
        toolsets.append(office_excel_toolset)
    except Exception as e:
        print(f"Office Excel工具初始化失败: {e}")
    
    return toolsets


def get_task_executor_instruction(context) -> str:
    """
    动态生成任务执行指令
    """
    current_task_id = context.state.get("current_executing_task_id")
    task_list = context.state.get("confirmed_task_list", [])
    
    if not current_task_id or not task_list:
        return "没有找到需要执行的任务。请先指定要执行的任务ID。"
    
    # 找到要执行的任务
    current_task = None
    for task in task_list:
        if task["id"] == current_task_id:
            current_task = task
            break
    
    if not current_task:
        return f"未找到ID为 {current_task_id} 的任务。"
    
    instruction = f"""现在需要执行以下任务：

**任务标题**: {current_task['title']}
**任务描述**: {current_task['description']}
**任务ID**: {current_task['id']}

请按照Think-Act-Observe的循环模式来执行这个任务：

1. **思考阶段**：深入分析任务要求，制定执行策略
2. **行动阶段**：使用合适的工具执行具体操作
3. **观察阶段**：评估执行结果，决定下一步

你可以使用以下工具：
- braveSearch: 搜索网络信息
- fetch: 获取网页内容
- fileSystem: 文件操作
- time: 时间相关操作
- office_word: Word文档处理
- office_excel: Excel表格处理

请开始执行任务，如果遇到需要用户补充的信息，请直接询问用户。如果无法完成任务，请明确说明原因。"""
    
    return instruction


# 创建任务执行agent
try:
    mcp_toolsets = create_mcp_toolsets()
    
    task_executor_agent = Agent(
        name="task_executor_agent",
        model=MODEL,
        description="基于Think-Act-Observe模式的任务执行器，能够使用多种工具执行具体任务",
        instruction=get_task_executor_instruction,
        tools=mcp_toolsets,
        after_model_callback=update_task_execution_status,
    )
except Exception as e:
    print(f"创建task_executor_agent失败: {e}")
    # 创建没有工具的基础版本
    task_executor_agent = Agent(
        name="task_executor_agent",
        model=MODEL,
        description="基于Think-Act-Observe模式的任务执行器",
        instruction=get_task_executor_instruction,
        after_model_callback=update_task_execution_status,
    )