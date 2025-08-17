"""
任务监控子Agent - 专门处理任务完成状态的监控和更新
"""

from typing import Optional, AsyncGenerator
from google.adk.agents import BaseAgent, LoopAgent, Agent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event, EventActions
from google.adk.models import llm_response as llm_response_module
from google.genai import types

from . import prompt

MODEL = "gemini-2.0-flash"


class TaskInquiryAgent(BaseAgent):
    """
    任务询问Agent - 专门负责询问用户特定任务的完成状态
    这个Agent会向用户询问当前任务是否完成，然后等待用户真实回答
    """
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 获取当前需要询问的任务
        current_task_id = ctx.session.state.get("current_asking_task_id")
        task_list = ctx.session.state.get("confirmed_task_list", [])
        
        if current_task_id is None or not task_list:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model", 
                    parts=[types.Part(text="没有找到需要询问的任务。")]
                )
            )
            return
        
        # 找到对应的任务
        current_task = None
        for task in task_list:
            if task["id"] == current_task_id:
                current_task = task
                break
        
        if current_task is None:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="没有找到指定的任务。")]
                )
            )
            return
        
        # 询问用户任务是否完成
        inquiry_message = f"""请问任务「{current_task['title']}」（{current_task['description']}）是否已经完成？

请明确回答：已完成 或 未完成"""
        
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part(text=inquiry_message)]
            )
        )


class UserResponseProcessor(BaseAgent):
    """
    用户回答处理Agent - 处理用户对任务完成状态的回答
    这个Agent会读取用户的输入并相应更新任务状态
    """
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        # 获取用户输入
        user_input = ""
        if ctx.user_content and ctx.user_content.parts:
            for part in ctx.user_content.parts:
                if hasattr(part, 'text') and part.text is not None:
                    user_input += part.text
        
        current_task_id = ctx.session.state.get("current_asking_task_id")
        task_list = ctx.session.state.get("confirmed_task_list", [])
        
        if not user_input or current_task_id is None or not task_list:
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="无法处理用户回答，请重新回答。")]
                )
            )
            return
        
        # 检查用户的回答
        user_input_lower = user_input.lower()
        if "已完成" in user_input or "完成了" in user_input or "完成" in user_input or "yes" in user_input_lower or "是" in user_input:
            # 更新对应任务的状态
            for task in task_list:
                if task["id"] == current_task_id:
                    task["status"] = "completed"
                    response_message = f"✅ 任务「{task['title']}」已标记为完成。"
                    break
            else:
                response_message = "未找到对应的任务。"
            
            # 更新session.state
            ctx.session.state["confirmed_task_list"] = task_list
            
        elif "未完成" in user_input or "没完成" in user_input or "no" in user_input_lower or "否" in user_input:
            # 任务保持pending状态
            current_task = None
            for task in task_list:
                if task["id"] == current_task_id:
                    current_task = task
                    break
            
            if current_task:
                response_message = f"📝 任务「{current_task['title']}」仍在进行中，请在完成后告知我。"
            else:
                response_message = "未找到对应的任务。"
        else:
            # 无法识别的回答
            response_message = "抱歉，我无法理解您的回答。请明确回答「已完成」或「未完成」。"
        
        yield Event(
            author=self.name,
            content=types.Content(
                role="model",
                parts=[types.Part(text=response_message)]
            )
        )


class TaskStatusChecker(BaseAgent):
    """检查是否还有未完成的任务，决定是否继续循环"""
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        task_list = ctx.session.state.get("confirmed_task_list", [])
        
        if not task_list:
            # 没有任务列表，结束循环
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="没有找到任务列表，结束监控。")]
                )
            )
            return
        
        # 查找第一个未完成的任务
        next_pending_task = None
        for task in task_list:
            if task["status"] == "pending":
                next_pending_task = task
                break
        
        if next_pending_task is None:
            # 所有任务都完成了
            completed_tasks = [task for task in task_list if task["status"] == "completed"]
            completion_report = "🎉 恭喜！所有任务都已完成：\n"
            for i, task in enumerate(completed_tasks, 1):
                completion_report += f"{i}. ✅ {task['title']}\n"
            completion_report += "任务执行完毕！"
            
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=completion_report)]
                )
            )
        else:
            # 还有未完成的任务，设置当前询问的任务ID并继续循环
            ctx.session.state["current_asking_task_id"] = next_pending_task["id"]
            yield Event(
                author=self.name,
                content=types.Content(
                    role="model",
                    parts=[types.Part(text=f"准备询问下一个任务：{next_pending_task['title']}")]
                )
            )


