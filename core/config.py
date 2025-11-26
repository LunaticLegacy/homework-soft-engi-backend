from dataclasses import asdict
from typing import Any, Dict

from settings import settings, AppSettings


def get_settings() -> AppSettings:
    """返回应用配置 dataclass。"""
    return settings


def load_config() -> Dict[str, Any]:
    """
    返回 dict 结构的配置（与旧 load_config 接口保持兼容）。
    """
    return asdict(settings)
