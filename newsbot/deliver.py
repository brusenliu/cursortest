from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from newsbot.config import Settings
from newsbot.db import Store
from newsbot.digest import DigestResult, build_digest, render_email
from newsbot.mailer import send_email

log = logging.getLogger("newsbot.deliver")


async def deliver_digest(
    settings: Settings,
    store: Store,
    *,
    mark_seen: bool = True,
    force_mail: bool = False,
    ignore_seen: bool = False,
    telegram_bot=None,
) -> DigestResult:
    result = await build_digest(
        settings,
        store,
        mark_seen=False,
        ignore_seen=ignore_seen,
    )
    today = datetime.now(ZoneInfo(settings.timezone)).strftime("%Y-%m-%d")
    subject, html, plain = render_email(settings, result)

    mailed = False
    if settings.mail_enabled and (force_mail or result.selected):
        already = store.get_kv("last_mail_date")
        if force_mail or already != today:
            await asyncio.to_thread(send_email, settings, subject, html, plain)
            store.set_kv("last_mail_date", today)
            mailed = True
        else:
            log.info("skip mail: already sent today")

    telegram_sent = False
    if telegram_bot is not None:
        chat_ids = settings.allowed_chat_ids
        if not chat_ids:
            log.warning("telegram configured but TELEGRAM_CHAT_ID is empty")
        else:
            from telegram.constants import ParseMode

            for chat_id in chat_ids:
                for message in result.messages:
                    await telegram_bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode=ParseMode.HTML,
                        disable_web_page_preview=True,
                    )
            telegram_sent = True

    if mark_seen and result.selected and (mailed or telegram_sent or not settings.mail_enabled):
        store.mark_many([(item.url, item.title, item.category_id) for item in result.selected])
        store.set_kv("last_digest", "\n\n---SPLIT---\n\n".join(result.messages))
        store.set_kv("last_digest_date", today)

    log.info(
        "delivered items=%s skipped=%s mailed=%s telegram=%s",
        len(result.selected),
        result.skipped,
        mailed,
        telegram_sent,
    )
    return result
