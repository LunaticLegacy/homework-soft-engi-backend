from __future__ import annotations

import os
from dataclasses import MISSING, dataclass, field, fields, is_dataclass
from functools import lru_cache
from typing import Optional, Any, Iterable, Tuple


def desc_field(
    *,
    desc: str,
    default: Any = MISSING,
    default_factory: Any = MISSING,
):
    """
    dataclass 字段包装：给字段挂一个描述信息 metadata['desc']。
    """
    if default is not MISSING and default_factory is not MISSING:
        raise ValueError("desc_field: cannot set both default and default_factory")
    if default is not MISSING:
        return field(default=default, metadata={"desc": desc})
    if default_factory is not MISSING:
        return field(default_factory=default_factory, metadata={"desc": desc})
    return field(metadata={"desc": desc})


def _env(name: str, default: str) -> str:
    """读取环境变量，未设置则返回 default。"""
    v = os.getenv(name)
    return default if v is None or v == "" else v


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    return default if v is None or v == "" else int(v)


def _env_bool(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None or v == "":
        return default
    return v.strip().lower() in {"1", "true", "yes", "y", "on"}


def _read_text(path: str) -> str:
    """
    读取文本文件。
    - 建议提示词文件缺失就直接报错，避免线上默默使用空提示词导致行为异常。
    """
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


# ----------------------------
# Settings Models (with desc)
# ----------------------------

@dataclass(frozen=True)
class ServerSettings:
    host: str = desc_field(desc="服务监听地址；0.0.0.0 表示监听所有网卡", default="0.0.0.0")
    port: int = desc_field(desc="服务监听端口", default=8000)
    reload: bool = desc_field(desc="是否热重载；开发 True，生产建议 False", default=True)
    workers: int = desc_field(desc="Worker 数；reload=True 时通常不启用多 worker", default=10)


@dataclass(frozen=True)
class SSLSettings:
    keyfile: Optional[str] = desc_field(desc="SSL 私钥文件路径；不启用 HTTPS 可为 None", default="certs/key.pem")
    certfile: Optional[str] = desc_field(desc="SSL 证书文件路径；不启用 HTTPS 可为 None", default="certs/cert.pem")


@dataclass(frozen=True)
class DatabaseSettings:
    db_url: str = desc_field(desc="数据库地址（host 或 DSN 前缀）；你当前写的是 host", default="127.0.0.1")
    db_username: str = desc_field(desc="数据库用户名", default="luna")
    db_password: str = desc_field(desc="数据库密码（生产环境务必用环境变量注入）", default="lunamoon")
    db_database_name: str = desc_field(desc="数据库名", default="luna")
    db_port: int = desc_field(desc="数据库端口", default=1980)
    minconn: int = desc_field(desc="连接池最小连接数", default=1)
    maxconn: int = desc_field(desc="连接池最大连接数", default=20)


@dataclass(frozen=True)
class RedisSettings:
    host: str = desc_field(desc="Redis 地址", default="localhost")
    port: int = desc_field(desc="Redis 端口", default=1981)
    db: int = desc_field(desc="Redis DB index", default=0)
    password: Optional[str] = desc_field(desc="Redis 密码；无密码可为 None", default=None)


@dataclass(frozen=True)
class LLMSettings:
    api_url: str = desc_field(desc="LLM API Base URL", default="https://api.deepseek.com")
    api_key: str = desc_field(desc="LLM API Key（务必用环境变量注入；不要写进仓库）", default="")
    model: str = desc_field(desc="LLM 模型名称", default="deepseek-reasoner")


@dataclass(frozen=True)
class PromptsSettings:
    task_decompose: str = desc_field(desc="任务分解提示词内容（从文件加载）", default="")
    task_suggestion: str = desc_field(desc="任务建议提示词内容（从文件加载）", default="")


@dataclass(frozen=True)
class AppSettings:
    server: ServerSettings = desc_field(desc="服务运行配置", default_factory=ServerSettings)
    ssl: SSLSettings = desc_field(desc="HTTPS/证书配置", default_factory=SSLSettings)
    database: DatabaseSettings = desc_field(desc="数据库配置", default_factory=DatabaseSettings)
    redis: RedisSettings = desc_field(desc="Redis 配置", default_factory=RedisSettings)
    llm: LLMSettings = desc_field(desc="大模型调用配置", default_factory=LLMSettings)
    prompts: PromptsSettings = desc_field(desc="提示词配置", default_factory=PromptsSettings)


# ----------------------------
# Settings Builder (env override + prompt load)
# ----------------------------

def build_settings() -> AppSettings:
    """
    组装配置：
    - 默认值来自 dataclass 默认值
    - 允许用环境变量覆盖
    - 提示词从文件读取
    """
    # 提示词路径（可用 env 覆盖）
    task_decompose_path = _env("PROMPT_TASK_DECOMPOSE_PATH", "./llm_prompts/task_composer.txt")
    task_suggestion_path = _env("PROMPT_TASK_SUGGESTION_PATH", "./llm_prompts/task_suggestor.txt")

    return AppSettings(
        server=ServerSettings(
            host=_env("APP_HOST", "0.0.0.0"),
            port=_env_int("APP_PORT", 8000),
            reload=_env_bool("APP_RELOAD", True),
            workers=_env_int("APP_WORKERS", 10),
        ),
        ssl=SSLSettings(
            keyfile=os.getenv("SSL_KEYFILE", "certs/key.pem"),
            certfile=os.getenv("SSL_CERTFILE", "certs/cert.pem"),
        ),
        database=DatabaseSettings(
            db_url=_env("DB_URL", "127.0.0.1"),
            db_username=_env("DB_USERNAME", "luna"),
            db_password=_env("DB_PASSWORD", "lunamoon"),
            db_database_name=_env("DB_NAME", "luna"),
            db_port=_env_int("DB_PORT", 1980),
            minconn=_env_int("DB_MINCONN", 1),
            maxconn=_env_int("DB_MAXCONN", 20),
        ),
        redis=RedisSettings(
            host=_env("REDIS_HOST", "localhost"),
            port=_env_int("REDIS_PORT", 1981),
            db=_env_int("REDIS_DB", 0),
            password=os.getenv("REDIS_PASSWORD"),
        ),
        llm=LLMSettings(
            api_url=_env("LLM_API_URL", "https://api.deepseek.com"),
            api_key=_env("LLM_API_KEY", "sk-558d007981e0400b9a3db23a824e4eef"),  # 重要：别再硬编码
            model=_env("LLM_MODEL", "deepseek-reasoner"),
        ),
        prompts=PromptsSettings(
            task_decompose=_read_text(task_decompose_path),
            task_suggestion=_read_text(task_suggestion_path),
        ),
    )


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """获取全局配置实例（单例缓存）。"""
    return build_settings()


# ----------------------------
# Optional: Export docs from desc metadata
# ----------------------------

def iter_setting_docs(obj: Any, prefix: str = "") -> Iterable[Tuple[str, str, str, str]]:
    """
    递归遍历 dataclass 实例，导出 (path, type, default/value, desc)。
    """
    if not is_dataclass(obj):
        return

    for f in fields(obj):
        value = getattr(obj, f.name)
        desc = (f.metadata or {}).get("desc", "")
        type_name = getattr(f.type, "__name__", str(f.type))
        path = f"{prefix}{f.name}" if not prefix else f"{prefix}.{f.name}"

        if is_dataclass(value):
            yield (path, type_name, "", desc)
            yield from iter_setting_docs(value, path)
        else:
            yield (path, type_name, repr(value), desc)


def settings_docs_markdown(settings: Optional[AppSettings] = None) -> str:
    """
    生成 Markdown 表格，可直接贴到 docs/DEVELOPMENT.md 或 README。
    """
    s = settings or get_settings()
    rows = list(iter_setting_docs(s))
    lines = [
        "| Key | Type | Value(Default) | Desc |",
        "|---|---|---|---|",
    ]
    for key, t, v, d in rows:
        lines.append(f"| `{key}` | `{t}` | `{v}` | {d} |")
    return "\n".join(lines)

