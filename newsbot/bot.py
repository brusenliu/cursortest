from __future__ import annotations

import logging
from datetime import time
from zoneinfo import ZoneInfo

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from newsbot.config import Settings
from newsbot.db import Store
from newsbot.deliver import deliver_digest

log = logging.getLogger("newsbot.bot")


class NewsBot:
    def __init__(self, settings: Settings, store: Store) -> None:
        self.settings = settings
        self.store = store

    def allowed(self, chat_id: int) -> bool:
        allowed = self.settings.allowed_chat_ids
        if not allowed:
            return False
        return chat_id in allowed

    async def send_chunks(self, bot, chat_id: int, messages: list[str]) -> None:
        for message in messages:
            await bot.send_message(
                chat_id=chat_id,
                text=message,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True,
            )

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None:
            return
        chat_id = chat.id
        if not self.settings.allowed_chat_ids:
            await update.message.reply_text(
                "还没有配置 TELEGRAM_CHAT_ID。\n"
                f"你的 chat id 是：`{chat_id}`\n"
                "把它写进服务器 /etc/newsbot.env 后重启服务。",
                parse_mode=ParseMode.MARKDOWN,
            )
            return
        if not self.allowed(chat_id):
            await update.message.reply_text("未授权的聊天。")
            return
        await update.message.reply_text(
            "已绑定。我会在每天 08:00（上海时间）推送资讯摘要。\n"
            "命令：/today 立刻出一份，/sources 查看源，/ping 探活。"
        )

    async def ping(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or not self.allowed(update.effective_chat.id):
            return
        await update.message.reply_text("pong")

    async def sources(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if update.effective_chat is None or not self.allowed(update.effective_chat.id):
            return
        lines = ["当前资讯源："]
        for category in self.settings.categories:
            names = "、".join(feed.name for feed in category.feeds)
            lines.append(f"• {category.name}：{names}")
        await update.message.reply_text("\n".join(lines))

    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        chat = update.effective_chat
        if chat is None or not self.allowed(chat.id):
            return
        await update.message.reply_text("正在整理今日资讯…")
        try:
            messages, selected, skipped = await build_digest(self.settings, self.store)
            await self.send_chunks(context.bot, chat.id, messages)
            log.info("sent /today items=%s skipped=%s", len(selected), skipped)
        except Exception:
            log.exception("failed to build /today digest")
            await update.message.reply_text("整理失败，请查看服务器日志。")

    async def daily_job(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        try:
            await deliver_digest(self.settings, self.store, telegram_bot=context.bot)
        except Exception:
            log.exception("daily digest failed")


def build_application(settings: Settings, store: Store) -> Application:
    newsbot = NewsBot(settings, store)
    application = Application.builder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler("start", newsbot.start))
    application.add_handler(CommandHandler("ping", newsbot.ping))
    application.add_handler(CommandHandler("sources", newsbot.sources))
    application.add_handler(CommandHandler("today", newsbot.today))

    tz = ZoneInfo(settings.timezone)
    when = time(hour=settings.digest_hour, minute=settings.digest_minute, tzinfo=tz)
    if application.job_queue is None:
        raise SystemExit("JobQueue extra is missing; install python-telegram-bot[job-queue]")
    application.job_queue.run_daily(newsbot.daily_job, time=when, name="daily-digest")
    return application
