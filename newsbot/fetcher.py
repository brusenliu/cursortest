from __future__ import annotations

import asyncio
import html
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from time import mktime

import feedparser
import httpx

from newsbot.config import Category, Feed, Settings

log = logging.getLogger("newsbot.fetcher")

USER_AGENT = "newsbot/1.0 (+https://github.com/brusenliu/cursortest)"


@dataclass
class Article:
    title: str
    url: str
    summary: str
    published_ts: float
    source: str
    category_id: str
    category_name: str


def _entry_time(entry: object) -> float:
    parsed = getattr(entry, "published_parsed", None) or getattr(entry, "updated_parsed", None)
    if parsed:
        try:
            return mktime(parsed)
        except (OverflowError, ValueError, TypeError):
            pass
    raw = getattr(entry, "published", None) or getattr(entry, "updated", None)
    if raw:
        try:
            dt = parsedate_to_datetime(str(raw))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            return dt.timestamp()
        except (TypeError, ValueError, OverflowError):
            pass
    return time.time()


def _entry_link(entry: object) -> str:
    link = str(getattr(entry, "link", "") or "").strip()
    if link:
        return link
    for item in getattr(entry, "links", []) or []:
        href = str(item.get("href") or "").strip()
        if href:
            return href
    return ""


async def _download(client: httpx.AsyncClient, feed: Feed, timeout: float) -> bytes | None:
    try:
        response = await client.get(feed.url, timeout=timeout)
        response.raise_for_status()
        return response.content
    except Exception as exc:
        log.warning("skip feed %s (%s): %s: %s", feed.name, feed.url, type(exc).__name__, exc)
        return None


def _parse_feed(payload: bytes, feed: Feed, category: Category, cutoff: float) -> list[Article]:
    parsed = feedparser.parse(payload)
    articles: list[Article] = []
    for entry in parsed.entries:
        url = _entry_link(entry)
        title = html.unescape(str(getattr(entry, "title", "") or "")).strip()
        title = " ".join(title.split())
        if not url or not title:
            continue
        published_ts = _entry_time(entry)
        if published_ts < cutoff:
            continue
        summary = str(getattr(entry, "summary", "") or getattr(entry, "description", "") or "")
        articles.append(
            Article(
                title=title,
                url=url,
                summary=summary,
                published_ts=published_ts,
                source=feed.name,
                category_id=category.id,
                category_name=category.name,
            )
        )
    return articles


async def fetch_articles(settings: Settings) -> tuple[list[Article], list[str]]:
    cutoff = time.time() - settings.max_age_hours * 3600
    timeout = float(settings.request_timeout_seconds)
    skipped: list[str] = []
    articles: list[Article] = []
    headers = {"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/xml, text/xml, */*"}

    async with httpx.AsyncClient(follow_redirects=True, headers=headers) as client:
        tasks: list[tuple[Category, Feed, asyncio.Task[bytes | None]]] = []
        for category in settings.categories:
            for feed in category.feeds:
                task = asyncio.create_task(_download(client, feed, timeout))
                tasks.append((category, feed, task))
        for category, feed, task in tasks:
            payload = await task
            if payload is None:
                skipped.append(feed.name)
                continue
            articles.extend(_parse_feed(payload, feed, category, cutoff))

    unique: dict[str, Article] = {}
    for article in sorted(articles, key=lambda item: item.published_ts, reverse=True):
        unique.setdefault(article.url, article)
    return list(unique.values()), skipped


def format_age(ts: float) -> str:
    dt = datetime.fromtimestamp(ts)
    return dt.strftime("%m-%d %H:%M")
