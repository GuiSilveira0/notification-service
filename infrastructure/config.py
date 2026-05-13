from functools import lru_cache
from pydantic_settings import BaseSettings
import os

@lru_cache
def get_env_filename():
    runtime_env = os.getenv('ENV')
    return '.env' if runtime_env else '.env'

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
        env_file = get_env_filename()
        env_file_enconding = 'utf-8'

@lru_cache
def get_environment_variable():
    return EnvironmentSettings()