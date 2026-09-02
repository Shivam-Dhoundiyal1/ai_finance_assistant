"""Load configuration from config.yaml and environment variables."""
from pathlib import Path
from typing import Any

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_config() -> dict[str, Any]:
    """Load config.yaml from project root."""
    path = _project_root() / "config.yaml"
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


class Settings(BaseSettings):
    """Runtime settings; env overrides config."""

    app_name: str = "Finnie"
    app_version: str = "1.0.0"

    # LLM
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_temperature: float = 0.3
    llm_max_tokens: int = 1024

    # RAG
    rag_persist_directory: str = "data/chroma"
    rag_collection_name: str = "finance_knowledge"
    rag_embedding_model: str = "all-MiniLM-L6-v2"
    rag_chunk_size: int = 800
    rag_chunk_overlap: int = 200
    rag_top_k: int = 5
    rag_knowledge_path: str = "src/data/knowledge"

    # Market
    alpha_vantage_api_key: str | None = None
    tavily_api_key: str | None = None
    market_provider: str = "yfinance"
    market_cache_ttl: int = 300

    model_config = SettingsConfigDict(
        env_file=str(_project_root() / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        cfg = load_config()
        app = cfg.get("app", {})
        llm = cfg.get("llm", {})
        rag = cfg.get("rag", {})
        market = cfg.get("market", {})
        
        # Build kwargs, avoid passing None for API keys to allow env vars to be used
        kwargs = {
            "app_name": app.get("name", "Finnie"),
            "app_version": app.get("version", "1.0.0"),
            "llm_provider": llm.get("provider", "openai"),
            "llm_model": llm.get("model", "gpt-4o-mini"),
            "llm_temperature": float(llm.get("temperature", 0.3)),
            "llm_max_tokens": int(llm.get("max_tokens", 1024)),
            "rag_persist_directory": rag.get("persist_directory", "data/chroma"),
            "rag_collection_name": rag.get("collection_name", "finance_knowledge"),
            "rag_embedding_model": rag.get("embedding_model", "all-MiniLM-L6-v2"),
            "rag_chunk_size": int(rag.get("chunk_size", 800)),
            "rag_chunk_overlap": int(rag.get("chunk_overlap", 200)),
            "rag_top_k": int(rag.get("top_k", 5)),
            "rag_knowledge_path": rag.get("knowledge_path", "src/data/knowledge"),
            "market_provider": market.get("provider", "yfinance"),
            "market_cache_ttl": int(market.get("cache_ttl_seconds", 300)),
        }
        
        # Only add API keys if they're explicitly in config (don't override env vars)
        if "openai_api_key" in cfg.get("llm", {}):
            kwargs["openai_api_key"] = cfg["llm"]["openai_api_key"]
        if "gemini_api_key" in cfg.get("llm", {}):
            kwargs["gemini_api_key"] = cfg["llm"]["gemini_api_key"]
        if "tavily_api_key" in cfg.get("market", {}):
            kwargs["tavily_api_key"] = cfg["market"]["tavily_api_key"]

        _settings = Settings(**kwargs)
    return _settings
