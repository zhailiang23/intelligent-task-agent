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
    
    # 首先设置当前执行的任务ID（如果还没设置）
    task_list = callback_context.state.get("confirmed_task_list", [])
    current_task_id = callback_context.state.get("current_executing_task_id")
    
    if not current_task_id and task_list:
        # 找到第一个待执行的任务并设置为当前执行任务
        for task in task_list:
            if task.get("status") == "pending":
                callback_context.state["current_executing_task_id"] = task["id"]
                current_task_id = task["id"]
                print(f"开始执行任务 {current_task_id}: {task.get('title', '')}")
                break
    
    # 检查是否包含任务完成或失败标识
    if current_task_id and task_list:
        task_completed = "任务完成" in response_text or "任务已完成" in response_text or "✅" in response_text
        task_failed = "无法完成任务" in response_text or "不能完成" in response_text or "失败" in response_text
        
        if task_completed or task_failed:
            # 更新对应任务的状态
            for task in task_list:
                if task["id"] == current_task_id:
                    task["status"] = "completed" if task_completed else "failed"
                    task["execution_result"] = response_text[:500]  # 保存前500字符的执行结果
                    status_text = "执行完成" if task_completed else "执行失败"
                    print(f"任务 {current_task_id} {status_text}")
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
    动态生成任务执行指令，包含前面步骤的上下文
    """
    # 从task_monitor传递的当前任务信息中获取任务
    # 这里我们需要从用户的调用上下文中解析当前任务
    task_list = context.state.get("confirmed_task_list", [])
    
    if not task_list:
        return "没有找到需要执行的任务列表。"
    
    # 找到第一个待执行的任务
    current_task = None
    for task in task_list:
        if task.get("status") == "pending":
            current_task = task
            break
    
    if not current_task:
        return "没有找到待执行的任务。"
    
    # 注意：在指令函数中不能修改只读的context.state
    # current_executing_task_id 将在回调函数中设置
    
    # 获取前面步骤的执行结果作为上下文
    execute_results = context.state.get("execute_result", [])
    previous_context = ""
    if execute_results:
        previous_context = "\\n\\n**前面步骤的执行结果上下文**：\\n"
        for i, result in enumerate(execute_results, 1):
            status_icon = "✅" if result.get("status") == "completed" else "❌"
            previous_context += f"步骤{i} - {result.get('task_title', '')} {status_icon}:\\n"
            previous_context += f"执行结果: {result.get('execution_result', '')[:300]}...\\n\\n"
    
    instruction = f"""现在需要执行以下任务：

**当前任务**:
- 任务标题: {current_task['title']}
- 任务描述: {current_task['description']}
- 任务ID: {current_task['id']}

{previous_context}

**执行要求**：
请按照Think-Act-Observe的循环模式来执行这个任务：

1. **🤔 思考阶段**：
   - 仔细分析当前任务的具体要求
   - 考虑前面步骤的执行结果和上下文
   - 制定合适的执行策略和步骤

2. **🚀 行动阶段**：
   - 使用合适的工具执行具体操作
   - 根据需要搜索信息、处理文件等
   - 如果需要用户补充信息，请直接询问

3. **👀 观察阶段**：
   - 评估执行结果是否满足任务要求
   - 判断任务是否已经完成
   - 决定是否需要继续循环

**可用工具**：
- braveSearch: 搜索网络信息
- fetch: 获取网页内容
- fileSystem: 文件操作
- time: 时间相关操作
- office_word: Word文档处理
- office_excel: Excel表格处理

**重要说明**：
- 如果你判断无法完成这个任务，请明确说明"无法完成任务"并详细解释原因
- 如果任务完成，请明确说明"任务已完成"并总结执行结果
- 请充分利用前面步骤的执行结果作为当前任务的输入和参考"""
    
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