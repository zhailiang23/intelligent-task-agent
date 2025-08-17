"""
智能任务Agent - 主控制器，包含任务复杂度判断和分发功能
"""

# 配置警告过滤器
from .shared_libraries.warning_config import configure_warnings
configure_warnings()

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.task_decomposer.agent import task_decomposer_agent
from .sub_agents.task_monitor.agent import task_monitor_agent

MODEL = "gemini-2.0-flash"

# 主Agent - 使用AgentTool模式调用子agent
intelligent_task_coordinator = LlmAgent(
    name="intelligent_task_coordinator",
    model=MODEL,
    description=(
        "智能任务处理协调器，负责判断任务复杂度并分发给合适的处理器。"
        "对于简单任务直接回答，对于复杂任务调用任务拆解子agent进行处理。"
    ),
    instruction=prompt.MAIN_AGENT_PROMPT,
    output_key="task_analysis_result",
    tools=[
        AgentTool(agent=task_decomposer_agent),
        AgentTool(agent=task_monitor_agent),
    ],
)

# 设置为根agent
root_agent = intelligent_task_coordinator