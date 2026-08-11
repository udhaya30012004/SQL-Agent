import os
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Agentic Data Analyst API"
    
    # CORS Origins (frontend URLs allowed to connect)
    # E.g., JSON list: '["http://localhost:3000", "http://localhost:5173"]'
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # ==========================================
    # AUTHENTICATION / JWT
    # ==========================================
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # API Keys
    GROQ_API: str = ""

    # Database strings
    # PostgreSQL Pagila Connection for SQL Agent queries
    CONNECTION_STRING: str = (
        "postgresql+psycopg2://postgres:1234@localhost:5432/pagila"
    )

    # SQLite database connection for backend metadata:
    # users, chat sessions, and chat messages.
    DATABASE_URL: str = (
        "sqlite:///./agent_backend.db"
    )

    # Directory where charts HTML/assets are written
    # We resolve it relative to the parent project directory
    CHARTS_DIR: str = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "SQL_Agent", "artifacts", "charts")
    )

    model_config = SettingsConfigDict(
        # Look for the .env file in the root workspace directory
        env_file=os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
