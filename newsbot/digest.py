from __future__ import annotations

import html
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from newsbot.config import Settings
from newsbot.db import Store
from newsbot.fetcher import Article, fetch_articles, format_age
from newsbot.summarize import clean_summary, llm_summaries

TELEGRAM_LIMIT = 3900
WEEKDAYS = "一二三四五六日"


@dataclass
class DigestResult:
    today: str
    today_label: str
    selected: list[Article]
    summaries: dict[str, str]
    skipped: list[str]
    messages: list[str] = field(default_factory=list)


def _pick(articles: list[Article], limit: int) -> list[Article]:
    """Prefer recency, but rotate sources so one site does not fill the section."""
    ordered = sorted(articles, key=lambda item: item.published_ts, reverse=True)
    buckets: dict[str, list[Article]] = defaultdict(list)
    for article in ordered:
        buckets[article.source].append(article)
    picked: list[Article] = []
    sources = list(buckets)
    while len(picked) < limit and any(buckets.values()):
        progressed = False
        for source in sources:
            if len(picked) >= limit:
                break
            if buckets[source]:
                picked.append(buckets[source].pop(0))
                progressed = True
        if not progressed:
            break
    return picked


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


def _today_label(now: datetime) -> str:
    weekday = WEEKDAYS[now.weekday()]
    return f"{now.year}年{now.month}月{now.day}日 星期{weekday}"


async def build_digest(
    settings: Settings,
    store: Store,
    mark_seen: bool = True,
    ignore_seen: bool = False,
) -> DigestResult:
    articles, skipped = await fetch_articles(settings)
    pool = articles if ignore_seen else [item for item in articles if not store.is_seen(item.url)]
    by_category: dict[str, list[Article]] = defaultdict(list)
    for article in pool:
        by_category[article.category_id].append(article)

    selected: list[Article] = []
    for category in settings.categories:
        selected.extend(_pick(by_category.get(category.id, []), category.max_items))

    summaries = {
        article.url: clean_summary(article.summary, article.title)
        for article in selected
    }
    llm = await llm_summaries(settings, selected)
    summaries.update(llm)

    tz = ZoneInfo(settings.timezone)
    now = datetime.now(tz)
    today = now.strftime("%Y-%m-%d")
    today_label = _today_label(now)
    header = f"<b>每日资讯 {today_label}</b>"
    if skipped:
        header += f"\n<i>未拉取到：{html.escape('、'.join(skipped))}</i>"

    if not selected:
        text = header + "\n\n今天没有新条目（或都已经推送过）。"
        last = store.get_kv("last_digest")
        last_date = store.get_kv("last_digest_date")
        if last and last_date == today and not ignore_seen:
            return DigestResult(
                today=today,
                today_label=today_label,
                selected=[],
                summaries={},
                skipped=skipped,
                messages=last.split("\n\n---SPLIT---\n\n"),
            )
        return DigestResult(today, today_label, [], {}, skipped, [text])

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
    return DigestResult(today, today_label, selected, summaries, skipped, messages)


def grouped_items(settings: Settings, result: DigestResult) -> list[tuple[str, list[Article]]]:
    groups: list[tuple[str, list[Article]]] = []
    for category in settings.categories:
        items = [article for article in result.selected if article.category_id == category.id]
        if items:
            groups.append((category.name, items))
    return groups


def render_email(settings: Settings, result: DigestResult) -> tuple[str, str, str]:
    subject = f"每日资讯 · {result.today_label}"
    total = len(result.selected)
    groups = grouped_items(settings, result)

    intro = f"共 {total} 条" if total else "今天没有新条目"
    if result.skipped:
        intro += f" · 未拉取到：{'、'.join(result.skipped)}"

    sections_html: list[str] = []
    plain_lines = [f"每日资讯", result.today_label, intro, ""]

    if not groups:
        sections_html.append(
            '<tr><td style="padding:16px 24px;color:#555;font-size:15px;">今天没有新条目（或都已经推送过）。</td></tr>'
        )
        plain_lines.append("今天没有新条目（或都已经推送过）。")
    else:
        for name, items in groups:
            rows = [
                f"""
                <tr>
                  <td style="padding:18px 24px 8px 24px;font-size:16px;font-weight:700;color:#111;border-top:1px solid #eee;">
                    {html.escape(name)}
                    <span style="font-weight:400;color:#888;font-size:13px;"> · {len(items)} 条</span>
                  </td>
                </tr>
                """
            ]
            plain_lines.append(f"【{name}】")
            for index, article in enumerate(items, start=1):
                summary = result.summaries.get(article.url, "")
                title = html.escape(article.title)
                href = html.escape(article.url, quote=True)
                meta = f"{html.escape(article.source)} · {format_age(article.published_ts)}"
                summary_html = (
                    f'<div style="margin:4px 0 0 0;color:#555;font-size:14px;line-height:1.55;">{html.escape(summary)}</div>'
                    if summary
                    else ""
                )
                rows.append(
                    f"""
                    <tr>
                      <td style="padding:10px 24px 14px 24px;">
                        <div style="font-size:15px;line-height:1.45;">
                          <span style="color:#999;">{index}.</span>
                          <a href="{href}" style="color:#0b57d0;text-decoration:none;font-weight:600;">{title}</a>
                        </div>
                        {summary_html}
                        <div style="margin-top:6px;color:#999;font-size:12px;">{meta}</div>
                      </td>
                    </tr>
                    """
                )
                plain_lines.append(f"{index}. {article.title}")
                if summary:
                    plain_lines.append(f"   {summary}")
                plain_lines.append(f"   {article.source} · {format_age(article.published_ts)}")
                plain_lines.append(f"   {article.url}")
                plain_lines.append("")
            sections_html.append("".join(rows))

    html_body = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(subject)}</title>
</head>
<body style="margin:0;padding:0;background:#f4f5f7;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background:#f4f5f7;padding:16px 0;">
    <tr>
      <td align="center">
        <table role="presentation" width="640" cellpadding="0" cellspacing="0" style="width:640px;max-width:96%;background:#ffffff;border-radius:8px;overflow:hidden;border:1px solid #e6e8eb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','PingFang SC','Hiragino Sans GB','Noto Sans SC',sans-serif;color:#222;">
          <tr>
            <td style="padding:22px 24px 10px 24px;background:#1f2937;color:#fff;">
              <div style="font-size:20px;font-weight:700;letter-spacing:0.02em;">每日资讯</div>
              <div style="margin-top:6px;font-size:13px;color:#d1d5db;">{html.escape(result.today_label)} · {html.escape(intro)}</div>
            </td>
          </tr>
          {''.join(sections_html)}
          <tr>
            <td style="padding:16px 24px 22px 24px;color:#9ca3af;font-size:12px;border-top:1px solid #eee;">
              由你的资讯机器人发送，仅供本人阅读。
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    return subject, html_body, "\n".join(plain_lines).strip() + "\n"
