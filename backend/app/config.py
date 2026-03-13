from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Required
    FAL_KEY: str
    REDIS_URL: str
    SUPABASE_URL: str
    SUPABASE_SERVICE_KEY: str

    # Optional
    SENTRY_DSN: str = ""
    APP_ENV: str = "development"
    APP_VERSION: str = "1.0.0"
    CORS_ORIGINS: str = "http://localhost:3000"
    CELERY_CONCURRENCY: int = 3
    MAX_UPLOAD_SIZE_MB: int = 50
    TEMP_DIR: str = "/tmp/cherrypick"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
