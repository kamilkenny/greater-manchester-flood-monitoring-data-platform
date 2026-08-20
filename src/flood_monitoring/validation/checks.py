from __future__ import annotations

from collections import Counter
from typing import Any


def duplicate_count(
    rows: list[dict[str, Any]],
    fields: tuple[str, ...],
) -> int:
    keys = [
        tuple(row.get(field) for field in fields)
        for row in rows
    ]

    counts = Counter(keys)

    return sum(
        count - 1
        for count in counts.values()
        if count > 1
    )


def build_quality_report(
    stations: list[dict[str, Any]],
    measures: list[dict[str, Any]],
    readings: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
) -> dict[str, Any]:
    station_duplicates = duplicate_count(
        stations,
        ("station_reference",),
    )

    measure_duplicates = duplicate_count(
        measures,
        ("measure_url",),
    )

    reading_duplicates = duplicate_count(
        readings,
        ("measure_url", "reading_datetime"),
    )

    local_measure_count = len(
        {
            row.get("measure_url")
            for row in measures
            if row.get("measure_url")
        }
    )

    reading_measure_count = len(
        {
            row.get("measure_url")
            for row in readings
            if row.get("measure_url")
        }
    )

    coverage = (
        round(
            100 * reading_measure_count / local_measure_count,
            2,
        )
        if local_measure_count
        else 0.0
    )

    errors = []

    if not stations:
        errors.append("No monitoring stations were returned.")

    if station_duplicates:
        errors.append(
            f"{station_duplicates} duplicate station keys detected."
        )

    if measure_duplicates:
        errors.append(
            f"{measure_duplicates} duplicate measure keys detected."
        )

    if reading_duplicates:
        errors.append(
            f"{reading_duplicates} duplicate reading keys detected."
        )

    if not readings:
        errors.append(
            "No latest readings matched the monitoring area."
        )

    return {
        "station_rows": len(stations),
        "measure_rows": len(measures),
        "reading_rows": len(readings),
        "warning_rows": len(warnings),
        "station_duplicates": station_duplicates,
        "measure_duplicates": measure_duplicates,
        "reading_duplicates": reading_duplicates,
        "stations_missing_river_name": sum(
            not row.get("river_name")
            for row in stations
        ),
        "stations_missing_town": sum(
            not row.get("town")
            for row in stations
        ),
        "stations_missing_coordinates": sum(
            row.get("latitude") is None
            or row.get("longitude") is None
            for row in stations
        ),
        "readings_missing_value": sum(
            row.get("value") is None
            for row in readings
        ),
        "reading_measure_coverage_pct": coverage,
        "errors": errors,
        "status": "PASSED" if not errors else "FAILED",
    }
