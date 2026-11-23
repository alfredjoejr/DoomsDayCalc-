"""Application settings, database URL normalization, CORS origins, and Matplotlib theme tokens."""

from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BACKEND_DIR / ".env")

APP_NAME = "DoomsDayCalc Mortality Intelligence API"
APP_VERSION = "1.0.0"
API_V1_PREFIX = "/api/v1"


def _normalize_database_url(raw_url: str) -> str:
    url = raw_url.strip()
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


DATABASE_URL: str = _normalize_database_url(
    os.getenv("DATABASE_URL", "")
)
DB_HOSTADDR: str = os.getenv("DB_HOSTADDR", "").strip()

CORS_ORIGINS: list[str] = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]

CATEGORY_COLORS: dict[str, str] = {
    "pandemic": "#F43F5E",
    "war": "#F97316",
    "famine": "#EAB308",
    "disaster": "#06B6D4",
    "atrocity": "#A855F7",
    "industrial": "#10B981",
}


@dataclass(frozen=True)
class ThemePalette:
    figure_bg: str
    axes_bg: str
    text_primary: str
    text_secondary: str
    grid_color: str
    spine_color: str
    accent_crimson: str


THEMES: dict[str, ThemePalette] = {
    "obsidian_dark": ThemePalette(
        figure_bg="#090B10",
        axes_bg="#151B27",
        text_primary="#F8FAFC",
        text_secondary="#94A3B8",
        grid_color="#263042",
        spine_color="#334155",
        accent_crimson="#E11D48",
    ),
    "publication_light": ThemePalette(
        figure_bg="#F8FAFC",
        axes_bg="#FFFFFF",
        text_primary="#0F172A",
        text_secondary="#475569",
        grid_color="#E2E8F0",
        spine_color="#CBD5E1",
        accent_crimson="#BE123C",
    ),
}
