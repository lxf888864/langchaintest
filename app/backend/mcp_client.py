from __future__ import annotations

import re
import time
from datetime import datetime, timezone

import anyio
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.backend.config import AppSettings


class MCPStockClient:
    _NAME_TO_SYMBOL = {
        "腾讯控股": "0700.HK",
        "阿里巴巴": "9988.HK",
        "贵州茅台": "600519.SS",
        "宁德时代": "300750.SZ",
    }

    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings

    async def _fetch_async(self, symbol_or_name: str) -> dict:
        server_params = StdioServerParameters(
            command=self.settings.mcp.server_command,
            args=self.settings.mcp.server_args,
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool("get_stock_price", {"symbol_or_name": symbol_or_name})
                if hasattr(result, "content") and result.content:
                    text_content = result.content[0]
                    if hasattr(text_content, "text"):
                        import json

                        return json.loads(text_content.text)
                if hasattr(result, "structuredContent"):
                    return result.structuredContent
                raise RuntimeError("MCP 工具返回格式不支持")

    @staticmethod
    def _flatten_exception_message(exc: BaseException) -> str:
        group_type = globals().get("BaseExceptionGroup")
        if group_type is not None and isinstance(exc, group_type):
            nested = [MCPStockClient._flatten_exception_message(e) for e in exc.exceptions]
            return " | ".join([m for m in nested if m])
        return str(exc)

    @staticmethod
    def _is_chinese_text(text: str) -> bool:
        return bool(re.search(r"[\u4e00-\u9fff]", text))

    def _resolve_symbol(self, symbol_or_name: str) -> str:
        symbol = symbol_or_name.strip()
        if symbol in self._NAME_TO_SYMBOL:
            return self._NAME_TO_SYMBOL[symbol]
        return symbol

    @staticmethod
    def _fetch_from_yahoo(symbol: str) -> dict:
        url = "https://query1.finance.yahoo.com/v7/finance/quote"
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = requests.get(url, params={"symbols": symbol}, timeout=10)
                if response.status_code == 429 and attempt < 2:
                    time.sleep(1.5 * (attempt + 1))
                    continue
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
                    "source": "Yahoo Finance (HTTP fallback)",
                }
            except Exception as exc:
                last_error = exc
        if last_error is None:
            raise RuntimeError("Yahoo 查询失败")
        raise last_error

    @staticmethod
    def _to_tencent_symbol(symbol: str) -> str:
        upper = symbol.strip().upper()
        if upper.endswith(".HK"):
            return f"s_hk{upper[:-3].zfill(5)}"
        if upper.endswith(".SS") or upper.endswith(".SH"):
            return f"s_sh{upper[:-3]}"
        if upper.endswith(".SZ"):
            return f"s_sz{upper[:-3]}"
        if upper.isdigit() and len(upper) == 6:
            prefix = "sh" if upper.startswith("6") else "sz"
            return f"s_{prefix}{upper}"
        raise ValueError(f"腾讯行情接口暂不支持该代码格式: {symbol}")

    @classmethod
    def _fetch_from_tencent(cls, symbol: str) -> dict:
        ts_symbol = cls._to_tencent_symbol(symbol)
        url = "https://qt.gtimg.cn/q=" + ts_symbol
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        response.encoding = "gbk"
        body = response.text
        if "~" not in body:
            raise ValueError(f"腾讯行情返回异常: {body[:120]}")
        chunks = body.split("\"")
        if len(chunks) < 2:
            raise ValueError(f"腾讯行情返回无法解析: {body[:120]}")
        parts = chunks[1].split("~")
        if len(parts) < 4:
            raise ValueError(f"腾讯行情字段不足: {body[:120]}")
        name = parts[1] or symbol
        raw_symbol = parts[2] or symbol
        price = parts[3]
        if not price:
            raise ValueError(f"腾讯行情无价格字段: {body[:120]}")
        currency = "HKD" if ".HK" in symbol.upper() else "CNY"
        return {
            "symbol": symbol,
            "name": name,
            "price": float(price),
            "currency": currency,
            "time": datetime.now(timezone.utc).isoformat(),
            "source": f"Tencent Quote ({raw_symbol})",
        }

    def _fetch_direct(self, symbol_or_name: str) -> dict:
        symbol = self._resolve_symbol(symbol_or_name)
        errors: list[str] = []

        # 中文名或港股/A股优先补充腾讯行情通道，降低 Yahoo 429 对中文查询的影响。
        if self._is_chinese_text(symbol_or_name) or symbol.upper().endswith((".HK", ".SS", ".SZ", ".SH")):
            try:
                return self._fetch_from_tencent(symbol)
            except Exception as exc:
                errors.append(f"腾讯行情失败: {self._flatten_exception_message(exc)}")

        try:
            return self._fetch_from_yahoo(symbol)
        except Exception as exc:
            errors.append(f"Yahoo失败: {self._flatten_exception_message(exc)}")

        if self._is_chinese_text(symbol_or_name) and symbol == symbol_or_name:
            raise RuntimeError(
                "未识别该中文股票名称，请改用股票代码重试（如 腾讯控股->0700.HK、贵州茅台->600519.SS）。"
                + "；".join(errors)
            )

        raise RuntimeError("；".join(errors))

    def fetch_stock_price(self, symbol_or_name: str) -> dict:
        symbol_or_name = symbol_or_name.strip()
        try:
            return anyio.run(self._fetch_async, symbol_or_name)
        except Exception as exc:
            mcp_error = self._flatten_exception_message(exc)
            try:
                data = self._fetch_direct(symbol_or_name)
                data["mcp_warning"] = f"MCP 调用失败，已自动回退: {mcp_error}"
                return data
            except Exception as fallback_exc:
                fallback_error = self._flatten_exception_message(fallback_exc)
                raise RuntimeError(
                    f"获取股票价格失败。MCP错误: {mcp_error}; 直连回退错误: {fallback_error}"
                ) from fallback_exc
