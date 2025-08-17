"""
任务监控子Agent - 自动执行任务列表中的任务
"""

import json
from typing import Optional
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import llm_response as llm_response_module
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from ..task_executor.agent import task_executor_agent

MODEL = "gemini-2.0-flash"


def update_execution_results(
    callback_context: CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """
    更新任务执行结果到session.state
    """
    if not llm_response.content or not llm_response.content.parts:
        return None
        
    response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, 'text') and part.text is not None:
            response_text += part.text
    
    # 获取当前执行的任务ID
    current_task_id = callback_context.state.get("current_executing_task_id")
    task_list = callback_context.state.get("confirmed_task_list", [])
    
    if current_task_id and task_list:
        # 初始化execute_result数组如果不存在
        if "execute_result" not in callback_context.state:
            callback_context.state["execute_result"] = []
        
        # 创建执行结果记录
        execution_record = {
            "task_id": current_task_id,
            "task_title": "",
            "task_description": "",
            "execution_result": response_text,
            "status": "completed",
            "timestamp": None  # 可以添加时间戳
        }
        
        # 找到对应的任务并获取详细信息
        for task in task_list:
            if task["id"] == current_task_id:
                execution_record["task_title"] = task.get("title", "")
                execution_record["task_description"] = task.get("description", "")
                task["status"] = "completed"
                break
        
        # 检查是否任务执行失败
        if "无法完成" in response_text or "不能完成" in response_text or "失败" in response_text:
            execution_record["status"] = "failed"
            # 更新对应任务状态
            for task in task_list:
                if task["id"] == current_task_id:
                    task["status"] = "failed"
                    break
        
        # 添加到执行结果数组
        callback_context.state["execute_result"].append(execution_record)
        
        # 更新任务列表
        callback_context.state["confirmed_task_list"] = task_list
        
        print(f"任务 {current_task_id} 执行结果已保存")
    
    return None


def get_task_monitor_instruction(context) -> str:
    """
    动态生成任务监控指令 - 现在负责自动执行任务
    """
    task_list = context.state.get("confirmed_task_list", [])
    
    if not task_list:
        return "没有找到需要执行的任务列表。请先使用任务拆解功能创建任务。"
    
    # 找到第一个未完成的任务
    pending_tasks = [task for task in task_list if task.get("status") == "pending"]
    completed_tasks = [task for task in task_list if task.get("status") in ["completed", "failed"]]
    
    if not pending_tasks:
        # 所有任务都完成了
        completion_report = "🎉 恭喜！所有任务都已执行完成：\\n"
        for i, task in enumerate(completed_tasks, 1):
            status_icon = "✅" if task.get("status") == "completed" else "❌"
            completion_report += f"{i}. {status_icon} {task['title']}\\n"
        completion_report += "\\n任务执行完毕！您可以查看详细的执行结果。"
        return completion_report
    
    # 获取下一个要执行的任务
    current_task = pending_tasks[0]
    
    # 获取之前的执行结果作为上下文
    execute_results = context.state.get("execute_result", [])
    previous_context = ""
    if execute_results:
        previous_context = "\\n\\n前面步骤的执行结果上下文：\\n"
        for i, result in enumerate(execute_results, 1):
            previous_context += f"步骤{i} ({result['task_title']}): {result['execution_result'][:200]}...\\n"
    
    instruction = f"""现在开始自动执行任务列表中的下一个任务。

**当前任务**:
- 任务ID: {current_task['id']}
- 任务标题: {current_task['title']}
- 任务描述: {current_task['description']}

**执行进度**: 正在执行第 {len(completed_tasks) + 1} 个任务，共 {len(task_list)} 个任务

{previous_context}

请调用task_executor_agent来执行这个任务。task_executor会使用Think-Act-Observe模式来完成任务。

如果task_executor判断无法完成任务，将终止整个执行流程并向用户说明情况。"""
    
    return instruction


# 创建任务监控agent，现在集成task_executor作为子agent
task_monitor_agent = Agent(
    name="task_monitor_agent", 
    model=MODEL,
    description="任务监控和自动执行器，负责循环执行任务列表中的每个任务",
    instruction=get_task_monitor_instruction,
    tools=[AgentTool(agent=task_executor_agent)],
    after_model_callback=update_execution_results,
)