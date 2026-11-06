from __future__ import annotations

import asyncio
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


async def _request_json(client: httpx.AsyncClient, url: str, params: dict, tries: int = 3):
    delay = 1.0
    last_error: Exception | None = None
    for _ in range(tries):
        try:
            response = await client.get(url, params=params, timeout=20)
            if response.status_code == 429:
                last_error = httpx.HTTPStatusError(
                    "429 Too Many Requests",
                    request=response.request,
                    response=response,
                )
                await asyncio.sleep(delay)
                delay *= 2
                continue
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            last_error = exc
            if exc.response.status_code not in {429, 500, 502, 503, 504}:
                raise
            await asyncio.sleep(delay)
            delay *= 2
        except httpx.HTTPError as exc:
            last_error = exc
            await asyncio.sleep(delay)
            delay *= 2
    assert last_error is not None
    raise last_error


def _text_from_gtx(data) -> str:
    parts = []
    chunks = data[0] if isinstance(data, list) and data else []
    for chunk in chunks or []:
        if chunk and chunk[0]:
            parts.append(str(chunk[0]))
    return SPACE_RE.sub(" ", "".join(parts)).strip()


def _text_from_chrome(data) -> str:
    if isinstance(data, list) and data:
        first = data[0]
        if isinstance(first, str):
            return SPACE_RE.sub(" ", first).strip()
        if isinstance(first, list) and first and first[0]:
            return SPACE_RE.sub(" ", str(first[0])).strip()
    return ""


async def _google_translate(client: httpx.AsyncClient, text: str) -> str:
    data = await _request_json(
        client,
        "https://translate.googleapis.com/translate_a/single",
        {"client": "gtx", "sl": "auto", "tl": "zh-CN", "dt": "t", "q": text},
    )
    translated = _text_from_gtx(data)
    if not translated:
        raise RuntimeError("empty gtx translation")
    return translated


async def _chrome_translate(client: httpx.AsyncClient, text: str) -> str:
    data = await _request_json(
        client,
        "https://clients5.google.com/translate_a/t",
        {"client": "dict-chrome-ex", "sl": "en", "tl": "zh-CN", "q": text},
        tries=2,
    )
    translated = _text_from_chrome(data)
    if not translated:
        raise RuntimeError("empty chrome translation")
    return translated


async def _mymemory_translate(client: httpx.AsyncClient, text: str) -> str:
    data = await _request_json(
        client,
        "https://api.mymemory.translated.net/get",
        {"q": text[:450], "langpair": "en|zh-CN"},
        tries=2,
    )
    translated = str(((data.get("responseData") or {}).get("translatedText")) or "")
    translated = SPACE_RE.sub(" ", translated).strip()
    if not translated or "MYMEMORY WARNING" in translated.upper():
        raise RuntimeError("mymemory unavailable")
    return translated


async def _translate_one(client: httpx.AsyncClient, text: str) -> str:
    last_error: Exception | None = None
    for translate in (_chrome_translate, _google_translate, _mymemory_translate):
        try:
            return await translate(client, text)
        except Exception as exc:
            last_error = exc
            await asyncio.sleep(0.6)
    assert last_error is not None
    raise last_error


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
                translated = await _translate_one(client, text)
                if translated and translated != text:
                    result[text] = translated
                    store.set_kv(f"tr:{text}", translated)
            except Exception as exc:
                log.warning("translate failed for %r: %s", text[:60], exc)
            await asyncio.sleep(0.5)
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
