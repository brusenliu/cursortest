from __future__ import annotations

import argparse
import asyncio
import logging
import os
from dataclasses import replace
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

from newsbot.config import load_settings
from newsbot.db import Store
from newsbot.deliver import deliver_digest
from newsbot.digest import build_digest, render_email


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _load_env() -> None:
    for candidate in (Path("/etc/newsbot.env"), Path(".env")):
        if candidate.exists():
            try:
                load_dotenv(candidate, override=False)
            except OSError as exc:
                logging.getLogger("newsbot").warning("skip env file %s: %s", candidate, exc)


def _writable_settings():
    settings = load_settings()
    parent = settings.db_path.parent
    if not parent.exists() or not os.access(parent, os.W_OK):
        settings = replace(settings, db_path=Path("./seen.sqlite"))
    return settings


async def print_digest() -> None:
    settings = _writable_settings()
    store = Store(settings.db_path)
    try:
        result = await build_digest(settings, store, mark_seen=False, ignore_seen=True)
        print(f"# items={len(result.selected)} skipped={result.skipped}\n")
        _, html, plain = render_email(settings, result)
        print(plain)
        print("\n---- html bytes", len(html), "----\n")
    finally:
        store.close()


async def send_now() -> None:
    settings = _writable_settings()
    if not settings.mail_enabled and not settings.telegram_bot_token:
        raise SystemExit("未配置邮件或 Telegram：请设置 MAIL_TO 与 SMTP_PASSWORD")
    store = Store(settings.db_path)
    try:
        result = await deliver_digest(settings, store, force_mail=True, ignore_seen=True)
        print(f"sent items={len(result.selected)} skipped={result.skipped} parts={len(result.messages)}")
    finally:
        store.close()


def run_telegram(settings, store) -> None:
    from newsbot.bot import build_application

    application = build_application(settings, store)
    logging.getLogger("newsbot").info(
        "starting telegram+scheduler tz=%s daily=%02d:%02d mail=%s",
        settings.timezone,
        settings.digest_hour,
        settings.digest_minute,
        settings.mail_enabled,
    )
    application.run_polling(drop_pending_updates=True)


def run_mail_scheduler(settings, store) -> None:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    log = logging.getLogger("newsbot")

    async def job() -> None:
        try:
            await deliver_digest(settings, store, force_mail=False)
        except Exception:
            log.exception("scheduled mail digest failed")

    async def main() -> None:
        scheduler = AsyncIOScheduler(timezone=ZoneInfo(settings.timezone))
        scheduler.add_job(
            job,
            "cron",
            hour=settings.digest_hour,
            minute=settings.digest_minute,
            id="daily-digest",
            replace_existing=True,
        )
        scheduler.start()
        log.info(
            "email scheduler started tz=%s daily=%02d:%02d to=%s",
            settings.timezone,
            settings.digest_hour,
            settings.digest_minute,
            settings.mail_recipients,
        )
        await asyncio.Event().wait()

    asyncio.run(main())


def run_service() -> None:
    settings = load_settings()
    store = Store(settings.db_path)
    if settings.telegram_bot_token:
        run_telegram(settings, store)
        return
    if settings.mail_enabled:
        run_mail_scheduler(settings, store)
        return
    raise SystemExit(
        "未配置推送渠道。请在 /etc/newsbot.env 填写 MAIL_TO 与 SMTP_PASSWORD，"
        "或填写 TELEGRAM_BOT_TOKEN。"
    )


def main() -> None:
    _configure_logging()
    _load_env()
    parser = argparse.ArgumentParser(description="Daily news digest bot")
    parser.add_argument("--print", action="store_true", help="Fetch and print a digest")
    parser.add_argument("--send", action="store_true", help="Fetch and send today's digest now")
    args = parser.parse_args()
    if args.print:
        asyncio.run(print_digest())
        return
    if args.send:
        asyncio.run(send_now())
        return
    run_service()


if __name__ == "__main__":
    main()
