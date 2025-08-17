"""
任务拆解子Agent - 专门处理复杂任务的拆解
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


def save_confirmed_tasks_to_state(
    callback_context: CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """
    检查LLM响应中是否包含用户确认的任务列表，并将其保存到session.state中
    """
    if not llm_response.content or not llm_response.content.parts:
        return None
        
    response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, 'text') and part.text is not None:
            response_text += part.text
    
    # 检查是否包含确认的任务列表（查找"## 执行步骤"部分）
    if "## 执行步骤" in response_text:
        # 提取执行步骤
        steps_section = response_text.split("## 执行步骤")[1]
        
        # 使用正则表达式提取步骤
        step_pattern = r'\d+\.\s*\*\*([^*]+)\*\*:\s*([^\n]+)'
        matches = re.findall(step_pattern, steps_section)
        
        if matches:
            # 构建任务列表
            tasks = []
            for i, (step_title, step_description) in enumerate(matches, 1):
                task = {
                    "id": i,
                    "title": step_title.strip(),
                    "description": step_description.strip(),
                    "status": "pending",  # 初始状态为待完成
                    "confirmed": True  # 标记为用户已确认
                }
                tasks.append(task)
            
            # 保存到session.state
            callback_context.state["confirmed_task_list"] = tasks
            callback_context.state["task_decomposition_complete"] = True
            
            print(f"任务列表已保存到session.state，共{len(tasks)}个任务")
    
    return None


task_decomposer_agent = Agent(
    name="task_decomposer_agent",
    model=MODEL,
    description="专门用于将复杂任务拆解为可执行的步骤序列",
    instruction=prompt.TASK_DECOMPOSER_PROMPT,
    tools=[
        MCPToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command='npx',
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-sequential-thinking"
                    ],
                ),
            ),
        )
    ],
    after_model_callback=save_confirmed_tasks_to_state,
)