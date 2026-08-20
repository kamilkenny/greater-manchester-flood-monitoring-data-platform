from __future__ import annotations

from typing import Any

import requests

from flood_monitoring.config import Settings


class EnvironmentAgencyClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent":
                    "greater-manchester-flood-monitoring-data-platform/0.1"
            }
        )

    def _get(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = self.session.get(
            f"{self.settings.api_base_url}{endpoint}",
            params=params,
            timeout=self.settings.request_timeout_seconds,
        )
        response.raise_for_status()
        return response.json()

    def fetch_stations(self) -> dict[str, Any]:
        return self._get(
            "/id/stations",
            {
                "lat": self.settings.latitude,
                "long": self.settings.longitude,
                "dist": self.settings.radius_km,
                "_view": "full",
                "_limit": 500,
            },
        )

    def fetch_flood_warnings(self) -> dict[str, Any]:
        return self._get(
            "/id/floods",
            {
                "lat": self.settings.latitude,
                "long": self.settings.longitude,
                "dist": self.settings.radius_km,
            },
        )

    def fetch_latest_readings(self) -> dict[str, Any]:
        return self._get(
            "/data/readings",
            {
                "latest": "",
                "_limit": 20000,
            },
        )
