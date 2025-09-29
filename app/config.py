from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    env: str = "dev"
    cors_allow_origins: List[str] = ["*"]

    api_key_header_name: str = "x-api-key"
    api_key: str | None = None

    mistral_api_key: str | None = None
    mistral_model: str = "mistral-small-latest"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins(self) -> List[str]:
        raw = os.getenv("CORS_ALLOW_ORIGINS", "*")
        if raw.strip() == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",")]

# ✅ CETTE LIGNE DOIT RESTER
settings = Settings()
