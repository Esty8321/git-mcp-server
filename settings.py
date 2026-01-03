from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


def get_default_env_path() -> Path:
    return Path(__file__).with_name(".env")


def _get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.environ.get(name, default)
    if value is None:
        return None
    return str(value).strip()


@dataclass(frozen=True)
class Settings:
    SMTP_HOST: Optional[str]
    SMTP_PORT: int
    SMTP_USERNAME: Optional[str]
    SMTP_PASSWORD: Optional[str]
    FROM_EMAIL: Optional[str]


def build_settings() -> Settings:
    smtp_port_raw = _get_env("SMTP_PORT", "587")
    try:
        smtp_port = int(smtp_port_raw) if smtp_port_raw else 587
    except ValueError:
        smtp_port = 587

    return Settings(
        SMTP_HOST=_get_env("SMTP_HOST"),
        SMTP_PORT=smtp_port,
        SMTP_USERNAME=_get_env("SMTP_USERNAME"),
        SMTP_PASSWORD=_get_env("SMTP_PASSWORD"),
        FROM_EMAIL=_get_env("FROM_EMAIL"),
    )
