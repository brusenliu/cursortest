from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

import httpx

log = logging.getLogger("newsbot.markets")

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Referer": "https://quote.eastmoney.com/",
    "Accept": "application/json, text/plain, */*",
}

# Rough market-cap leaders. 105 = NASDAQ, 106 = NYSE on East Money.
US_TOP10 = [
    ("105.NVDA", "英伟达"),
    ("105.MSFT", "微软"),
    ("105.AAPL", "苹果"),
    ("105.GOOGL", "谷歌"),
    ("105.AMZN", "亚马逊"),
    ("105.META", "Meta"),
    ("105.AVGO", "博通"),
    ("105.TSLA", "特斯拉"),
    ("106.BRK_B", "伯克希尔B"),
    ("106.JPM", "摩根大通"),
]

# Major A-share industry / theme boards.
CN_BOARDS = [
    ("90.BK0896", "白酒"),
    ("90.BK0917", "半导体"),
    ("90.BK1031", "人工智能"),
    ("90.BK0493", "新能源车"),
    ("90.BK0727", "光伏设备"),
    ("90.BK0475", "银行"),
    ("90.BK0473", "证券"),
    ("90.BK0474", "保险"),
    ("90.BK0451", "房地产"),
    ("90.BK0465", "医药"),
    ("90.BK0447", "煤炭"),
    ("90.BK0478", "有色金属"),
]

# Spot / domestic gold references on East Money.
GOLD_QUOTES = [
    ("122.XAU", "伦敦金", "XAU"),
    ("118.AU9999", "黄金9999", "AU9999"),
    ("90.BK1617", "黄金板块", "BK1617"),
]


@dataclass
class Quote:
    code: str
    name: str
    price: float | None
    change_pct: float | None
    unit: str = ""


@dataclass
class MarketSnapshot:
    us: list[Quote]
    china: list[Quote]
    gold: list[Quote]
    note: str = ""


def _num(value) -> float | None:
    if value is None or value == "-" or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


async def _fetch_ulist(client: httpx.AsyncClient, secids: str) -> dict[str, dict]:
    params = {"fltt": 2, "fields": "f12,f14,f2,f3,f4", "secids": secids}
    hosts = (
        "https://push2.eastmoney.com/api/qt/ulist.np/get",
        "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
    )
    last_error: Exception | None = None
    for host in hosts:
        for attempt in range(2):
            try:
                response = await client.get(host, params=params, timeout=20)
                response.raise_for_status()
                payload = response.json()
                rows = ((payload.get("data") or {}).get("diff")) or []
                return {str(row.get("f12")): row for row in rows}
            except Exception as exc:
                last_error = exc
                await asyncio.sleep(0.4 * (attempt + 1))
    assert last_error is not None
    raise last_error


async def fetch_markets() -> MarketSnapshot:
    us_map = {code.split(".", 1)[1]: zh for code, zh in US_TOP10}
    cn_map = {code.split(".", 1)[1]: zh for code, zh in CN_BOARDS}
    notes: list[str] = []
    us: list[Quote] = []
    china: list[Quote] = []
    gold: list[Quote] = []

    async with httpx.AsyncClient(headers=UA, follow_redirects=True) as client:
        try:
            data = await _fetch_ulist(client, ",".join(code for code, _ in US_TOP10))
            for code, fallback in US_TOP10:
                symbol = code.split(".", 1)[1]
                row = data.get(symbol) or data.get(symbol.replace("_", "."))
                if not row:
                    continue
                name = us_map.get(symbol) or str(row.get("f14") or symbol)
                us.append(
                    Quote(
                        code=symbol.replace("_", "."),
                        name=name,
                        price=_num(row.get("f2")),
                        change_pct=_num(row.get("f3")),
                        unit="USD",
                    )
                )
        except Exception as exc:
            log.warning("US quotes failed: %s", exc)
            notes.append("美股行情暂时无法获取")

        try:
            data = await _fetch_ulist(client, ",".join(code for code, _ in CN_BOARDS))
            for code, fallback in CN_BOARDS:
                symbol = code.split(".", 1)[1]
                row = data.get(symbol)
                if not row:
                    continue
                name = cn_map.get(symbol) or str(row.get("f14") or symbol)
                # Strip East Money suffixes like Ⅱ / 概念
                name = name.replace("Ⅱ", "").replace("概念", "").strip()
                china.append(
                    Quote(
                        code=symbol,
                        name=name or fallback,
                        price=_num(row.get("f2")),
                        change_pct=_num(row.get("f3")),
                    )
                )
            china.sort(key=lambda item: item.change_pct if item.change_pct is not None else -999, reverse=True)
        except Exception as exc:
            log.warning("China board quotes failed: %s", exc)
            notes.append("A股板块行情暂时无法获取")

        try:
            data = await _fetch_ulist(client, ",".join(code for code, _, _ in GOLD_QUOTES))
            for code, fallback, display in GOLD_QUOTES:
                symbol = code.split(".", 1)[1]
                row = data.get(symbol)
                if not row:
                    continue
                unit = "USD/oz" if symbol == "XAU" else ("元/克" if symbol.startswith("AU") else "")
                gold.append(
                    Quote(
                        code=display,
                        name=fallback,
                        price=_num(row.get("f2")),
                        change_pct=_num(row.get("f3")),
                        unit=unit,
                    )
                )
        except Exception as exc:
            log.warning("Gold quotes failed: %s", exc)
            notes.append("黄金行情暂时无法获取")

    return MarketSnapshot(us=us, china=china, gold=gold, note="；".join(notes))


def format_change(pct: float | None) -> str:
    if pct is None:
        return "—"
    sign = "+" if pct > 0 else ""
    return f"{sign}{pct:.2f}%"


def change_color(pct: float | None) -> str:
    if pct is None:
        return "#6b7280"
    if pct > 0:
        return "#dc2626"  # A-share convention: red = up
    if pct < 0:
        return "#16a34a"
    return "#6b7280"
