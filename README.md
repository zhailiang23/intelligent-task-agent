# 智能任务处理Agent

这是一个基于ADK标准多agent架构的智能任务处理系统，能够自动判断用户任务的复杂度并分发给合适的处理器。

## 🏗️ 架构设计

采用标准的ADK多agent架构模式：

```
intelligent_task_coordinator (主Agent)
├── 简单任务 → 直接回答
└── 复杂任务 → task_decomposer_agent (子Agent)
                └── Sequential Thinking MCP工具
```

## 📁 目录结构

```
intelligent_task_agent/
├── intelligent_task/
│   ├── __init__.py
│   ├── agent.py                    # 主Agent定义
│   ├── prompt.py                   # 主Agent提示词
│   ├── shared_libraries/           # 共享库
│   │   ├── __init__.py
│   │   └── complexity_analyzer.py  # 复杂度分析器（备用）
│   └── sub_agents/                 # 子Agent目录
│       ├── __init__.py
│       └── task_decomposer/        # 任务拆解子Agent
│           ├── __init__.py
│           ├── agent.py            # 子Agent定义
│           └── prompt.py           # 子Agent提示词
├── deployment/
│   └── deploy.py                   # 部署脚本
├── pyproject.toml
└── README.md
```

## 🔍 功能特性

### 主Agent (intelligent_task_coordinator)
- **智能分发**: 基于LLM自然语言理解判断任务复杂度
- **直接处理**: 对简单任务提供即时回答
- **工具调用**: 使用AgentTool调用子agent处理复杂任务

### 子Agent (task_decomposer_agent)
- **专业拆解**: 专门处理复杂任务的详细拆解
- **结构化思考**: 使用Sequential Thinking MCP工具
- **清晰输出**: 提供结构化的任务执行计划

## 🚀 使用方法

```python
from intelligent_task.agent import root_agent

# 部署agent
# root_agent会自动判断任务复杂度并选择合适的处理方式
```

## 📋 任务类型

### 简单任务
- 概念解释 ("什么是...")
- 基础问答 ("如何...")  
- 简单查询
- 定义性问题

### 复杂任务
- 多步骤操作
- 系统开发任务
- 需要规划的项目
- 复杂分析任务

## 🔧 技术特点

1. **标准架构**: 遵循ADK多agent最佳实践
2. **模块化设计**: 清晰的代码组织和职责分离
3. **灵活扩展**: 可轻松添加新的子agent
4. **工具集成**: 无缝集成MCP工具
5. **智能分发**: 基于LLM的自然语言理解

## 📈 架构优势

- ✅ **标准化**: 符合ADK官方架构模式
- ✅ **可维护**: 清晰的模块化结构
- ✅ **可扩展**: 易于添加新功能和子agent
- ✅ **高效**: LLM驱动的智能任务分发
- ✅ **专业**: 专门的子agent处理特定任务类型