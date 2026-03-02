from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.backend.agent_service import StockAgentService
from app.backend.config import load_settings
from app.backend.rag_service import RagService

settings = load_settings()
rag_service = RagService(settings)
agent_service = StockAgentService(settings, rag_service)

app = FastAPI(title="Stock Agent API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    stock_name: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    try:
        target = Path(settings.storage.upload_dir) / file.filename
        with target.open("wb") as f:
            content = await file.read()
            f.write(content)
        count = rag_service.ingest_file(target)
        return {"message": f"上传成功并切分入库 {count} 个片段", "filename": file.filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e


@app.post("/chat")
def chat(req: ChatRequest) -> dict:
    stock_name = req.stock_name.strip()
    if not stock_name or stock_name == "请输入股票名称，我可以为您生成评论":
        raise HTTPException(status_code=400, detail="请输入有效股票名称/代码")

    try:
        answer = agent_service.generate_comment(stock_name)
        return {"stock_name": stock_name, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
