"""应用设置持久化存储（用户目录下 JSON 文件）。"""

import json
from pathlib import Path
from typing import Any, Dict


CONFIG_PATH = Path.home() / ".fluentcrypto" / "settings.json"


def load_settings() -> Dict[str, Any]:
    """读取持久化设置；文件不存在或损坏时返回空字典。"""
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def save_settings(values: Dict[str, Any]) -> None:
    """把设置写入 JSON 配置文件。"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(
        json.dumps(values, ensure_ascii=False, indent=2), encoding="utf-8"
    )
