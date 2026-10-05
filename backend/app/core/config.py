from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8050
    serpapi_api_key: str = ""
    database_url: str = "postgresql://gap:gap@localhost:5432/gap"
    allowed_origins: str = "http://localhost:3000"
    search_cache_dir: str = ".cache/serpapi"
    serpapi_concurrency: int = 3

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
