from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://events_user:events_pass@db:5432/events_db"
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 300          # segundos
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://events_user:events_pass@db:5432/events_db"
    REDIS_URL: str = "redis://redis:6379/0"
    CACHE_TTL: int = 300          # segundos
    APP_ENV: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()