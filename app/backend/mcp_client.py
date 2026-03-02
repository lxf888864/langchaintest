from __future__ import annotations

from datetime import datetime, timezone

import anyio
import requests
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.backend.config import AppSettings


class MCPStockClient:
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
    def _fetch_direct(symbol_or_name: str) -> dict:
        url = "https://query1.finance.yahoo.com/v7/finance/quote"
        response = requests.get(url, params={"symbols": symbol_or_name}, timeout=10)
        response.raise_for_status()
        payload = response.json()
        result = payload.get("quoteResponse", {}).get("result", [])
        if not result:
            raise ValueError(f"未查询到股票: {symbol_or_name}")
        quote = result[0]
        return {
            "symbol": quote.get("symbol", symbol_or_name),
            "name": quote.get("shortName") or quote.get("longName") or symbol_or_name,
            "price": quote.get("regularMarketPrice"),
            "currency": quote.get("currency", "USD"),
            "time": datetime.now(timezone.utc).isoformat(),
            "source": "Yahoo Finance (HTTP fallback)",
        }

    def fetch_stock_price(self, symbol_or_name: str) -> dict:
        symbol_or_name = symbol_or_name.strip()
        try:
            return anyio.run(self._fetch_async, symbol_or_name)
        except Exception as exc:
            # 在 MCP 进程启动失败（常见于 Windows python 命令或环境差异）时回退到直连查询，
            # 避免把 ExceptionGroup 直接暴露给前端。
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
