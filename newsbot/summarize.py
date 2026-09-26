from __future__ import annotations

import html
import json
import logging
import re

import httpx

from newsbot.config import Settings
from newsbot.fetcher import Article

log = logging.getLogger("newsbot.summarize")

TAG_RE = re.compile(r"<[^>]+>")
SPACE_RE = re.compile(r"\s+")
SENTENCE_RE = re.compile(r"(.+?[。！？.!?])", re.S)
URL_RE = re.compile(r"https?://\S+", re.I)
NOISE_RE = re.compile(
    r"(article url|comments url|comments|link)[:：]?",
    re.I,
)
STATS_RE = re.compile(
    r"points\s*:\s*\d+(?:\s*#\s*(?:comments\s*:)?\s*\d+)?(?:\s*#\s*comments\s*:\s*\d+)?",
    re.I,
)
LEAD_RE = re.compile(
    r"^(IT之家|36氪|新浪|澎湃|少数派|Solidot).{0,24}(?:消息|报道)[，,：:]\s*",
)


def strip_html(text: str) -> str:
    text = html.unescape(text or "")
    text = TAG_RE.sub(" ", text)
    return SPACE_RE.sub(" ", text).strip()


def clean_summary(text: str, title: str = "", max_len: int = 72) -> str:
    cleaned = strip_html(text)
    cleaned = URL_RE.sub(" ", cleaned)
    cleaned = NOISE_RE.sub(" ", cleaned)
    cleaned = STATS_RE.sub(" ", cleaned)
    cleaned = LEAD_RE.sub("", cleaned)
    cleaned = SPACE_RE.sub(" ", cleaned).strip(" -—|·,，:：")
    if not cleaned or cleaned.lower() in {"points", "comments"} or cleaned.lower().startswith("points"):
        return ""
    title_norm = SPACE_RE.sub(" ", title or "").strip()
    if title_norm and (cleaned == title_norm or cleaned.startswith(title_norm)):
        rest = cleaned[len(title_norm) :].lstrip(" ：:-—。.")
        cleaned = rest or ""
    if not cleaned:
        return ""
    match = SENTENCE_RE.search(cleaned)
    snippet = match.group(1).strip() if match else cleaned
    if len(snippet) > max_len:
        return snippet[: max_len - 1].rstrip() + "…"
    return snippet


def rule_summary(text: str, max_len: int = 80) -> str:
    return clean_summary(text, max_len=max_len)


async def llm_summaries(settings: Settings, articles: list[Article]) -> dict[str, str]:
    if not settings.llm_api_key or not articles:
        return {}
    payload_items = [
        {
            "id": index,
            "title": article.title,
            "source": article.source,
            "snippet": clean_summary(article.summary, article.title, 180) or article.title,
        }
        for index, article in enumerate(articles)
    ]
    prompt = (
        "请把下列新闻整理成一句中文摘要，客观、短、不夸张。"
        "只返回 JSON 数组，每项格式 {\"id\": 数字, \"summary\": \"不超过40字\"}。\n\n"
        + json.dumps(payload_items, ensure_ascii=False)
    )
    url = f"{settings.llm_base_url}/v1/chat/completions"
    body = {
        "model": settings.llm_model,
        "temperature": 0.2,
        "messages": [
            {"role": "system", "content": "你是新闻编辑，只输出 JSON。"},
            {"role": "user", "content": prompt},
        ],
    }
    headers = {
        "Authorization": f"Bearer {settings.llm_api_key}",
        "Content-Type": "application/json",
    }
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*|\s*```$", "", content)
        parsed = json.loads(content)
        result: dict[str, str] = {}
        for item in parsed:
            index = int(item["id"])
            summary = str(item.get("summary") or "").strip()
            if 0 <= index < len(articles) and summary:
                result[articles[index].url] = clean_summary(summary, max_len=40)
        return result
    except Exception as exc:
        log.warning("LLM summarize failed, falling back to RSS snippets: %s", exc)
        return {}
