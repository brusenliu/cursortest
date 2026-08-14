from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PACKAGE_DIR = Path(__file__).resolve().parent
DEFAULT_FEEDS_PATH = PACKAGE_DIR / "feeds.yaml"


@dataclass(frozen=True)
class Feed:
    name: str
    url: str


@dataclass(frozen=True)
class Category:
    id: str
    name: str
    max_items: int
    feeds: list[Feed]


@dataclass(frozen=True)
class Settings:
    timezone: str
    digest_hour: int
    digest_minute: int
    max_age_hours: int
    request_timeout_seconds: int
    categories: list[Category]
    telegram_bot_token: str = ""
    telegram_chat_id: str = ""
    llm_api_key: str = ""
    llm_base_url: str = "https://api.deepseek.com"
    llm_model: str = "deepseek-chat"
    db_path: Path = field(default_factory=lambda: Path("/var/lib/newsbot/seen.sqlite"))
    feeds_path: Path = DEFAULT_FEEDS_PATH

    @property
    def allowed_chat_ids(self) -> set[int]:
        raw = self.telegram_chat_id.strip()
        if not raw:
            return set()
        return {int(part.strip()) for part in raw.split(",") if part.strip()}


def _load_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    if not isinstance(data, dict):
        raise ValueError(f"feeds config must be a mapping: {path}")
    return data


def load_settings(feeds_path: Path | None = None) -> Settings:
    path = Path(os.environ.get("NEWSBOT_FEEDS", feeds_path or DEFAULT_FEEDS_PATH))
    raw = _load_yaml(path)
    categories: list[Category] = []
    for item in raw.get("categories") or []:
        feeds = [
            Feed(name=str(feed["name"]), url=str(feed["url"]))
            for feed in item.get("feeds") or []
        ]
        categories.append(
            Category(
                id=str(item["id"]),
                name=str(item["name"]),
                max_items=int(item.get("max_items") or 8),
                feeds=feeds,
            )
        )
    db_path = Path(os.environ.get("NEWSBOT_DB", "/var/lib/newsbot/seen.sqlite"))
    return Settings(
        timezone=str(raw.get("timezone") or "Asia/Shanghai"),
        digest_hour=int(raw.get("digest_hour") or 8),
        digest_minute=int(raw.get("digest_minute") or 0),
        max_age_hours=int(raw.get("max_age_hours") or 36),
        request_timeout_seconds=int(raw.get("request_timeout_seconds") or 15),
        categories=categories,
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", "").strip(),
        llm_api_key=os.environ.get("LLM_API_KEY", "").strip(),
        llm_base_url=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        llm_model=os.environ.get("LLM_MODEL", "deepseek-chat").strip() or "deepseek-chat",
        db_path=db_path,
        feeds_path=path,
    )
