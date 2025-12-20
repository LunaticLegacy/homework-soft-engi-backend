import json
from typing import Dict, Any

json_message: str = """
{
  "main_goal": "原始目标（可稍作整理但不改变含义）",
  "tasks": [
    {
      "title": "主任务标题",
      "description": "主任务的详细描述",
      "estimated_time": 30,
      "estimated_time_unit": "minute",
      "priority": "medium",
      "subtasks": [
        {
          "title": "子任务标题",
          "description": "子任务详细描述",
          "estimated_time": 15,
          "estimated_time_unit": "minute",
          "priority": "medium",
          "subtasks": [
          ]
        }
      ]
    }
  ],
  "summary": "用 2–4 句话对整个任务计划进行总结，面向人类阅读"
}
"""

parser: json.JSONDecoder = json.JSONDecoder()
result: Dict[str, Any] = parser.decode(json_message)
print(result)
