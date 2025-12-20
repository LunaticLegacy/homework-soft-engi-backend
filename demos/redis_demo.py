#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from modules.redisman import RedisManager
from core.config import load_config
import pytest

import asyncio

from typing import Dict, Any

async def test_func():
    config_redis: Dict[str, Any] = load_config()
    redisman: RedisManager = RedisManager(**config_redis["redis"])

    # 初始化连接池
    await redisman.init_pool()

    # 测试连接
    assert await redisman.ping(), "❌ Redis连接失败"
    print("✅ Redis连接成功")

    # 测试字符串存取
    key1, value1 = "test:string", "喵喵喵"
    await redisman.set(key1, value1, expire=5)
    result1 = await redisman.get(key1)
    assert result1 == value1, "❌ 普通字符串存取失败"
    print(f"✅ 字符串测试通过: {result1}")

    # 测试复杂数据（JSON）
    key2, data = "test:json", {"name": "白毛猫娘", "age": 3, "skills": ["sleep", "purr"]}
    await redisman.set(key2, data)
    result2 = await redisman.get(key2)
    assert result2 == data, "❌ JSON 序列化失败"
    print(f"✅ JSON数据测试通过: {result2}")

    # 测试Pickle对象
    import datetime
    key3, obj = "test:pickle", datetime.datetime.now()
    await redisman.set(key3, obj, serialize="pickle")
    result3 = await redisman.get(key3, deserialize="pickle")
    assert isinstance(result3, datetime.datetime), "❌ Pickle 序列化失败"
    print(f"✅ Pickle测试通过: {result3}")

    # 测试 exists / delete
    exists = await redisman.exists(key1, key2)
    print(f"存在键数量: {exists}")
    deleted = await redisman.delete(key1, key2, key3)
    print(f"删除键数量: {deleted}")

    # 关闭连接池
    await redisman.close_pool()
    print("✅ Redis连接关闭完毕")



if __name__ == "__main__":
    asyncio.run(test_func())
