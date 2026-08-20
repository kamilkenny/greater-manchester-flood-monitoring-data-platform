from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pandas as pd

from flood_monitoring.config import load_settings
from flood_monitoring.ingestion.environment_agency import (
    EnvironmentAgencyClient,
)
from flood_monitoring.ingestion.transforms import (
    MEASURE_COLUMNS,
    READING_COLUMNS,
    STATION_COLUMNS,
    WARNING_COLUMNS,
    normalise_measures,
    normalise_readings,
    normalise_stations,
    normalise_warnings,
)
from flood_monitoring.validation import build_quality_report


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(
        json.dumps(
            payload,
            indent=2,
            ensure_ascii=False,
            default=str,
        ),
        encoding="utf-8",
    )


def write_csv(
    path: Path,
    rows: list[dict],
    columns: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    pd.DataFrame(
        rows,
        columns=columns,
    ).to_csv(
        path,
        index=False,
    )


def main() -> None:
    settings = load_settings()

    started = datetime.now(timezone.utc)

    run_id = started.strftime("%Y%m%dT%H%M%SZ")

    client = EnvironmentAgencyClient(settings)

    print("Fetching Environment Agency stations...")
    station_payload = client.fetch_stations()

    print("Fetching current flood warnings...")
    warning_payload = client.fetch_flood_warnings()

    print("Fetching latest national readings...")
    reading_payload = client.fetch_latest_readings()

    stations_raw = station_payload.get("items", [])
    warnings_raw = warning_payload.get("items", [])
    readings_raw = reading_payload.get("items", [])

    raw_path = (
        settings.raw_dir
        / started.strftime("%Y")
        / started.strftime("%m")
        / started.strftime("%d")
        / run_id
    )

    write_json(
        raw_path / "stations.json",
        station_payload,
    )

    write_json(
        raw_path / "flood_warnings.json",
        warning_payload,
    )

    write_json(
        raw_path / "latest_readings.json",
        reading_payload,
    )

    stations = normalise_stations(stations_raw)

    measures = normalise_measures(stations_raw)

    readings = normalise_readings(
        readings_raw,
        measures,
    )

    warnings = normalise_warnings(warnings_raw)

    quality = build_quality_report(
        stations,
        measures,
        readings,
        warnings,
    )

    latest = settings.staging_dir / "latest"

    write_csv(
        latest / "stations.csv",
        stations,
        STATION_COLUMNS,
    )

    write_csv(
        latest / "measures.csv",
        measures,
        MEASURE_COLUMNS,
    )

    write_csv(
        latest / "latest_readings.csv",
        readings,
        READING_COLUMNS,
    )

    write_csv(
        latest / "flood_warnings.csv",
        warnings,
        WARNING_COLUMNS,
    )

    finished = datetime.now(timezone.utc)

    summary = {
        "run_id": run_id,
        "status": quality["status"],
        "started_at_utc": started.isoformat(),
        "finished_at_utc": finished.isoformat(),
        "duration_seconds": round(
            (finished - started).total_seconds(),
            3,
        ),
        "monitoring_area": {
            "centre_latitude": settings.latitude,
            "centre_longitude": settings.longitude,
            "radius_km": settings.radius_km,
        },
        "source_counts": {
            "stations": len(stations_raw),
            "national_latest_readings":
                len(readings_raw),
            "current_flood_warnings":
                len(warnings_raw),
        },
        "staged_counts": {
            "stations": len(stations),
            "measures": len(measures),
            "local_latest_readings": len(readings),
            "flood_warnings": len(warnings),
        },
        "data_quality": quality,
        "raw_snapshot_directory": str(raw_path),
    }

    write_json(
        latest / "etl_run_summary.json",
        summary,
    )

    print()
    print("=" * 70)
    print("INGESTION SUMMARY")
    print("=" * 70)
    print(json.dumps(summary, indent=2))

    if quality["errors"]:
        raise SystemExit(
            "Pipeline failed data-quality validation."
        )


if __name__ == "__main__":
    main()
