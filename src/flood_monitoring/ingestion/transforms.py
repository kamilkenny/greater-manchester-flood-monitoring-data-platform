from __future__ import annotations

from typing import Any


STATION_COLUMNS = [
    "station_reference",
    "station_name",
    "river_name",
    "town",
    "catchment_name",
    "latitude",
    "longitude",
    "status",
    "date_opened",
    "typical_range_low",
    "typical_range_high",
]

MEASURE_COLUMNS = [
    "measure_id",
    "measure_url",
    "station_reference",
    "parameter",
    "parameter_name",
    "qualifier",
    "unit_name",
    "period_seconds",
]

READING_COLUMNS = [
    "station_reference",
    "measure_id",
    "measure_url",
    "parameter",
    "qualifier",
    "unit_name",
    "reading_datetime",
    "reading_date",
    "value",
]

WARNING_COLUMNS = [
    "warning_id",
    "flood_area_id",
    "description",
    "county",
    "river_or_sea",
    "severity",
    "severity_level",
    "is_tidal",
    "time_raised",
    "time_message_changed",
    "time_severity_changed",
    "message",
]


def _uri(value: Any) -> str | None:
    if isinstance(value, str):
        return value

    if isinstance(value, dict):
        return value.get("@id")

    return None


def normalise_stations(
    stations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []

    for station in stations:
        scale = station.get("stageScale")

        if not isinstance(scale, dict):
            scale = {}

        rows.append(
            {
                "station_reference": station.get("stationReference"),
                "station_name": station.get("label"),
                "river_name": station.get("riverName"),
                "town": station.get("town"),
                "catchment_name": station.get("catchmentName"),
                "latitude": station.get("lat"),
                "longitude": station.get("long"),
                "status": station.get("status"),
                "date_opened": station.get("dateOpened"),
                "typical_range_low": scale.get("typicalRangeLow"),
                "typical_range_high": scale.get("typicalRangeHigh"),
            }
        )

    return rows


def normalise_measures(
    stations: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []

    for station in stations:
        station_reference = station.get("stationReference")

        for measure in station.get("measures") or []:
            if isinstance(measure, str):
                measure_url = measure
                measure = {}
            else:
                measure_url = measure.get("@id")

            measure_id = (
                measure_url.rstrip("/").split("/")[-1]
                if measure_url
                else None
            )

            rows.append(
                {
                    "measure_id": measure_id,
                    "measure_url": measure_url,
                    "station_reference": station_reference,
                    "parameter": measure.get("parameter"),
                    "parameter_name": measure.get("parameterName"),
                    "qualifier": measure.get("qualifier"),
                    "unit_name": measure.get("unitName"),
                    "period_seconds": measure.get("period"),
                }
            )

    return rows


def normalise_readings(
    readings: list[dict[str, Any]],
    measures: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    measure_lookup = {
        row["measure_url"]: row
        for row in measures
        if row.get("measure_url")
    }

    rows = []

    for reading in readings:
        measure_url = _uri(reading.get("measure"))

        measure = measure_lookup.get(measure_url)

        if measure is None:
            continue

        rows.append(
            {
                "station_reference":
                    measure.get("station_reference"),
                "measure_id": measure.get("measure_id"),
                "measure_url": measure_url,
                "parameter": measure.get("parameter"),
                "qualifier": measure.get("qualifier"),
                "unit_name": measure.get("unit_name"),
                "reading_datetime": reading.get("dateTime"),
                "reading_date": reading.get("date"),
                "value": reading.get("value"),
            }
        )

    return rows


def normalise_warnings(
    warnings: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows = []

    for warning in warnings:
        area = warning.get("floodArea")

        if not isinstance(area, dict):
            area = {}

        rows.append(
            {
                "warning_id": warning.get("@id"),
                "flood_area_id": warning.get("floodAreaID"),
                "description": warning.get("description"),
                "county": area.get("county"),
                "river_or_sea": area.get("riverOrSea"),
                "severity": warning.get("severity"),
                "severity_level": warning.get("severityLevel"),
                "is_tidal": warning.get("isTidal"),
                "time_raised": warning.get("timeRaised"),
                "time_message_changed":
                    warning.get("timeMessageChanged"),
                "time_severity_changed":
                    warning.get("timeSeverityChanged"),
                "message": warning.get("message"),
            }
        )

    return rows
