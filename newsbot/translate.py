from __future__ import annotations

import logging
import re
from collections.abc import Iterable

import httpx

from newsbot.db import Store

log = logging.getLogger("newsbot.translate")

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")
SPACE_RE = re.compile(r"\s+")


def is_mostly_english(text: str) -> bool:
    text = SPACE_RE.sub(" ", (text or "").strip())
    if not text:
        return False
    if CJK_RE.search(text):
        return False
    latin = len(LATIN_RE.findall(text))
    return latin >= 3


async def _google_translate(client: httpx.AsyncClient, text: str) -> str:
    response = await client.get(
        "https://translate.googleapis.com/translate_a/single",
        params={"client": "gtx", "sl": "auto", "tl": "zh-CN", "dt": "t", "q": text},
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    parts = []
    for chunk in data[0] or []:
        if chunk and chunk[0]:
            parts.append(str(chunk[0]))
    return SPACE_RE.sub(" ", "".join(parts)).strip()


async def translate_texts(store: Store, texts: Iterable[str]) -> dict[str, str]:
    unique: list[str] = []
    seen: set[str] = set()
    for text in texts:
        text = SPACE_RE.sub(" ", (text or "").strip())
        if not text or text in seen or not is_mostly_english(text):
            continue
        seen.add(text)
        unique.append(text)

    result: dict[str, str] = {}
    pending: list[str] = []
    for text in unique:
        cached = store.get_kv(f"tr:{text}")
        if cached:
            result[text] = cached
        else:
            pending.append(text)

    if not pending:
        return result

    headers = {"User-Agent": "Mozilla/5.0"}
    async with httpx.AsyncClient(headers=headers, follow_redirects=True) as client:
        for text in pending:
            try:
                translated = await _google_translate(client, text)
                if translated and translated != text:
                    result[text] = translated
                    store.set_kv(f"tr:{text}", translated)
            except Exception as exc:
                log.warning("translate failed for %r: %s", text[:60], exc)
    return result


def bilingual(original: str, translations: dict[str, str]) -> str:
    original = SPACE_RE.sub(" ", (original or "").strip())
    if not original:
        return ""
    if not is_mostly_english(original):
        return original
    zh = translations.get(original)
    if not zh:
        return original
    return f"{original}（{zh}）"
