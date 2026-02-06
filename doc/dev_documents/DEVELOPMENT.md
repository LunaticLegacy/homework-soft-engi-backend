# 后端开发文档

## 1. 项目概述

这是一个基于 Python 和 FastAPI 框架的后端项目。

主要功能是任务管理，集成了 AI 功能（任务分解、任务建议、AI 对话）

项目采用模块化开发，支持异步数据库操作和缓存管理。

## 2. 技术栈

- 开发；`Python 3.13.5`
- 后端框架：`FastAPI`
- 数据库：`PostgreSQL`
- 缓存：`Redis`
- ASGI 服务器：`Uvicorn`，基于 FastAPI

## 3. 项目概述

项目结构：

```
backend/
├── api/                    # API接口定义
│   └── v1/                 # V1版本API，已弃用
├── core/                   # 核心功能模块
├── routes/                 # 路由定义
├── services/               # 业务逻辑服务
├── modules/                # 可复用模块
├── sql/                    # SQL脚本
├── tests/                  # 测试代码
├── llm_prompts/            # LLM提示词
├── demos/                  # 示例代码
└── doc/                    # 文档
```

## 4. 配置

项目使用[settings.py](settings.py) 统一管理配置，包含：

- ServerSettings：服务器配置（host、port、workers 等）
- DatabaseSettings：数据库连接配置
- RedisSettings：Redis 连接配置
- LLMSettings：大语言模型 API 配置
- PromptsSettings：AI 提示词配置

## 5. 启动项目

### 5.1 前置条件

注意：本项目在运行前，需手动启动`PostgreSQL`和`Redis`。

对 PostgreSQL 而言，在文件夹`/sql`内有一系列`.sql`后缀文件。请在主程序启动前，使用该文件组，建立本项目所需建立的数据库程序。

### 5.2 主程序启动

依赖安装：

```
pip install -r ./requirements.txt
```

启动命令：

```
python app.py
```

## 6. 核心功能模块

### 6.1 数据库管理

使用类`DatabaseManager`管理异步数据库连接池，支持 PostgreSQL 异步操作。

在应用生命周期中自动初始化和清理连接，但获取链接需要手动获取并手动释放。

> 未来将会改为使用`async with`上下文的结构。

### 6.2 缓存管理

使用 Redis 作为缓存系统，`redis_manager` 管理 Redis 连接池。

### 6.3 AI 功能

集成大语言模型，支持任务分解和任务建议。通过 [ai_routes.py](routes/ai_routes.py) 提供 AI 相关 API。

## 7. API 接口

### 7.1 API 版本管理

/api/v1/ - V1 版本 API 接口，包含用户管理、状态检查等基础功能。

> 该 API 将在下个版本被废弃，并转入正式版本。

### 7.2 路由模块

```
main_routes.py - 主路由
user_routes.py - 用户相关路由
ai_routes.py - AI功能路由
workspace_routes.py - 工作空间路由
project_routes.py - 项目路由
task_routes.py - 任务路由
```

## 8. 业务服务层

```
user_service.py - 用户服务
workspace_service.py - 工作空间服务
project_service.py - 项目服务
task_service.py - 任务服务
ai_task_service.py - AI任务服务
```

## 9. 代码规范

### 9.1 类型注解

```python
def example_function(a: int, b: float) -> float:
    """
    乘法操作。
    Args:
        a (int): 第一个数字。
        b (float): 第二个数字。
    Returns:
        (float): 乘积。
    """
    return a * b
```

### 9.2 函数文档

使用 Google 风格的文档字符串，包括参数和返回值说明。

### 9.3 命名规范

- 类名：开头大写，如 `DatabaseManager`
- 函数名：全小写，单词间用下划线分隔，如 `function_in_class`
- 私有函数：在函数名前加一个下划线，如 `_a_private_function`

## 10. 测试规范

使用`pytest`进行测试。测试文件放在 tests 目录下，且文件名必须以 test 开头。

## 11. Docker 部署

项目包含 Dockerfile 和 docker-compose.yml，以用于部署后端数据库服务器。本项目在运行千需启动后端服务器。
