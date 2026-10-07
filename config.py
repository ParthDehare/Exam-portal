from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "Realtime MockExam"
    secret_key: str = "0000"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    # Defaulting to SQLite for simple deployment without external dependencies
    database_url: str = "sqlite+aiosqlite:///./exam_portal.db"
    redis_url: str = "redis://localhost:6379/0" # Kept for backward compatibility, but unused
    gemini_api_key: str = ""
    debug: bool = True

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
