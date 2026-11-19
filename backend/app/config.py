"""Application settings loaded from environment variables and the root .env file."""

from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "SFU CS Course Planner API"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = False
    sfu_courses_api_base_url: str = "https://api.sfucourses.com/v1/rest"
    sfu_courses_api_timeout_seconds: float = 10.0
    database_url: str = "postgresql+psycopg://planner:planner@localhost:5432/course_planner"
    session_ttl_days: int = Field(default=7, ge=1)
    session_cookie_name: str = "session"
    # None means "decide from app_env": Secure cookies everywhere except development.
    session_cookie_secure: bool | None = None
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cookie_secure(self) -> bool:
        """Whether the session cookie is only sent over HTTPS."""
        if self.session_cookie_secure is not None:
            return self.session_cookie_secure
        return self.app_env != "development"


settings = Settings()
