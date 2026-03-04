import os
from typing import Any

from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.backend.config import AppSettings


def _provider(value: str) -> str:
    return value.strip().lower()


def build_chat_model(settings: AppSettings) -> Any:
    provider = _provider(settings.llm_provider)
    if provider == "openai":
        api_key = settings.openai.api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("使用 OpenAI 时请在 settings.yaml 的 openai.api_key 配置密钥，或设置环境变量 OPENAI_API_KEY")
        return ChatOpenAI(
            model=settings.openai.model,
            api_key=api_key,
            base_url=settings.openai.base_url,
            temperature=0.2,
        )
    if provider == "ollama":
        return ChatOllama(
            model=settings.ollama.model,
            base_url=settings.ollama.base_url,
            temperature=0.2,
        )
    raise ValueError(f"不支持的 llm_provider: {settings.llm_provider}，可选值: ollama/openai")


def build_embeddings(settings: AppSettings) -> Any:
    provider = _provider(settings.embedding_provider)
    if provider == "openai":
        api_key = settings.openai.api_key or os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            raise ValueError("使用 OpenAI Embeddings 时请在 settings.yaml 的 openai.api_key 配置密钥，或设置环境变量 OPENAI_API_KEY")
        return OpenAIEmbeddings(
            model=settings.openai.embedding_model,
            api_key=api_key,
            base_url=settings.openai.base_url,
        )
    if provider == "ollama":
        return OllamaEmbeddings(
            model=settings.ollama.embedding_model,
            base_url=settings.ollama.base_url,
        )
    raise ValueError(f"不支持的 embedding_provider: {settings.embedding_provider}，可选值: ollama/openai")
