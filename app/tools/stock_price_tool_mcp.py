from __future__ import annotations

from datetime import datetime, timezone

import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("stock-price-tool")


def _query_yahoo(symbol: str) -> dict:
    url = "https://query1.finance.yahoo.com/v7/finance/quote"
    response = requests.get(url, params={"symbols": symbol}, timeout=10)
    response.raise_for_status()
    payload = response.json()
    result = payload.get("quoteResponse", {}).get("result", [])
    if not result:
        raise ValueError(f"未查询到股票: {symbol}")
    quote = result[0]
    return {
        "symbol": quote.get("symbol", symbol),
        "name": quote.get("shortName") or quote.get("longName") or symbol,
        "price": quote.get("regularMarketPrice"),
        "currency": quote.get("currency", "USD"),
        "time": datetime.now(timezone.utc).isoformat(),
        "source": "Yahoo Finance",
    }


@mcp.tool()
def get_stock_price(symbol_or_name: str) -> dict:
    """获取指定股票的当前价格。输入示例：AAPL, TSLA, 600519.SS。"""
    return _query_yahoo(symbol_or_name.strip())


if __name__ == "__main__":
    mcp.run()
