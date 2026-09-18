from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd

from flood_monitoring.config import load_settings
from flood_monitoring.ingestion.environment_agency import (
    EnvironmentAgencyClient,
)
from flood_monitoring.ingestion.transforms import (
    normalise_measures,
    normalise_readings,
    normalise_stations,
    normalise_warnings,
)


CURRENT_COLUMNS = [
    "StationKey",
    "StationReference",
    "StationName",
    "RiverName",
    "Town",
    "Latitude",
    "Longitude",
    "Parameter",
    "Qualifier",
    "UnitName",
    "ReadingDateTimeUTC",
    "CurrentValue",
    "PreviousValue",
    "AbsoluteChange",
    "TypicalRangeLow",
    "TypicalRangeHigh",
    "CurrentStatus",
]

HIGH_LEVEL_COLUMNS = [
    "StationKey",
    "StationName",
    "RiverName",
    "Town",
    "ReadingDateTimeUTC",
    "CurrentValue",
    "TypicalRangeHigh",
    "CurrentStatus",
]

RAINFALL_COLUMNS = [
    "StationKey",
    "StationName",
    "RiverName",
    "Town",
    "ReadingDateTimeUTC",
    "CurrentValue",
    "UnitName",
]

WARNING_COLUMNS = [
    "Severity",
    "SeverityLevel",
    "WarningCount",
    "LatestUpdateUTC",
]

ETL_COLUMNS = [
    "RunId",
    "PipelineName",
    "StartTimeUTC",
    "EndTimeUTC",
    "RowsExtracted",
    "RowsLoaded",
    "RowsRejected",
    "StationRows",
    "ReadingRows",
    "WarningRows",
    "Status",
    "DurationSeconds",
    "ErrorMessage",
]


def _items(payload: dict) -> list[dict]:
    items = payload.get("items", [])

    if isinstance(items, list):
        return items

    return []


def _client() -> EnvironmentAgencyClient:
    return EnvironmentAgencyClient(load_settings())


def _status(row: pd.Series) -> str:
    if str(row.get("Parameter", "")).lower() != "level":
        return "CURRENT"

    value = pd.to_numeric(
        pd.Series([row.get("CurrentValue")]),
        errors="coerce",
    ).iloc[0]

    low = pd.to_numeric(
        pd.Series([row.get("TypicalRangeLow")]),
        errors="coerce",
    ).iloc[0]

    high = pd.to_numeric(
        pd.Series([row.get("TypicalRangeHigh")]),
        errors="coerce",
    ).iloc[0]

    if pd.notna(value) and pd.notna(high) and value > high:
        return "ABOVE TYPICAL RANGE"

    if pd.notna(value) and pd.notna(low) and value < low:
        return "BELOW TYPICAL RANGE"

    if pd.notna(value) and (
        pd.notna(low) or pd.notna(high)
    ):
        return "WITHIN TYPICAL RANGE"

    return "CURRENT"


def _load_current(
    client: EnvironmentAgencyClient,
) -> pd.DataFrame:
    station_items = _items(client.fetch_stations())

    station_rows = normalise_stations(station_items)
    measure_rows = normalise_measures(station_items)

    reading_items = _items(
        client.fetch_latest_readings()
    )

    reading_rows = normalise_readings(
        reading_items,
        measure_rows,
    )

    stations = pd.DataFrame(station_rows)
    readings = pd.DataFrame(reading_rows)

    if stations.empty or readings.empty:
        return pd.DataFrame(columns=CURRENT_COLUMNS)

    merged = readings.merge(
        stations,
        on="station_reference",
        how="inner",
    )

    current = pd.DataFrame(
        {
            "StationKey":
                merged["station_reference"],
            "StationReference":
                merged["station_reference"],
            "StationName":
                merged["station_name"],
            "RiverName":
                merged["river_name"],
            "Town":
                merged["town"],
            "Latitude":
                merged["latitude"],
            "Longitude":
                merged["longitude"],
            "Parameter":
                merged["parameter"],
            "Qualifier":
                merged["qualifier"],
            "UnitName":
                merged["unit_name"],
            "ReadingDateTimeUTC":
                merged["reading_datetime"],
            "CurrentValue":
                merged["value"],
            "PreviousValue":
                pd.NA,
            "AbsoluteChange":
                pd.NA,
            "TypicalRangeLow":
                merged["typical_range_low"],
            "TypicalRangeHigh":
                merged["typical_range_high"],
        }
    )

    current["CurrentValue"] = pd.to_numeric(
        current["CurrentValue"],
        errors="coerce",
    )

    current["TypicalRangeLow"] = pd.to_numeric(
        current["TypicalRangeLow"],
        errors="coerce",
    )

    current["TypicalRangeHigh"] = pd.to_numeric(
        current["TypicalRangeHigh"],
        errors="coerce",
    )

    current["CurrentStatus"] = current.apply(
        _status,
        axis=1,
    )

    return current[CURRENT_COLUMNS]


