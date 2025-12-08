from dataclasses import dataclass
from typing import Optional

import io

@dataclass(frozen=True)
class ServerSettings:
    host: str
    port: int
    reload: bool
    workers: int


@dataclass(frozen=True)
class SSLSettings:
    keyfile: Optional[str]
    certfile: Optional[str]


@dataclass(frozen=True)
class DatabaseSettings:
    db_url: str
    db_username: str
    db_password: str
    db_database_name: str
    db_port: int
    minconn: int
    maxconn: int


@dataclass(frozen=True)
class RedisSettings:
    host: str
    port: int
    db: int
    password: Optional[str]


@dataclass(frozen=True)
class LLMSettings:
    api_url: str
    api_key: str
    model: str


@dataclass(frozen=True)
class PromptsSettings:
    task_decompose: str
    task_suggestion: str


@dataclass(frozen=True)
class AppSettings:
    server: ServerSettings
    ssl: SSLSettings
    database: DatabaseSettings
    redis: RedisSettings
    llm: LLMSettings
    prompts: PromptsSettings


# 以文件形式载入提示词内容。
task_sug_msg: str
task_comp_ms: str

with open("./llm_prompts/task_composer.txt", 'r', encoding="utf-8") as composer:
    task_comp_msg = composer.read()

with open("./llm_prompts/task_suggestor.txt", 'r', encoding="utf-8") as sug:
    task_sug_msg = sug.read()


# 直接使用 Python 字面量承载配置内容（与 config.json 对应）
settings = AppSettings(
    server=ServerSettings(
        host="0.0.0.0",
        port=8000,
        reload=True,
        workers=10,
    ),
    ssl=SSLSettings(
        keyfile="certs/key.pem",
        certfile="certs/cert.pem",
    ),
    database=DatabaseSettings(
        db_url="127.0.0.1",
        db_username="luna",
        db_password="lunamoon",
        db_database_name="luna",
        db_port=1980,
        minconn=1,
        maxconn=20,
    ),
    redis=RedisSettings(
        host="localhost",
        port=1981,
        db=0,
        password=None,
    ),
    llm=LLMSettings(
        api_url="https://api.deepseek.com",
        api_key="sk-e8b4315f80e24843825ca39cd880e214",
        model="deepseek-reasoner",
    ),
    prompts=PromptsSettings(
        # 提示词
        task_decompose=task_sug_msg,
        task_suggestion=task_comp_msg
    ),
)


def get_settings() -> AppSettings:
    """获取全局配置实例。"""
    return settings
