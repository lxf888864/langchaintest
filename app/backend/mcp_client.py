from __future__ import annotations

import anyio
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

    def fetch_stock_price(self, symbol_or_name: str) -> dict:
        return anyio.run(self._fetch_async, symbol_or_name)
