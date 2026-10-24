from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/ folder (config.py lives in backend/app/)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    # Secrets: loaded from backend/.env, never written in code
    TINYFISH_API_KEY: str
    SECRET_KEY: str
    LLM_API_KEY: str = ""  # empty until we pick an LLM (needed in Phase 3)

    # Non-secret settings with safe defaults
    DATABASE_URL: str = f"sqlite:///{(BASE_DIR / 'visa_watchdog.db').as_posix()}"
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")


settings = Settings()