from __future__ import annotations

import csv
import json
import os
import re
import time
from datetime import date, datetime
from pathlib import Path

import pymssql


ROOT = Path(__file__).resolve().parents[3]
STAGING = ROOT / "data" / "staging" / "latest"


def _clean(value):
    if value is None:
        return None

    value = str(value).strip()

    return value or None


def _number(value):
    value = _clean(value)
    return None if value is None else float(value)


def _integer(value):
    value = _clean(value)
    return None if value is None else int(value)


def _boolean(value):
    value = _clean(value)

    if value is None:
        return None

    return value.lower() in {"true", "1", "yes"}


def _date(value):
    value = _clean(value)

    if value is None:
        return None

    return date.fromisoformat(value[:10])


def _datetime(value):
    value = _clean(value)

    if value is None:
        return None

    parsed = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if parsed.tzinfo is not None:
        parsed = parsed.astimezone().replace(
            tzinfo=None
        )

    return parsed


def _connection():
    required = (
        "SQL_SERVER",
        "SQL_DATABASE",
        "SQL_USER",
        "SQL_PASSWORD",
    )

    missing = [
        name
        for name in required
        if not os.getenv(name)
    ]

    if missing:
        raise RuntimeError(
            "Missing SQL environment variables: "
            + ", ".join(missing)
        )

    last_error = None

    for attempt in range(1, 13):
        try:
            return pymssql.connect(
                server=os.environ["SQL_SERVER"],
                user=os.environ["SQL_USER"],
                password=os.environ["SQL_PASSWORD"],
                database=os.environ["SQL_DATABASE"],
                login_timeout=30,
            )
        except pymssql.Error as exc:
            last_error = exc

            if attempt == 12:
                break

            print(
                "Azure SQL not ready, "
                f"retrying in 10 seconds ({attempt}/12)..."
            )

            time.sleep(10)

    raise RuntimeError(
        "Unable to connect to Azure SQL after retries."
    ) from last_error


def deploy_sql(cursor) -> None:
    files = [
        "sql/ddl/01_create_schemas.sql",
        "sql/ddl/02_create_core_tables.sql",
        "sql/staging/01_create_staging_tables.sql",
        "sql/procedures/01_load_station_dimension.sql",
        "sql/procedures/02_load_river_readings.sql",
        "sql/procedures/03_load_flood_warnings.sql",
        "sql/procedures/04_log_etl_execution.sql",
        "sql/procedures/05_build_monitoring_summary.sql",
        "sql/views/01_reporting_views.sql",
    ]

    for relative in files:
        text = (ROOT / relative).read_text(
            encoding="utf-8"
        )

        batches = re.split(
            r"(?im)^\s*GO\s*;?\s*$",
            text,
        )

        for batch in batches:
            if batch.strip():
                cursor.execute(batch)


