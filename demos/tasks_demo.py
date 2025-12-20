#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
任务功能脚本
"""

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from modules.databaseman.database_manager import DatabaseManager
from core.config import load_config
from services import WorkspaceService, ProjectService, TaskService

from typing import Any, Dict, Optional
from services.models.task_data_model import *

async def test():

    config: Dict[str, Any] = load_config()
    database: DatabaseManager = DatabaseManager(**config["database"])
    await database.init_pool()

    # 我需要fetch到一个东西

    ts: TaskService = TaskService(database)

    json_message: str = """

    """

    result: Optional[TaskListInfo] = await ts.create_task_by_json(
        project_id="00000000-0000-0000-0000-000000000000",
        workspace_id="00000000-0000-0000-0000-000000000000",
        creator_id="00000000-0000-0000-0000-000000000000",
        json_message=json_message
    )

    # result: Optional[Dict[str, Any]] = await ts.get_task_tree(
    #     task_id="3e42fb09-d2db-432d-91fa-8a0b593c603b"
    # )

    print(result)

# 启动
asyncio.run(test())
