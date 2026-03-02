from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel


class OllamaConfig(BaseModel):
    base_url: str
    model: str
    embedding_model: str


class StorageConfig(BaseModel):
    upload_dir: str
    chroma_dir: str
    collection_name: str


class MCPConfig(BaseModel):
    server_command: str
    server_args: list[str]


class RetrievalConfig(BaseModel):
    chunk_size: int
    chunk_overlap: int
    top_k: int


class AppSettings(BaseModel):
    ollama: OllamaConfig
    storage: StorageConfig
    mcp: MCPConfig
    retrieval: RetrievalConfig


def load_settings(path: str = "app/config/settings.yaml") -> AppSettings:
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f)
    return AppSettings(**raw)
