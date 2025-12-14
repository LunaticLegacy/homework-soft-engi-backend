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
from typing import Dict, Any, List, Tuple

from core.config import load_config, get_settings
from modules.llm_fetcher.llm_fetcher import LLMFetcher
from services.ai_task_service import AITaskService
from modules.databaseman.database_manager import DatabaseManager

async def demo_ai_task():
    """演示AI任务规划功能"""
    print("\n=== AI任务规划功能演示 ===\n")
    
    # 创建LLM获取器
    config: Dict[str, Any] = load_config()

    db_manager = DatabaseManager(**config["database"])
    await db_manager.init_pool()
    llm_fetcher = LLMFetcher(**config["llm"])
    task_manager = AITaskService(llm_fetcher=llm_fetcher, db_manager=db_manager)

    # 添加上下文存储
    context_history: List[Tuple[str, str]] = []  # 存储 (role, content) 的元组
    running: bool = True

    while running:
        try:
            
            # 模拟用户问题
            user_question: str = input("请输入问题：\n>> ")
            
            # 将用户问题添加到上下文
            context_history.append(("user", user_question))
            
            print("正在获取AI建议...")
            
            # 构造系统提示词
            system_prompt: str = get_settings().prompts.task_decompose
            
            # 准备完整的对话历史
            messages = []
            messages.append({"role": "system", "content": system_prompt})
            for role, content in context_history:
                messages.append({"role": role, "content": content})
            
            # 调用LLM，并显示结果
            full_response = ""
            async for chunk in llm_fetcher.fetch_stream_with_context(
                messages=messages,
                temperature=0.7,
                max_tokens=8192
            ):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            # 将AI响应添加到上下文
            context_history.append(("assistant", full_response))
            
            # 显示上下文历史（可选）
            print(f"\n\n当前上下文历史包含 {len(context_history)} 条消息")
            

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
    # 添加上下文存储
    context_history: List[Tuple[str, str]] = []  # 存储 (role, content) 的元组
    running: bool = True

    while running:
        try:
            
            # 模拟用户问题
            user_question: str = input("请输入问题：\n>> ")
            
            # 将用户问题添加到上下文
            context_history.append(("user", user_question))
            
            print("正在获取AI建议...")
            
            # 构造系统提示词
            system_prompt: str = get_settings().prompts.task_decompose
            
            # 调用LLM，并显示结果
            full_response = ""
            async for chunk in llm_fetcher.fetch_stream(
                msg=user_question,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=8192
            ):
                print(chunk, end="", flush=True)
                full_response += chunk
            
            # 将AI响应添加到上下文
            context_history.append(("assistant", full_response))
            
            # 显示上下文历史（可选）
            print(f"\n\n当前上下文历史包含 {len(context_history)} 条消息")
            
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
    asyncio.run(demo_ai_task())
    
    print("\n=== 演示结束 ===")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("== 退出程序：检测到Ctrl+C ==")
        quit(1)