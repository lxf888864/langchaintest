from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate

from app.backend.config import AppSettings
from app.backend.mcp_client import MCPStockClient
from app.backend.model_provider import build_chat_model
from app.backend.rag_service import RagService


class StockAgentService:
    def __init__(self, settings: AppSettings, rag_service: RagService) -> None:
        self.settings = settings
        self.rag_service = rag_service
        self.llm = build_chat_model(settings)
        self.stock_client = MCPStockClient(settings)

    def generate_comment(self, stock_name: str) -> str:
        stock_data = self.stock_client.fetch_stock_price(stock_name)
        docs = self.rag_service.retrieve(f"{stock_name} 基本面 财务 业务 风险")
        context = "\n\n".join([f"来源:{d.metadata.get('source', 'unknown')}\n{d.page_content}" for d in docs])

        prompt = ChatPromptTemplate.from_template(
            """
你是一个股票研究助手。请根据以下信息给出简洁、客观的股票评论。

[实时行情]
股票代码: {symbol}
股票名称: {name}
当前价格: {price} {currency}
行情时间: {time}
数据来源: {source}

[RAG资料]
{context}

要求：
1) 先给出一段总结（3-5句）。
2) 再给出“利好因素 / 风险因素”各至少2条。
3) 最后一行固定输出："以上内容仅供参考，不构成投资建议。"
            """
        )

        chain = prompt | self.llm
        response = chain.invoke(
            {
                "symbol": stock_data.get("symbol", stock_name),
                "name": stock_data.get("name", stock_name),
                "price": stock_data.get("price", "N/A"),
                "currency": stock_data.get("currency", "N/A"),
                "time": stock_data.get("time", "N/A"),
                "source": stock_data.get("source", "N/A"),
                "context": context or "未检索到用户上传资料。",
            }
        )
        return response.content
