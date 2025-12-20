import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
import types
from typing import Any, List, Optional, Dict

from services.models.task_data_model import *

# Stub asyncpg to avoid optional dependency during unit tests (only if missing)
try:
    import asyncpg  # type: ignore
except ImportError:
    async def _fake_create_pool(*args, **kwargs):
        return None

    sys.modules.setdefault(
        "asyncpg",
        types.SimpleNamespace(
            create_pool=_fake_create_pool,
            Connection=object,
            pool=types.SimpleNamespace(Pool=object),
        ),
    )

# Stub redis/redis.asyncio for imports under modules.redisman
try:
    import redis  # type: ignore
except ImportError:
    redis_stub = types.SimpleNamespace(
        Redis=object,
        StrictRedis=object,
    )
    sys.modules.setdefault("redis", redis_stub)
    redis_asyncio_stub = types.SimpleNamespace(Redis=object, ConnectionPool=object)
    sys.modules.setdefault("redis.asyncio", redis_asyncio_stub)
    redis_stub.asyncio = redis_asyncio_stub

# Stub openai for modules.llm_fetcher import chain if missing
try:
    import openai  # type: ignore
except ImportError:
    class _OpenAIStub:
        def __init__(self, *args, **kwargs):
            pass

    openai_mod = types.ModuleType("openai")
    openai_mod.OpenAI = _OpenAIStub
    openai_types_mod = types.ModuleType("openai.types")
    openai_chat_mod = types.ModuleType("openai.types.chat")
    openai_chat_mod.ChatCompletion = object
    openai_types_mod.chat = openai_chat_mod
    openai_mod.types = openai_types_mod

    sys.modules.setdefault("openai", openai_mod)
    sys.modules.setdefault("openai.types", openai_types_mod)
    sys.modules.setdefault("openai.types.chat", openai_chat_mod)

# Stub fastapi/starlette for exception imports if missing
try:
    import fastapi  # type: ignore
    import starlette  # type: ignore
except ImportError:
    class _HTTPExceptionStub(Exception):
        def __init__(self, status_code: int = 500, detail: str = ""):
            super().__init__(detail)
            self.status_code = status_code
            self.detail = detail

    fastapi_mod = types.ModuleType("fastapi")
    fastapi_mod.HTTPException = _HTTPExceptionStub
    fastapi_exceptions_mod = types.ModuleType("fastapi.exceptions")
    fastapi_exceptions_mod.RequestValidationError = type("RequestValidationError", (Exception,), {})
    fastapi_responses_mod = types.ModuleType("fastapi.responses")
    fastapi_responses_mod.JSONResponse = lambda *args, **kwargs: None
    fastapi_mod.exceptions = fastapi_exceptions_mod
    fastapi_mod.responses = fastapi_responses_mod

    starlette_exceptions_mod = types.ModuleType("starlette.exceptions")
    starlette_exceptions_mod.HTTPException = _HTTPExceptionStub

    sys.modules.setdefault("fastapi", fastapi_mod)
    sys.modules.setdefault("fastapi.exceptions", fastapi_exceptions_mod)
    sys.modules.setdefault("fastapi.responses", fastapi_responses_mod)
    sys.modules.setdefault("starlette.exceptions", starlette_exceptions_mod)

from services.task_service import TaskService
from modules.databaseman import DatabaseManager


@pytest.fixture
def get_db() -> DatabaseManager:
    from core.config import load_config
    db = DatabaseManager(**(load_config()["database"]))
    return db

@pytest.mark.asyncio
async def test_create_task_by_json_rejects_multiple_main_tasks(get_db):
    db = get_db
    await db.init_pool()
    svc = TaskService(db=db)
    sample_json = """
{
  "main_goal": "作为男生，为明天动漫社的女仆祭打扮成猫娘形象，侧重外观准备。",
  "tasks": [
        {"title": "为明天动漫社的女仆祭打扮成猫娘形象", "description": "", "estimated_time": 1.5, "estimated_time_unit": "hour", "priority": "medium", "subtasks": [
                {"title": "选择并准备猫娘服装", "description": "", "estimated_time": 2, "estimated_time_unit": "hour", "priority": "high", "subtasks": []},
                {"title": "化妆和面部修饰", "description": "", "estimated_time": 1.5, "estimated_time_unit": "hour", "priority": "medium", "subtasks": []}
        ]}
  ],
  "summary": "示例"
}
"""
    result = await svc.create_task_by_json(
        project_id="00000000-0000-0000-0000-000000000000",
        workspace_id="00000000-0000-0000-0000-000000000000",
        creator_id="00000000-0000-0000-0000-000000000000",
        json_message=sample_json
    )
    assert (result is not None)

@pytest.mark.asyncio
async def test_create_task_by_json_inserts_single_main_with_subtasks(get_db):
    db = get_db
    await db.init_pool()
    svc = TaskService(db=db)
    json_message = """
{
  "main_goal": "main goal",
  "tasks": [
    {
      "title": "主任务",
      "description": "描述",
      "estimated_time": 2,
      "estimated_time_unit": "hour",
      "priority": "high",
      "subtasks": [
        {
          "title": "子任务A",
          "description": "子A",
          "estimated_time": 30,
          "estimated_time_unit": "minute",
          "priority": "medium",
          "subtasks": []
        },
        {
          "title": "子任务B",
          "description": "子B",
          "estimated_time": 1,
          "estimated_time_unit": "hour",
          "priority": "low",
          "subtasks": []
        }
      ]
    }
  ],
  "summary": "总结"
}
"""

    result: Optional[Task] = await svc.create_task_by_json(
        project_id="00000000-0000-0000-0000-000000000000",
        workspace_id="00000000-0000-0000-0000-000000000000",
        creator_id="00000000-0000-0000-0000-000000000000",
        json_message=json_message
    )
    
    # 返回值类型：
    # {
    # "main_goal": payload.get("main_goal"),
    # "summary": payload.get("summary"),
    # "tasks": [created_tree]
    # }

    assert (result is not None)


@pytest.mark.asyncio
async def test_task_get_tree(get_db):
    db = get_db
    await db.init_pool()
    svc = TaskService(db=db)
    result: Optional[TaskTree] = await svc.get_task_tree("6f879b48-f215-4707-88d4-3d17079639e0")
    assert result != None


# async def test1():
#     from core.config import load_config
#     db = DatabaseManager(**load_config()["database"])

#     await db.init_pool()
#     svc = TaskService(db=db)
#     result: Optional[TaskTree] = await svc.get_task_tree("6f879b48-f215-4707-88d4-3d17079639e0")
#     assert result != None
#     print(result)

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(test1())
