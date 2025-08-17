# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 环境和依赖管理

使用conda管理Python环境：
```bash
# 激活环境
conda activate manus-agent

# 安装依赖
pip install -e .

# 安装MCP工具（必需）
npm install -g @modelcontextprotocol/server-sequential-thinking
```

## 开发和测试命令

```bash
# 运行主要的系统测试
python test_refactored_system.py

# 运行任务监控修复测试
python test_task_monitor_fix.py

# 测试连接
python test_connection.py

# 部署agent系统
python deployment/deploy.py

# 启动ADK web服务
adk web --no-reload
```

## 核心架构

这是一个基于Google ADK (Agent Development Kit) 的多agent智能任务处理系统，采用标准的主-子agent架构模式：

### 主要组件

1. **主Agent** (`intelligent_task/agent.py`)
   - `intelligent_task_coordinator`: 智能任务分发器
   - 基于LLM判断任务复杂度并路由到合适的处理器
   - 简单任务直接回答，复杂任务分发给子agent

2. **子Agents** (`intelligent_task/sub_agents/`)
   - `task_decomposer_agent`: 复杂任务拆解器，使用Sequential Thinking MCP工具
   - `task_monitor_agent`: 任务监控器，逐个询问用户任务完成状态

3. **状态管理**
   - 使用session.state保存任务列表和状态
   - 任务拆解结果以JSON格式存储：`{"id": int, "title": str, "description": str, "status": "pending|completed"}`

### 关键机制

**AgentTool模式**: 主agent使用AgentTool调用子agents，符合ADK最佳实践

**回调函数**: 
- `save_confirmed_tasks_to_state()`: 自动提取和保存任务拆解结果
- `process_user_response_callback()`: 处理用户对任务完成状态的回答

**MCP集成**: task_decomposer_agent集成Sequential Thinking MCP工具进行深度思考

## 工作流程

1. **任务接收**: 用户提交任务到主agent
2. **复杂度判断**: 主agent基于LLM判断任务类型
3. **任务分发**: 
   - 简单任务 → 直接回答
   - 复杂任务 → task_decomposer_agent拆解
   - 监控请求 → task_monitor_agent询问状态
4. **状态更新**: 通过回调函数自动更新session.state

## 文件结构要点

```
intelligent_task/
├── agent.py                    # 主agent定义，包含AgentTool集成
├── prompt.py                   # 主agent提示词，定义任务分发逻辑
├── shared_libraries/           # 共享组件
│   ├── complexity_analyzer.py  # 备用复杂度分析器
│   └── warning_config.py       # 警告过滤配置
└── sub_agents/                 # 子agent目录
    ├── task_decomposer/        # 任务拆解子agent
    │   ├── agent.py            # 包含MCP工具集成和状态保存回调
    │   └── prompt.py           # Sequential Thinking提示词
    └── task_monitor/           # 任务监控子agent
        ├── agent.py            # 包含用户交互和状态更新逻辑
        └── prompt.py           # 任务监控提示词
```

## 调试和故障排除

常见问题：
- **导入错误**: 确保所有`__init__.py`文件正确导出agents
- **状态更新失败**: 检查callback函数中的状态操作，避免在只读context中修改状态
- **MCP工具连接**: 确保Sequential Thinking MCP服务正确安装和配置

## ADK特定注意事项

- 使用`google.genai.types.Content`和`types.Part`构造Event内容
- 状态修改只能在callback函数中进行，instruction函数中的context.state是只读的
- AgentTool会自动处理子agent的调用和结果传递
- 模型统一使用"gemini-2.0-flash"