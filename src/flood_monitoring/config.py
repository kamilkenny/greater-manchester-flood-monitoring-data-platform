from dataclasses import dataclass
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    api_base_url: str
    latitude: float
    longitude: float
    radius_km: float
    request_timeout_seconds: int
    raw_dir: Path
    staging_dir: Path


def load_settings() -> Settings:
    return Settings(
        api_base_url=os.getenv(
            "EA_API_BASE_URL",
            "https://environment.data.gov.uk/flood-monitoring",
        ),
        latitude=float(os.getenv("GM_LATITUDE", "53.4808")),
        longitude=float(os.getenv("GM_LONGITUDE", "-2.2426")),
        radius_km=float(os.getenv("GM_RADIUS_KM", "35")),
        request_timeout_seconds=int(
            os.getenv("EA_REQUEST_TIMEOUT_SECONDS", "60")
        ),
        raw_dir=Path("data/raw"),
        staging_dir=Path("data/staging"),
    )
