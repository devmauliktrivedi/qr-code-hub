from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


APP_DIR = Path(__file__).resolve().parents[1]
load_dotenv(APP_DIR / ".env")

DEFAULT_SECRET_KEY = "change-me-before-deploying"


def _resolve_database_path(raw_path: str) -> Path:
    candidate = Path(raw_path)
    if candidate.is_absolute():
        return candidate
    return APP_DIR / candidate


def _parse_admin_usernames(raw_value: str) -> tuple[str, ...]:
    usernames = []
    for item in raw_value.split(","):
        cleaned = item.strip().lower()
        if cleaned and cleaned not in usernames:
            usernames.append(cleaned)
    return tuple(usernames)


@dataclass(frozen=True)
class Settings:
    app_name: str = "QR Code Hub | By Krishna"
    page_icon: str = "🔗"
    cookie_prefix: str = "qr_code_hub_secure_"
    app_dir: Path = APP_DIR
    avatar_dir: Path = APP_DIR / "avatars"
    sql_dir: Path = APP_DIR / "sql"
    data_dir: Path = APP_DIR / "data"
    secret_key: str = os.getenv("SECRET_KEY", DEFAULT_SECRET_KEY)
    database_path: Path = _resolve_database_path(
        os.getenv("DATABASE_PATH", "data/qr_code_hub.db")
    )
    admin_usernames: tuple[str, ...] = field(
        default_factory=lambda: _parse_admin_usernames(os.getenv("ADMIN_USERNAMES", "kisu"))
    )

    @property
    def using_default_secret(self) -> bool:
        return self.secret_key == DEFAULT_SECRET_KEY

    @property
    def has_explicit_admins(self) -> bool:
        return bool(self.admin_usernames)


settings = Settings()


def ensure_runtime_dirs() -> None:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    settings.sql_dir.mkdir(parents=True, exist_ok=True)
