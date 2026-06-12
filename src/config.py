"""Application configuration."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "raw"

INITIAL_CENTER: list[float] = [48.0, 85.0]
INITIAL_ZOOM = 3
SELECTED_ZOOM = 8

DEFAULT_TILE_URL = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png"
DEFAULT_TILE_ATTRIBUTION = (
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> '
    'contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
)
DEFAULT_TILE_LAYER_NAME = "CARTO Voyager"


@dataclass(frozen=True)
class AppSettings:
    """Runtime settings loaded from environment variables."""

    data_dir: Path
    tile_url: str
    tile_attribution: str
    tile_layer_name: str
    debug: bool


def load_settings() -> AppSettings:
    """Load app settings from environment variables and sensible defaults."""

    load_dotenv(PROJECT_ROOT / ".env")
    data_dir = Path(os.getenv("GLOBAL_LOCATION_DATA_DIR", str(DATA_DIR))).resolve()
    return AppSettings(
        data_dir=data_dir,
        tile_url=os.getenv("GLOBAL_LOCATION_TILE_URL", DEFAULT_TILE_URL),
        tile_attribution=os.getenv("GLOBAL_LOCATION_TILE_ATTRIBUTION", DEFAULT_TILE_ATTRIBUTION),
        tile_layer_name=os.getenv("GLOBAL_LOCATION_TILE_LAYER_NAME", DEFAULT_TILE_LAYER_NAME),
        debug=os.getenv("DASH_DEBUG", "false").strip().lower() in {"1", "true", "yes", "on"},
    )
