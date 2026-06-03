from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    app_name: str = "Denoise Web App API"
    env: str = "dev"
    host: str = "0.0.0.0"
    port: int = 8000
    max_upload_mb: int = 64
    cors_origins: list[str] = None  # type: ignore[assignment]
    data_dir: Path = Path("analysis/denoise_selection/webapp/data")

    def __post_init__(self) -> None:
        if self.cors_origins is None:
            self.cors_origins = ["http://localhost:5173", "http://127.0.0.1:5173"]


def load_settings() -> Settings:
    s = Settings()
    s.env = os.getenv("APP_ENV", s.env)
    s.host = os.getenv("APP_HOST", s.host)
    s.port = int(os.getenv("APP_PORT", str(s.port)))
    s.max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", str(s.max_upload_mb)))
    cors_raw = os.getenv("CORS_ORIGINS", "")
    if cors_raw.strip():
        s.cors_origins = [x.strip() for x in cors_raw.split(",") if x.strip()]
    s.data_dir = Path(os.getenv("APP_DATA_DIR", str(s.data_dir))).resolve()
    return s


SETTINGS = load_settings()

