from functools import lru_cache
from pydantic_settings import BaseSettings

class EnvironmentSettings(BaseSettings):
    # PostgreSQL
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    DATABASE_URL: str

    # Redis
    REDIS_URL: str

    # RabbitMQ
    RABBITMQ_URL: str
    RABBITMQ_MANAGEMENT_PORT: int

    # Email Provider
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_FROM: str

    # Retry
    MAX_RETRY_ATTEMPTS: int
    RETRY_BACKOFF_BASE: int
    RETRY_INITIAL_DELAY: int

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

@lru_cache
def get_environment_variable():
    return EnvironmentSettings()