from __future__ import annotations

import html
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from zoneinfo import ZoneInfo

from newsbot.config import Settings
from newsbot.db import Store
from newsbot.fetcher import Article, fetch_articles, format_age
from newsbot.markets import MarketSnapshot, change_color, fetch_markets, format_change
from newsbot.summarize import clean_summary, llm_summaries
from newsbot.translate import bilingual, translate_texts

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
    markets: MarketSnapshot | None = None
    translations: dict[str, str] = field(default_factory=dict)


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


def _format_item(article: Article, summary: str, translations: dict[str, str]) -> str:
    title = html.escape(bilingual(article.title, translations))
    source = html.escape(article.source)
    link = html.escape(article.url, quote=True)
    line = f'• <a href="{link}">{title}</a> <i>{source}</i>'
    if summary:
        line += f"\n  {html.escape(bilingual(summary, translations))}"
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
    markets = await fetch_markets()
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

    to_translate = [article.title for article in selected]
    to_translate.extend(summary for summary in summaries.values() if summary)
    translations = await translate_texts(store, to_translate)

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
                markets=markets,
            )
        return DigestResult(today, today_label, [], {}, skipped, [text], markets, translations)

    sections: list[str] = []
    for category in settings.categories:
        items = [article for article in selected if article.category_id == category.id]
        if not items:
            continue
        body = "\n\n".join(
            _format_item(article, summaries.get(article.url, ""), translations) for article in items
        )
        sections.append(f"<b>{html.escape(category.name)}</b>\n{body}")

    messages = split_messages(sections, header)
    if mark_seen:
        store.mark_many([(item.url, item.title, item.category_id) for item in selected])
        store.set_kv("last_digest", "\n\n---SPLIT---\n\n".join(messages))
        store.set_kv("last_digest_date", today)
    return DigestResult(today, today_label, selected, summaries, skipped, messages, markets, translations)


def grouped_items(settings: Settings, result: DigestResult) -> list[tuple[str, list[Article]]]:
    groups: list[tuple[str, list[Article]]] = []
    for category in settings.categories:
        items = [article for article in result.selected if article.category_id == category.id]
        if items:
            groups.append((category.name, items))
    return groups


def _market_table_html(title: str, quotes) -> str:
    if not quotes:
        return f"""
        <tr>
          <td style="padding:16px 24px;color:#6b7280;font-size:14px;border-top:1px solid #eee;">
            <b>{html.escape(title)}</b><br>暂无数据
          </td>
        </tr>
        """
    body = []
    for quote in quotes:
        price = f"{quote.price:.2f}" if quote.price is not None else "—"
        change = format_change(quote.change_pct)
        color = change_color(quote.change_pct)
        body.append(
            f"""
            <tr>
              <td style="padding:6px 8px 6px 24px;font-size:13px;">{html.escape(quote.name)}</td>
              <td style="padding:6px 8px;font-size:12px;color:#9ca3af;">{html.escape(quote.code)}</td>
              <td style="padding:6px 8px;font-size:13px;text-align:right;">{html.escape(price)}</td>
              <td style="padding:6px 24px 6px 8px;font-size:13px;text-align:right;font-weight:700;color:{color};">{html.escape(change)}</td>
            </tr>
            """
        )
    return f"""
    <tr>
      <td style="padding:18px 24px 4px 24px;font-size:16px;font-weight:700;color:#111;border-top:1px solid #eee;">
        {html.escape(title)}
      </td>
    </tr>
    <tr>
      <td style="padding:0 0 8px 0;">
        <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
          <tr>
            <td style="padding:4px 8px 4px 24px;font-size:12px;color:#9ca3af;">名称</td>
            <td style="padding:4px 8px;font-size:12px;color:#9ca3af;">代码</td>
            <td style="padding:4px 8px;font-size:12px;color:#9ca3af;text-align:right;">现价</td>
            <td style="padding:4px 24px 4px 8px;font-size:12px;color:#9ca3af;text-align:right;">涨跌幅</td>
          </tr>
          {''.join(body)}
        </table>
      </td>
    </tr>
    """


def render_email(settings: Settings, result: DigestResult) -> tuple[str, str, str]:
    subject = f"每日资讯 · {result.today_label}"
    total = len(result.selected)
    groups = grouped_items(settings, result)
    translations = result.translations

    intro = f"共 {total} 条资讯"
    if result.markets and (result.markets.us or result.markets.china):
        intro += " · 含行情"
    if result.skipped:
        intro += f" · 未拉取到：{'、'.join(result.skipped)}"

    sections_html: list[str] = []
    plain_lines = ["每日资讯", result.today_label, intro, ""]

    markets = result.markets
    if markets:
        if markets.note:
            plain_lines.append(markets.note)
        if markets.us:
            sections_html.append(_market_table_html("美股前十", markets.us))
            plain_lines.append("【美股前十】")
            for quote in markets.us:
                price = f"{quote.price:.2f}" if quote.price is not None else "—"
                plain_lines.append(f"{quote.name}({quote.code})  {price}  {format_change(quote.change_pct)}")
            plain_lines.append("")
        if markets.china:
            sections_html.append(_market_table_html("国内主要板块", markets.china))
            plain_lines.append("【国内主要板块】")
            for quote in markets.china:
                plain_lines.append(f"{quote.name}  {format_change(quote.change_pct)}")
            plain_lines.append("")

    if not groups:
        sections_html.append(
            '<tr><td style="padding:16px 24px;color:#555;font-size:15px;border-top:1px solid #eee;">今天没有新条目（或都已经推送过）。</td></tr>'
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
                title_show = bilingual(article.title, translations)
                summary_show = bilingual(summary, translations) if summary else ""
                href = html.escape(article.url, quote=True)
                meta = f"{html.escape(article.source)} · {format_age(article.published_ts)}"
                summary_html = (
                    f'<div style="margin:4px 0 0 0;color:#555;font-size:14px;line-height:1.55;">{html.escape(summary_show)}</div>'
                    if summary_show
                    else ""
                )
                rows.append(
                    f"""
                    <tr>
                      <td style="padding:10px 24px 14px 24px;">
                        <div style="font-size:15px;line-height:1.45;">
                          <span style="color:#999;">{index}.</span>
                          <a href="{href}" style="color:#0b57d0;text-decoration:none;font-weight:600;">{html.escape(title_show)}</a>
                        </div>
                        {summary_html}
                        <div style="margin-top:6px;color:#999;font-size:12px;">{meta}</div>
                      </td>
                    </tr>
                    """
                )
                plain_lines.append(f"{index}. {title_show}")
                if summary_show:
                    plain_lines.append(f"   {summary_show}")
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
              行情来自公开行情接口，仅供参考；资讯由你的机器人整理，仅供本人阅读。
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
