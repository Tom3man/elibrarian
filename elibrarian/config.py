from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ebooks_library: Path
    ebooks_inbox: Path

    model_config = SettingsConfigDict(
        env_file="paths.env",
        env_file_encoding="utf-8",
    )


settings = Settings()