def _load_warnings(
    client: EnvironmentAgencyClient,
) -> pd.DataFrame:
    warning_items = _items(
        client.fetch_flood_warnings()
    )

    warnings = pd.DataFrame(
        normalise_warnings(warning_items)
    )

    if warnings.empty:
        return pd.DataFrame(columns=WARNING_COLUMNS)

    warnings["severity_level"] = pd.to_numeric(
        warnings["severity_level"],
        errors="coerce",
    )

    # Severity level 4 means the warning is no longer in force.
    warnings = warnings[
        warnings["severity_level"].between(1, 3)
    ].copy()

    if warnings.empty:
        return pd.DataFrame(columns=WARNING_COLUMNS)

    time_columns = [
        "time_message_changed",
        "time_severity_changed",
        "time_raised",
    ]

    for column in time_columns:
        warnings[column] = pd.to_datetime(
            warnings[column],
            errors="coerce",
            utc=True,
        )

    warnings["LatestUpdateUTC"] = warnings[
        time_columns
    ].max(axis=1)

    summary = (
        warnings
        .groupby(
            ["severity", "severity_level"],
            dropna=False,
        )
        .agg(
            WarningCount=("warning_id", "count"),
            LatestUpdateUTC=(
                "LatestUpdateUTC",
                "max",
            ),
        )
        .reset_index()
        .rename(
            columns={
                "severity": "Severity",
                "severity_level": "SeverityLevel",
            }
        )
        .sort_values("SeverityLevel")
    )

    return summary[WARNING_COLUMNS]


def load_live_dashboard_snapshot() -> dict:
    client = _client()

    current = _load_current(client)

    level_mask = (
        current["Parameter"]
        .fillna("")
        .astype(str)
        .str.lower()
        .eq("level")
    )

    high_levels = current[
        level_mask
        & current["CurrentStatus"].eq(
            "ABOVE TYPICAL RANGE"
        )
    ][HIGH_LEVEL_COLUMNS].copy()

    rainfall = current[
        current["Parameter"]
        .fillna("")
        .astype(str)
        .str.lower()
        .eq("rainfall")
    ][RAINFALL_COLUMNS].copy()

    warnings = _load_warnings(client)

    return {
        "current": current,
        "high_levels": high_levels,
        "rainfall": rainfall,
        "warnings": warnings,
        "etl": pd.DataFrame(columns=ETL_COLUMNS),
        "_source": "environment_agency",
    }


def get_live_river_names() -> list[str]:
    current = _load_current(_client())

    if current.empty:
        return []

    level = current[
        current["Parameter"]
        .fillna("")
        .astype(str)
        .str.lower()
        .eq("level")
    ]

    return sorted(
        level["RiverName"]
        .dropna()
        .astype(str)
        .str.strip()
        .loc[lambda values: values.ne("")]
        .unique()
        .tolist()
    )


