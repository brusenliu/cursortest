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
    mail_to: str = ""
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_host: str = ""
    smtp_port: int = 0
    smtp_from: str = ""
    smtp_security: str = ""
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

    @property
    def mail_recipients(self) -> list[str]:
        return [part.strip() for part in self.mail_to.split(",") if part.strip()]

    @property
    def mail_enabled(self) -> bool:
        return bool(self.mail_recipients and self.smtp_password)


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
    mail_to = os.environ.get("MAIL_TO", "").strip()
    smtp_user = os.environ.get("SMTP_USER", "").strip()
    if not smtp_user and mail_to:
        smtp_user = mail_to.split(",")[0].strip()
    smtp_from = os.environ.get("SMTP_FROM", "").strip() or smtp_user
    return Settings(
        timezone=str(raw.get("timezone") or "Asia/Shanghai"),
        digest_hour=int(raw.get("digest_hour") or 8),
        digest_minute=int(raw.get("digest_minute") or 0),
        max_age_hours=int(raw.get("max_age_hours") or 36),
        request_timeout_seconds=int(raw.get("request_timeout_seconds") or 15),
        categories=categories,
        telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", "").strip(),
        telegram_chat_id=os.environ.get("TELEGRAM_CHAT_ID", "").strip(),
        mail_to=mail_to,
        smtp_user=smtp_user,
        smtp_password=os.environ.get("SMTP_PASSWORD", "").strip(),
        smtp_host=os.environ.get("SMTP_HOST", "").strip(),
        smtp_port=int(os.environ.get("SMTP_PORT", "0") or 0),
        smtp_from=smtp_from,
        smtp_security=os.environ.get("SMTP_SECURITY", "").strip().lower(),
        llm_api_key=os.environ.get("LLM_API_KEY", "").strip(),
        llm_base_url=os.environ.get("LLM_BASE_URL", "https://api.deepseek.com").rstrip("/"),
        llm_model=os.environ.get("LLM_MODEL", "deepseek-chat").strip() or "deepseek-chat",
        db_path=db_path,
        feeds_path=path,
    )