def load_staging(cursor) -> dict[str, int]:
    cursor.execute("TRUNCATE TABLE stg.RiverReading")
    cursor.execute("TRUNCATE TABLE stg.FloodWarning")
    cursor.execute("TRUNCATE TABLE stg.Station")

    with (STAGING / "stations.csv").open(
        newline="",
        encoding="utf-8",
    ) as handle:
        stations = list(csv.DictReader(handle))

    for row in stations:
        cursor.execute(
            """
            INSERT INTO stg.Station
            (
                StationReference,
                StationName,
                RiverName,
                Town,
                CatchmentName,
                Latitude,
                Longitude,
                StationStatus,
                DateOpened,
                TypicalRangeLow,
                TypicalRangeHigh
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                _clean(row["station_reference"]),
                _clean(row["station_name"]),
                _clean(row["river_name"]),
                _clean(row["town"]),
                _clean(row["catchment_name"]),
                _number(row["latitude"]),
                _number(row["longitude"]),
                _clean(row["status"]),
                _date(row["date_opened"]),
                _number(row["typical_range_low"]),
                _number(row["typical_range_high"]),
            ),
        )

    with (STAGING / "latest_readings.csv").open(
        newline="",
        encoding="utf-8",
    ) as handle:
        readings = list(csv.DictReader(handle))

    for row in readings:
        cursor.execute(
            """
            INSERT INTO stg.RiverReading
            (
                StationReference,
                MeasureId,
                MeasureURL,
                Parameter,
                Qualifier,
                UnitName,
                ReadingDateTimeUTC,
                ReadingDate,
                ReadingValue
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                _clean(row["station_reference"]),
                _clean(row["measure_id"]),
                _clean(row["measure_url"]),
                _clean(row["parameter"]),
                _clean(row["qualifier"]),
                _clean(row["unit_name"]),
                _datetime(row["reading_datetime"]),
                _date(row["reading_date"]),
                _number(row["value"]),
            ),
        )

    with (STAGING / "flood_warnings.csv").open(
        newline="",
        encoding="utf-8",
    ) as handle:
        warnings = list(csv.DictReader(handle))

    for row in warnings:
        cursor.execute(
            """
            INSERT INTO stg.FloodWarning
            (
                WarningId,
                FloodAreaId,
                FloodAreaDescription,
                County,
                RiverOrSea,
                Severity,
                SeverityLevel,
                IsTidal,
                TimeRaisedUTC,
                TimeMessageChangedUTC,
                TimeSeverityChangedUTC,
                WarningMessage
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                _clean(row["warning_id"]),
                _clean(row["flood_area_id"]),
                _clean(row["description"]),
                _clean(row["county"]),
                _clean(row["river_or_sea"]),
                _clean(row["severity"]),
                _integer(row["severity_level"]),
                _boolean(row["is_tidal"]),
                _datetime(row["time_raised"]),
                _datetime(row["time_message_changed"]),
                _datetime(row["time_severity_changed"]),
                _clean(row["message"]),
            ),
        )

    return {
        "stations": len(stations),
        "readings": len(readings),
        "warnings": len(warnings),
    }


def run_warehouse_load(cursor) -> None:
    cursor.execute(
        "EXEC dbo.usp_LoadStationDimension"
    )

    cursor.execute(
        "EXEC dbo.usp_LoadRiverReadings"
    )

    cursor.execute(
        "EXEC dbo.usp_LoadFloodWarnings"
    )


def load_audit(cursor) -> None:
    summary = json.loads(
        (
            STAGING / "etl_run_summary.json"
        ).read_text(encoding="utf-8")
    )

    source = summary["source_counts"]
    staged = summary["staged_counts"]

    rows_extracted = (
        source["stations"]
        + source["national_latest_readings"]
        + source["current_flood_warnings"]
    )

    rows_loaded = (
        staged["stations"]
        + staged["local_latest_readings"]
        + staged["flood_warnings"]
    )

    cursor.execute(
        """
        EXEC audit.usp_LogETLExecution
            @RunId=%s,
            @PipelineName=%s,
            @StartTimeUTC=%s,
            @EndTimeUTC=%s,
            @RowsExtracted=%s,
            @RowsLoaded=%s,
            @RowsRejected=%s,
            @StationRows=%s,
            @ReadingRows=%s,
            @WarningRows=%s,
            @Status=%s,
            @DurationSeconds=%s,
            @ErrorMessage=%s
        """,
        (
            summary["run_id"],
            "Environment Agency Flood Monitoring ETL",
            _datetime(summary["started_at_utc"]),
            _datetime(summary["finished_at_utc"]),
            rows_extracted,
            rows_loaded,
            0,
            staged["stations"],
            staged["local_latest_readings"],
            staged["flood_warnings"],
            summary["status"],
            summary["duration_seconds"],
            None,
        ),
    )


def main() -> None:
    conn = _connection()
    conn.autocommit(True)

    cursor = conn.cursor()

    print("Deploying SQL objects...")
    deploy_sql(cursor)

    print("Loading staging tables...")
    counts = load_staging(cursor)

    print("Executing warehouse procedures...")
    run_warehouse_load(cursor)

    print("Recording ETL audit...")
    load_audit(cursor)

    print()
    print("AZURE SQL LOAD COMPLETED")

    for name, value in counts.items():
        print(f"{name}: {value}")

    cursor.execute(
        "SELECT COUNT(*) FROM dbo.DimStation"
    )
    print("DimStation:", cursor.fetchone()[0])

    cursor.execute(
        "SELECT COUNT(*) FROM dbo.FactRiverReading"
    )
    print("FactRiverReading:", cursor.fetchone()[0])

    conn.close()


if __name__ == "__main__":
    main()
