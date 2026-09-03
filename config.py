from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Realtime MockExam"
    secret_key: str = "0000"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    # Defaulting to PostgreSQL for production readiness
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/mockexam"
    redis_url: str = "redis://localhost:6379/0"
    debug: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
