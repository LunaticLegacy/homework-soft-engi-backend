#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI功能演示脚本
展示如何使用AI任务分解功能
"""


import sys
import os
# 添加项目根目录到Python路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import asyncio
from typing import Dict, Any

from core.config import load_config
from modules.llm_fetcher.llm_fetcher import LLMFetcher
from services.ai_task_service import AITaskService
from modules.databaseman.database_manager import DatabaseManager


async def demo_ai_task():
    """演示AI任务规划功能"""
    print("\n=== AI任务规划功能演示 ===\n")
    
    # 创建LLM获取器
    config: Dict[str, Any] = load_config()

    db_manager = DatabaseManager(**config["database"])
    llm_fetcher = LLMFetcher(**config["llm"])
    task_manager = AITaskService(llm_fetcher=llm_fetcher, db_manager=db_manager)

    await task_manager.decompose_task(
        user_id="acm",
        goal="",
        workspace_id=None
    )

    running: bool = True

    while running:
        try:
            
            # 模拟用户问题
            user_question: str = input("请输入问题：\n>> ")
            
            print("正在获取AI建议...")
            
            # 构造系统提示词
            system_prompt: str = "你是一个资深的软件架构师，专门负责设计高并发的电商网站系统。"
            
            # 调用LLM，并显示结果。
            async for chunk in llm_fetcher.fetch_stream(
                msg=user_question,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=8192
            ):
                print(chunk, end="", flush=True)
            
            print("演示完成！")
            print("\n实际使用时，此功能将：")
            print("1. 接收用户问题")
            print("2. 调用LLM获取专业建议")
            print("3. 返回AI的回答")

        except KeyboardInterrupt:
            print("== 用户主动退出 ==")
            running = False
        except Exception as e:
            print(f"\n 演示过程中出现错误: {e}")
            running = False
    return

async def demo_ai_chat():
    """演示AI对话功能"""
    print("\n=== AI对话功能演示 ===\n")
    
    # 创建LLM获取器
    config: Dict[str, Any] = load_config()["llm"]

    llm_fetcher = LLMFetcher(**config)
    running: bool = True

    while running:
        try:
            
            # 模拟用户问题
            user_question: str = input("请输入问题：\n>> ")
            
            print("正在获取AI建议...")
            
            # 构造系统提示词
            system_prompt: str = "你是一个资深的软件架构师，专门负责设计高并发的电商网站系统。"
            
            # 调用LLM，并显示结果。
            async for chunk in llm_fetcher.fetch_stream(
                msg=user_question,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=8192
            ):
                print(chunk, end="", flush=True)
            
            print("演示完成！")
            print("\n实际使用时，此功能将：")
            print("1. 接收用户问题")
            print("2. 调用LLM获取专业建议")
            print("3. 返回AI的回答")

        except KeyboardInterrupt:
            print("== 用户主动退出 ==")
            running = False
        except Exception as e:
            print(f"\n 演示过程中出现错误: {e}")
            running = False
    return

def main():
    """主函数"""
    print("Stella Dream - AI任务管理助手")
    print("AI功能演示\n")
    
    # 运行演示
    asyncio.run(demo_ai_chat())
    
    print("\n=== 演示结束 ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("== 退出程序：检测到Ctrl+C ==")
        quit(1)
