from collections import Counter
import json
from pathlib import Path

import requests

BASE_URL = "https://environment.data.gov.uk/flood-monitoring"

LATITUDE = 53.4808
LONGITUDE = -2.2426
DISTANCE_KM = 35

session = requests.Session()
session.headers.update(
    {
        "User-Agent": "greater-manchester-flood-monitoring-data-platform/0.1"
    }
)


def fetch_json(endpoint: str, params: dict | None = None) -> dict:
    response = session.get(
        f"{BASE_URL}{endpoint}",
        params=params,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    station_payload = fetch_json(
        "/id/stations",
        {
            "lat": LATITUDE,
            "long": LONGITUDE,
            "dist": DISTANCE_KM,
            "_view": "full",
            "_limit": 500,
        },
    )

    stations = station_payload.get("items", [])

    flood_payload = fetch_json(
        "/id/floods",
        {
            "lat": LATITUDE,
            "long": LONGITUDE,
            "dist": DISTANCE_KM,
        },
    )

    floods = flood_payload.get("items", [])

    rivers = Counter(
        station.get("riverName", "Unknown")
        for station in stations
    )

    towns = Counter(
        station.get("town", "Unknown")
        for station in stations
    )

    print("=" * 70)
    print("GREATER MANCHESTER ENVIRONMENT AGENCY SOURCE PROFILE")
    print("=" * 70)

    print(f"\nStations within {DISTANCE_KM} km: {len(stations)}")
    print(f"Current flood warnings / alerts: {len(floods)}")

    print("\nTOP RIVERS")
    for river, count in rivers.most_common(15):
        print(f"{river}: {count}")

    print("\nTOP TOWNS")
    for town, count in towns.most_common(15):
        print(f"{town}: {count}")

    print("\nFIRST 15 STATIONS")
    for station in stations[:15]:
        print(
            station.get("stationReference"),
            "|",
            station.get("label"),
            "|",
            station.get("riverName"),
            "|",
            station.get("town"),
            "|",
            station.get("lat"),
            "|",
            station.get("long"),
        )

    print("\nSTATION FIELD NAMES")
    station_fields = sorted(
        {
            key
            for station in stations
            for key in station.keys()
        }
    )
    print(station_fields)

    print("\nFLOOD WARNING FIELD NAMES")
    flood_fields = sorted(
        {
            key
            for flood in floods
            for key in flood.keys()
        }
    )
    print(flood_fields)

    sample_dir = Path("data/sample")
    sample_dir.mkdir(parents=True, exist_ok=True)

    (sample_dir / "sample_stations.json").write_text(
        json.dumps(stations[:10], indent=2),
        encoding="utf-8",
    )

    (sample_dir / "sample_flood_warnings.json").write_text(
        json.dumps(floods[:10], indent=2),
        encoding="utf-8",
    )

    if stations:
        reference = stations[0]["stationReference"]

        readings_payload = fetch_json(
            f"/id/stations/{reference}/readings",
            {
                "latest": "",
                "_view": "full",
            },
        )

        readings = readings_payload.get("items", [])

        (sample_dir / "sample_latest_readings.json").write_text(
            json.dumps(readings, indent=2),
            encoding="utf-8",
        )

        print(
            f"\nLatest reading sample for station {reference}: "
            f"{len(readings)} measurement records"
        )

        if readings:
            print("\nREADING FIELD NAMES")
            print(sorted(readings[0].keys()))

    print("\nSource profile completed successfully.")


if __name__ == "__main__":
    main()
