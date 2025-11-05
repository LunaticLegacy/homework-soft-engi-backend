# AI功能使用示例

## 1. 功能概述

本系统集成了基于大语言模型（LLM）的AI功能，主要包括：
1. 任务分解：将用户的大目标自动分解为可执行的子任务
2. 任务建议：为特定任务提供完成建议和技巧
3. AI对话：与AI进行自然语言对话

## 2. API接口说明

### 2.1 任务分解接口

**接口地址**：`POST /ai/decompose`

**请求参数**：
```json
{
  "goal": "在6个月内学会Python并找到相关工作",
  "user_id": "uuid-string",
  "workspace_id": "uuid-string"  // 可选
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "main_goal": "在6个月内学会Python并找到相关工作",
    "tasks": [
      {
        "title": "学习Python基础知识",
        "description": "掌握Python语法、数据结构、函数等基础知识",
        "estimated_minutes": 1200,
        "priority": "high",
        "subtasks": [
          {
            "title": "学习变量和数据类型",
            "description": "了解Python中的各种变量类型和数据结构",
            "estimated_minutes": 120
          },
          {
            "title": "学习控制结构",
            "description": "掌握条件语句和循环语句的使用",
            "estimated_minutes": 180
          }
        ]
      }
    ]
  },
  "message": "任务分解成功"
}
```

### 2.2 任务建议接口

**接口地址**：`POST /ai/suggestions/{task_id}`

**请求参数**：
```json
{
  "user_id": "uuid-string"
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "task_title": "学习Python基础知识",
    "suggestions": [
      {
        "title": "制定学习计划",
        "description": "合理安排学习时间，循序渐进",
        "steps": [
          "每天安排2小时学习时间",
          "每周完成一个小项目",
          "每月进行一次总结回顾"
        ]
      }
    ],
    "resources": [
      {
        "title": "Python官方文档",
        "url": "https://docs.python.org/"
      }
    ],
    "tips": [
      "多动手实践，理论结合实际",
      "加入Python学习社区，与他人交流"
    ]
  },
  "message": "建议获取成功"
}
```

### 2.3 AI对话接口

**接口地址**：`POST /ai/chat`

**请求参数**：
```json
{
  "message": "如何快速掌握Python的面向对象编程？",
  "user_id": "uuid-string",
  "system_prompt": "你是一个专业的Python编程导师"  // 可选
}
```

**响应示例**：
```json
{
  "success": true,
  "data": {
    "response": "掌握Python面向对象编程的关键点包括：1. 理解类和对象的概念..."
  },
  "message": "对话成功"
}
```

## 3. 配置说明

AI功能需要在`config.json`中配置LLM相关参数：

```json
{
  "llm": {
    "api_url": "https://api.deepseek.com",
    "api_key": "your-api-key-here",
    "model": "deepseek-reasoner"
  }
}
```

## 4. 使用流程

1. 用户在前端输入大目标
2. 前端调用`/ai/decompose`接口，将目标发送到后端
3. 后端使用LLM将大目标分解为具体任务
4. 系统将分解结果保存到数据库
5. 前端展示分解后的任务列表供用户查看和管理

## 5. 注意事项

1. 需要在环境变量或配置文件中设置正确的API密钥
2. 根据实际使用的LLM平台调整API URL和模型名称
3. 注意控制API调用频率，避免超出配额限制
4. 对AI返回的结果进行适当验证和处理