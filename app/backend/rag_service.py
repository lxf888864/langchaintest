from __future__ import annotations

from pathlib import Path

from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.backend.config import AppSettings
from app.backend.model_provider import build_embeddings


class RagService:
    def __init__(self, settings: AppSettings) -> None:
        self.settings = settings
        Path(settings.storage.upload_dir).mkdir(parents=True, exist_ok=True)
        Path(settings.storage.chroma_dir).mkdir(parents=True, exist_ok=True)

        self.vectorstore = Chroma(
            collection_name=settings.storage.collection_name,
            embedding_function=build_embeddings(settings),
            persist_directory=settings.storage.chroma_dir,
        )
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.retrieval.chunk_size,
            chunk_overlap=settings.retrieval.chunk_overlap,
        )

    def _load_docs(self, file_path: Path) -> list[Document]:
        ext = file_path.suffix.lower()
        if ext in {".txt", ".md"}:
            loader = TextLoader(str(file_path), encoding="utf-8")
        elif ext == ".pdf":
            loader = PyPDFLoader(str(file_path))
        elif ext in {".docx", ".doc"}:
            loader = UnstructuredWordDocumentLoader(str(file_path))
        else:
            raise ValueError(f"不支持的文件类型: {ext}")
        return loader.load()

    def ingest_file(self, file_path: Path) -> int:
        docs = self._load_docs(file_path)
        chunks = self.splitter.split_documents(docs)
        for chunk in chunks:
            chunk.metadata["source"] = file_path.name
        self.vectorstore.add_documents(chunks)
        return len(chunks)

    def retrieve(self, query: str) -> list[Document]:
        retriever = self.vectorstore.as_retriever(search_kwargs={"k": self.settings.retrieval.top_k})
        return retriever.invoke(query)
