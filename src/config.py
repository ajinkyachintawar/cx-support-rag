from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    jina_api_key: str = Field(..., description="Jina AI API key for embeddings")
    gemini_api_key: str = Field(default="", description="Google Gemini API key (unused, kept for reference)")
    groq_api_key: str = Field(..., description="Groq API key for LLM synthesis")
    supabase_url: str = Field(..., description="Supabase project URL (PostgreSQL connection string)")
    supabase_service_key: str = Field(default="", description="Supabase service role key (unused with direct PG)")

    embedding_model: str = "jina-embeddings-v3"
    embedding_dimension: int = 1024
    embedding_api_url: str = "https://api.jina.ai/v1/embeddings"

    synthesis_model: str = "llama-3.3-70b-versatile"
    synthesis_max_tokens: int = 2048

    vector_top_k: int = 10
    keyword_top_k: int = 10
    fusion_top_n: int = 5   # retrieve 5, but synthesis uses top 3
    synthesis_top_k: int = 3  # number of chunks passed to LLM
    rrf_k: int = 60

    chunk_max_tokens: int = 400
    chunk_overlap_tokens: int = 50

    confidence_threshold: float = 0.4
    rrf_score_floor: float = 0.015

    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"
    audit_log_path: str = "logs/audit.jsonl"

    knowledge_base_path: str = "data/knowledge_base"

    model_config = {"env_file": ".env", "env_prefix": "KB_"}


settings = Settings()
