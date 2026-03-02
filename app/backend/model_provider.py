from langchain_ollama import ChatOllama, OllamaEmbeddings

from app.backend.config import AppSettings


def build_chat_model(settings: AppSettings) -> ChatOllama:
    return ChatOllama(
        model=settings.ollama.model,
        base_url=settings.ollama.base_url,
        temperature=0.2,
    )


def build_embeddings(settings: AppSettings) -> OllamaEmbeddings:
    return OllamaEmbeddings(
        model=settings.ollama.embedding_model,
        base_url=settings.ollama.base_url,
    )
