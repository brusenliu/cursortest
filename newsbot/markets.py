from __future__ import annotations

import asyncio
import json
import logging
import re
from dataclasses import dataclass

import httpx

log = logging.getLogger("newsbot.markets")

UA = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/plain, */*",
}

# Rough market-cap leaders. 105 = NASDAQ, 106 = NYSE on East Money.
US_TOP10 = [
    ("105.NVDA", "NVDA", "英伟达"),
    ("105.MSFT", "MSFT", "微软"),
    ("105.AAPL", "AAPL", "苹果"),
    ("105.GOOGL", "GOOGL", "谷歌"),
    ("105.AMZN", "AMZN", "亚马逊"),
    ("105.META", "META", "Meta"),
    ("105.AVGO", "AVGO", "博通"),
    ("105.TSLA", "TSLA", "特斯拉"),
    ("106.BRK_B", "BRK-B", "伯克希尔B"),
    ("106.JPM", "JPM", "摩根大通"),
]

# Major A-share industry / theme boards (East Money codes).
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

# Sina industry board name → our display name (fallback when East Money is down).
SINA_CN_MAP = [
    ("酿酒行业", "白酒"),
    ("电子器件", "半导体"),
    ("电子信息", "人工智能"),
    ("汽车制造", "新能源车"),
    ("发电设备", "光伏设备"),
    ("金融行业", "金融"),
    ("房地产", "房地产"),
    ("生物制药", "医药"),
    ("煤炭行业", "煤炭"),
    ("有色金属", "有色金属"),
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
        "https://push2delay.eastmoney.com/api/qt/ulist.np/get",
        "https://push2.eastmoney.com/api/qt/ulist.np/get",
    )
    last_error: Exception | None = None
    for host in hosts:
        for attempt in range(2):
            try:
                response = await client.get(
                    host,
                    params=params,
                    timeout=20,
                    headers={**UA, "Referer": "https://quote.eastmoney.com/"},
                )
                if response.status_code >= 500:
                    raise httpx.HTTPStatusError(
                        f"{response.status_code}",
                        request=response.request,
                        response=response,
                    )
                response.raise_for_status()
                payload = response.json()
                rows = ((payload.get("data") or {}).get("diff")) or []
                if not rows:
                    raise ValueError("empty eastmoney ulist")
                return {str(row.get("f12")): row for row in rows}
            except Exception as exc:
                last_error = exc
                await asyncio.sleep(0.4 * (attempt + 1))
    assert last_error is not None
    raise last_error


async def _yahoo_quote(client: httpx.AsyncClient, symbol: str) -> tuple[float | None, float | None]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
    response = await client.get(
        url,
        params={"interval": "1d", "range": "5d"},
        timeout=20,
        headers=UA,
    )
    response.raise_for_status()
    result = (response.json().get("chart") or {}).get("result") or []
    if not result:
        return None, None
    meta = result[0].get("meta") or {}
    price = _num(meta.get("regularMarketPrice"))
    prev = _num(meta.get("chartPreviousClose") or meta.get("previousClose"))
    pct = None
    if price is not None and prev:
        pct = (price - prev) / prev * 100
    return price, pct


async def _fetch_us_yahoo(client: httpx.AsyncClient) -> list[Quote]:
    quotes: list[Quote] = []
    for _, yahoo_sym, name in US_TOP10:
        try:
            price, pct = await _yahoo_quote(client, yahoo_sym)
            if price is None and pct is None:
                continue
            quotes.append(
                Quote(
                    code=yahoo_sym.replace("-", "."),
                    name=name,
                    price=price,
                    change_pct=pct,
                    unit="USD",
                )
            )
        except Exception as exc:
            log.warning("Yahoo US quote failed %s: %s", yahoo_sym, exc)
    return quotes


async def _fetch_gold_yahoo(client: httpx.AsyncClient) -> list[Quote]:
    try:
        price, pct = await _yahoo_quote(client, "GC=F")
        if price is None:
            return []
        return [
            Quote(
                code="GC=F",
                name="COMEX黄金",
                price=price,
                change_pct=pct,
                unit="USD/oz",
            )
        ]
    except Exception as exc:
        log.warning("Yahoo gold quote failed: %s", exc)
        return []


async def _fetch_china_sina(client: httpx.AsyncClient) -> list[Quote]:
    url = "https://vip.stock.finance.sina.com.cn/q/view/newSinaHy.php"
    response = await client.get(
        url,
        timeout=20,
        headers={**UA, "Referer": "https://finance.sina.com.cn"},
    )
    response.raise_for_status()
    match = re.search(r"=\s*(\{.*\})\s*;?\s*$", response.text, re.S)
    if not match:
        raise ValueError("unexpected sina industry payload")
    data = json.loads(match.group(1))
    by_name: dict[str, tuple[str, float | None]] = {}
    for raw in data.values():
        parts = str(raw).split(",")
        if len(parts) < 6:
            continue
        board_name = parts[1].strip()
        by_name[board_name] = (parts[0], _num(parts[5]))

    quotes: list[Quote] = []
    for sina_name, display in SINA_CN_MAP:
        hit = by_name.get(sina_name)
        if not hit:
            continue
        code, pct = hit
        quotes.append(Quote(code=code, name=display, price=None, change_pct=pct))
    quotes.sort(key=lambda item: item.change_pct if item.change_pct is not None else -999, reverse=True)
    return quotes


async def fetch_markets() -> MarketSnapshot:
    notes: list[str] = []
    us: list[Quote] = []
    china: list[Quote] = []
    gold: list[Quote] = []

    async with httpx.AsyncClient(headers=UA, follow_redirects=True) as client:
        # --- US ---
        try:
            data = await _fetch_ulist(client, ",".join(code for code, _, _ in US_TOP10))
            for code, yahoo_sym, fallback in US_TOP10:
                symbol = code.split(".", 1)[1]
                row = data.get(symbol) or data.get(symbol.replace("_", "."))
                if not row:
                    continue
                us.append(
                    Quote(
                        code=symbol.replace("_", "."),
                        name=fallback,
                        price=_num(row.get("f2")),
                        change_pct=_num(row.get("f3")),
                        unit="USD",
                    )
                )
        except Exception as exc:
            log.warning("US EastMoney failed, trying Yahoo: %s", exc)
            us = await _fetch_us_yahoo(client)
            if us:
                notes.append("美股行情来自 Yahoo（东方财富暂不可用）")
            else:
                notes.append("美股行情暂时无法获取")

        # --- China boards ---
        try:
            data = await _fetch_ulist(client, ",".join(code for code, _ in CN_BOARDS))
            cn_map = {code.split(".", 1)[1]: zh for code, zh in CN_BOARDS}
            for code, fallback in CN_BOARDS:
                symbol = code.split(".", 1)[1]
                row = data.get(symbol)
                if not row:
                    continue
                name = cn_map.get(symbol) or str(row.get("f14") or symbol)
                name = name.replace("Ⅱ", "").replace("概念", "").strip()
                china.append(
                    Quote(
                        code=symbol,
                        name=name or fallback,
                        price=_num(row.get("f2")),
                        change_pct=_num(row.get("f3")),
                    )
                )
            china.sort(
                key=lambda item: item.change_pct if item.change_pct is not None else -999,
                reverse=True,
            )
        except Exception as exc:
            log.warning("China EastMoney failed, trying Sina: %s", exc)
            try:
                china = await _fetch_china_sina(client)
                if china:
                    notes.append("A股板块来自新浪行业（东方财富暂不可用）")
                else:
                    notes.append("A股板块行情暂时无法获取")
            except Exception as sina_exc:
                log.warning("China Sina boards failed: %s", sina_exc)
                notes.append("A股板块行情暂时无法获取")

        # --- Gold ---
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
            log.warning("Gold EastMoney failed, trying Yahoo: %s", exc)
            gold = await _fetch_gold_yahoo(client)
            if gold:
                notes.append("黄金行情来自 Yahoo（东方财富暂不可用）")
            else:
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
