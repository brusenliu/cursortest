from __future__ import annotations

import html
from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from newsbot.config import Settings
from newsbot.db import Store
from newsbot.fetcher import Article, fetch_articles, format_age
from newsbot.summarize import llm_summaries, rule_summary

TELEGRAM_LIMIT = 3900


def _pick(articles: list[Article], limit: int) -> list[Article]:
    return sorted(articles, key=lambda item: item.published_ts, reverse=True)[:limit]


def _format_item(article: Article, summary: str) -> str:
    title = html.escape(article.title)
    source = html.escape(article.source)
    link = html.escape(article.url, quote=True)
    line = f'• <a href="{link}">{title}</a> <i>{source}</i>'
    if summary:
        line += f"\n  {html.escape(summary)}"
    line += f"\n  <i>{format_age(article.published_ts)}</i>"
    return line


def split_messages(chunks: list[str], header: str) -> list[str]:
    messages: list[str] = []
    current = header
    for chunk in chunks:
        candidate = f"{current}\n\n{chunk}" if current else chunk
        if len(candidate) <= TELEGRAM_LIMIT:
            current = candidate
            continue
        if current:
            messages.append(current)
        if len(chunk) <= TELEGRAM_LIMIT:
            current = chunk
            continue
        # Extremely long single category: split by item blocks.
        parts = chunk.split("\n\n")
        buf = parts[0]
        for part in parts[1:]:
            trial = f"{buf}\n\n{part}"
            if len(trial) <= TELEGRAM_LIMIT:
                buf = trial
            else:
                messages.append(buf)
                buf = part
        current = buf
    if current:
        messages.append(current)
    return messages


async def build_digest(settings: Settings, store: Store, mark_seen: bool = True) -> tuple[list[str], list[Article], list[str]]:
    articles, skipped = await fetch_articles(settings)
    fresh = [item for item in articles if not store.is_seen(item.url)]
    by_category: dict[str, list[Article]] = defaultdict(list)
    for article in fresh:
        by_category[article.category_id].append(article)

    selected: list[Article] = []
    for category in settings.categories:
        selected.extend(_pick(by_category.get(category.id, []), category.max_items))

    summaries = {article.url: rule_summary(article.summary) for article in selected}
    llm = await llm_summaries(settings, selected)
    summaries.update(llm)

    tz = ZoneInfo(settings.timezone)
    today = datetime.now(tz).strftime("%Y-%m-%d")
    header = f"<b>每日资讯 {today}</b>"
    if skipped:
        header += f"\n<i>未拉取到：{html.escape('、'.join(skipped))}</i>"

    if not selected:
        text = header + "\n\n今天没有新条目（或都已经推送过）。"
        last = store.get_kv("last_digest")
        last_date = store.get_kv("last_digest_date")
        if last and last_date == today:
            return last.split("\n\n---SPLIT---\n\n"), [], skipped
        return [text], [], skipped

    sections: list[str] = []
    for category in settings.categories:
        items = [article for article in selected if article.category_id == category.id]
        if not items:
            continue
        body = "\n\n".join(_format_item(article, summaries.get(article.url, "")) for article in items)
        sections.append(f"<b>{html.escape(category.name)}</b>\n{body}")

    messages = split_messages(sections, header)
    if mark_seen:
        store.mark_many([(item.url, item.title, item.category_id) for item in selected])
        store.set_kv("last_digest", "\n\n---SPLIT---\n\n".join(messages))
        store.set_kv("last_digest_date", today)
    return messages, selected, skipped
