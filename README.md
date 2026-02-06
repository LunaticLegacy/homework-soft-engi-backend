<div align="center">

# 🚀 星之梦 任务管理助手 · 后端服务

[![GitHub stars](https://img.shields.io/github/stars/LunaticLegacy/homework-soft-engi-backend?style=social)](https://github.com/LunaticLegacy/homework-soft-engi-backend/stargazers)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](#-docker-部署推荐)

> 🧠 一个基于LLM的任务管理助手（后端）：使用LLM辅助，对任务进行分解，并管理。

[**功能特性**](#-功能特性) • [**快速开始**](#-快速开始) • [**部署指南**](docs/DEPLOY.md) • [**开发文档**](docs/DEVELOPMENT.md) • [**更新日志**](docs/CHANGELOG.md)

</div>

---

## ✨ 本仓库功能特性

### 🎯 核心能力

- **统一API网关**：为前端提供稳定的接口、统一错误码与返回结构
- **鉴权与权限**：登录 / Token / 角色权限（按你的实现保留）
- **业务模块化**：模块按目录组织，便于多人协作与扩展
- **可观测性**：结构化日志 + 健康检查（建议上线必备）
- **Docker 化**：本地/线上一致运行环境，降低部署成本

### 🧩 技术栈

- Web Framework：FastAPI
- Database：PostgreSQL（使用asyncpg开发）
- Cache：Redis
- DevOps：Docker

---

## 🚀 快速开始

> 推荐使用本地运行——本服务一开始作为服务器专用服务准备。

### 方式一：本地运行（开发推荐）

#### 1) 准备环境

- Python 3.10+
- Docker
  - PostgreSQL / Redis

#### 2) 安装依赖

```bash
# 任选一种方式（按你项目实际）
pip install -r requirements.txt
# 或
poetry install
```

#### 3) 设置参数

在`settings.py`里设置自己使用的LLM。

#### 4) 启动前端内容

> 该应用必须前后端均启动才可用。

## 📁 项目结构

```
homework-soft-engi-backend/
├── api/                    # API接口定义
│   └── v1/                 # V1版本API，已弃用
├── core/                   # 核心功能模块
├── demos/                  # 示例代码
├── doc/                    # 文档
├── docker/                 # 容器配置
├── llm_prompts/            # LLM提示词
├── modules/                # 可复用的关键模块（包含SQL、Redis和LLM）
├── routes/                 # 路由定义
├── services/               # 业务逻辑服务
├── sql/                    # SQL脚本
├── tests/                  # 测试代码
├── app.py                  # 运行用程序
├── requirements.txt        # 需要的包体
└── settings.py             # 运行时设置
```

## 🗺️ Roadmap

- 统一错误提示与全局异常兜底
- E2E / 关键链路回归（可选）
- 多端适配清单（H5/小程序差异点文档化）

## 🤝 贡献

欢迎提交 Issue / Pull Request！

开发文档：[doc/dev_documents/DEVELOPMENT.md](doc/dev_documents/DEVELOPMENT.md)

## 📄 License

[MIT License](LICENSE)
