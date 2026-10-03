from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    model_provider: str = "mock"
    model_name: str = "qwen-plus"
    llm_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    llm_api_key: str = ""
    openai_base_url: str = ""
    openai_api_key: str = ""

    knowledge_base_path: str = "data/processed/chunks.json"
    top_k: int = 5
    run_log_dir: str = "run"
    run_log_enabled: bool = True
    backend_cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.backend_cors_origins.split(",") if origin.strip()]

    @property
    def effective_llm_base_url(self) -> str:
        return self.llm_base_url or self.openai_base_url

    @property
    def effective_llm_api_key(self) -> str:
        return self.llm_api_key or self.openai_api_key


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