def get_live_current_river_stations(
    river_name: str,
) -> pd.DataFrame:
    current = _load_current(_client())

    if current.empty:
        return pd.DataFrame(
            columns=[
                "StationName",
                "RiverName",
                "Town",
                "ReadingDateTimeUTC",
                "CurrentValue",
                "PreviousValue",
                "AbsoluteChange",
                "UnitName",
                "TypicalRangeLow",
                "TypicalRangeHigh",
                "CurrentStatus",
            ]
        )

    mask = (
        current["RiverName"]
        .fillna("")
        .astype(str)
        .eq(river_name)
        & current["Parameter"]
        .fillna("")
        .astype(str)
        .str.lower()
        .eq("level")
    )

    columns = [
        "StationName",
        "RiverName",
        "Town",
        "ReadingDateTimeUTC",
        "CurrentValue",
        "PreviousValue",
        "AbsoluteChange",
        "UnitName",
        "TypicalRangeLow",
        "TypicalRangeHigh",
        "CurrentStatus",
    ]

    return current.loc[mask, columns].copy()


def get_live_river_history(
    river_name: str,
    limit: int = 2500,
) -> pd.DataFrame:
    client = _client()

    station_items = _items(client.fetch_stations())
    station_rows = normalise_stations(station_items)
    measure_rows = normalise_measures(station_items)

    stations = pd.DataFrame(station_rows)

    columns = [
        "StationName",
        "RiverName",
        "Town",
        "MeasureId",
        "Qualifier",
        "UnitName",
        "ReadingDateTimeUTC",
        "ReadingValue",
        "TypicalRangeLow",
        "TypicalRangeHigh",
    ]

    if stations.empty:
        return pd.DataFrame(columns=columns)

    selected = stations[
        stations["river_name"]
        .fillna("")
        .astype(str)
        .eq(river_name)
    ]

    references = (
        selected["station_reference"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    if not references:
        return pd.DataFrame(columns=columns)

    now = datetime.now(timezone.utc)
    start = now - timedelta(days=2)

    reading_items: list[dict] = []

    for reference in references[:20]:
        try:
            payload = client.fetch_station_readings(
                reference,
                start.date().isoformat(),
                now.date().isoformat(),
                limit=500,
            )
            reading_items.extend(_items(payload))
        except Exception:
            continue

    reading_rows = normalise_readings(
        reading_items,
        measure_rows,
    )

    readings = pd.DataFrame(reading_rows)

    if readings.empty:
        return pd.DataFrame(columns=columns)

    readings = readings[
        readings["parameter"]
        .fillna("")
        .astype(str)
        .str.lower()
        .eq("level")
    ]

    merged = readings.merge(
        stations,
        on="station_reference",
        how="inner",
    )

    merged = merged[
        merged["river_name"]
        .fillna("")
        .astype(str)
        .eq(river_name)
    ].copy()

    history = pd.DataFrame(
        {
            "StationName":
                merged["station_name"],
            "RiverName":
                merged["river_name"],
            "Town":
                merged["town"],
            "MeasureId":
                merged["measure_id"],
            "Qualifier":
                merged["qualifier"],
            "UnitName":
                merged["unit_name"],
            "ReadingDateTimeUTC":
                merged["reading_datetime"],
            "ReadingValue":
                pd.to_numeric(
                    merged["value"],
                    errors="coerce",
                ),
            "TypicalRangeLow":
                pd.to_numeric(
                    merged["typical_range_low"],
                    errors="coerce",
                ),
            "TypicalRangeHigh":
                pd.to_numeric(
                    merged["typical_range_high"],
                    errors="coerce",
                ),
        }
    )

    history["ReadingDateTimeUTC"] = pd.to_datetime(
        history["ReadingDateTimeUTC"],
        errors="coerce",
        utc=True,
    )

    history = (
        history
        .dropna(subset=["ReadingDateTimeUTC"])
        .sort_values(
            "ReadingDateTimeUTC",
            ascending=False,
        )
        .head(max(100, min(int(limit), 5000)))
    )

    return history[columns]
