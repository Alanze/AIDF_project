from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    model_provider: str = "mock"
    model_name: str = "qwen2.5:7b-instruct"
    openai_base_url: str = "http://localhost:11434/v1"
    openai_api_key: str = "ollama"

    knowledge_base_path: str = "data/processed/chunks.json"
    top_k: int = 5
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