# 创建各个子agent实例
task_inquiry_agent = TaskInquiryAgent(name="task_inquiry_agent")
user_response_processor = UserResponseProcessor(name="user_response_processor")
task_status_checker = TaskStatusChecker(name="task_status_checker")

def get_task_monitor_instruction(context) -> str:
    """
    动态生成任务监控指令
    """
    task_list = context.state.get("confirmed_task_list", [])
    
    if not task_list:
        return "没有找到需要监控的任务列表。请先使用任务拆解功能创建任务。"
    
    # 找到第一个未完成的任务
    pending_tasks = [task for task in task_list if task.get("status") == "pending"]
    completed_tasks = [task for task in task_list if task.get("status") == "completed"]
    
    if not pending_tasks:
        # 所有任务都完成了
        completion_report = "🎉 恭喜！所有任务都已完成：\n"
        for i, task in enumerate(completed_tasks, 1):
            completion_report += f"{i}. ✅ {task['title']}\n"
        completion_report += "\n任务执行完毕！如果您还有其他任务需要处理，请随时告诉我。"
        return completion_report
    
    # 还有未完成的任务，询问第一个
    current_task = pending_tasks[0]
    
    # 注意：不能在这里修改state，因为context.state是只读的
    # 我们将任务ID包含在指令中，让回调函数处理状态更新
    
    inquiry_message = f"""我来帮您检查任务完成情况。

请问任务「{current_task['title']}」是否已经完成？
任务描述：{current_task['description']}
任务ID：{current_task['id']}

请回答：
- 如果已完成，请说「已完成」
- 如果未完成，请说「未完成」

当前进度：已完成 {len(completed_tasks)}/{len(task_list)} 个任务"""
    
    return inquiry_message


def process_user_response_callback(
    callback_context: CallbackContext,
    llm_response: llm_response_module.LlmResponse,
) -> Optional[llm_response_module.LlmResponse]:
    """
    处理用户对任务完成状态的回答
    """
    if not llm_response.content or not llm_response.content.parts:
        return None
    
    # 获取LLM的回复内容（这里包含了对用户输入的理解）
    response_text = ""
    for part in llm_response.content.parts:
        if hasattr(part, 'text') and part.text is not None:
            response_text += part.text
    
    # 获取任务列表
    task_list = callback_context.state.get("confirmed_task_list", [])
    if not task_list:
        return None
    
    # 从响应中寻找任务ID（LLM的回复中应该包含了任务ID信息）
    # 或者我们找到第一个未完成的任务作为当前任务
    current_task_id = None
    for task in task_list:
        if task.get("status") == "pending":
            current_task_id = task["id"]
            break
    
    if current_task_id is None:
        return None
    
    # 检查回复中是否表明任务已完成
    # 这里我们假设LLM会根据用户输入生成相应的回复
    if "已完成" in response_text or "完成了" in response_text or "完成" in response_text:
        # 更新对应任务的状态
        for task in task_list:
            if task["id"] == current_task_id:
                task["status"] = "completed"
                print(f"任务 {current_task_id} 已标记为完成")
                break
        
        # 更新session.state
        callback_context.state["confirmed_task_list"] = task_list
    
    return None


# 创建任务监控agent
task_monitor_agent = Agent(
    name="task_monitor_agent", 
    model=MODEL,
    description="监控任务完成状态，逐个询问用户每个任务是否完成",
    instruction=get_task_monitor_instruction,
    after_model_callback=process_user_response_callback,
)