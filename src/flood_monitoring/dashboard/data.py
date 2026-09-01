from __future__ import annotations

import os
import time
from pathlib import Path

import pandas as pd
import pymssql
from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")


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
            "Dashboard database configuration is incomplete: "
            + ", ".join(missing)
        )

    server = (
        os.environ["SQL_SERVER"]
        .removeprefix("tcp:")
        .split(",")[0]
    )

    last_error = None

    for attempt in range(1, 19):
        try:
            return pymssql.connect(
                server=server,
                user=os.environ["SQL_USER"],
                password=os.environ["SQL_PASSWORD"],
                database=os.environ["SQL_DATABASE"],
                login_timeout=30,
                timeout=30,
            )

        except pymssql.Error as exc:
            last_error = exc
            message = str(exc)

            if "18456" in message:
                raise RuntimeError(
                    "Azure SQL authentication failed."
                ) from exc

            if attempt == 18:
                break

            time.sleep(10)

    raise RuntimeError(
        "Unable to connect to Azure SQL after retries."
    ) from last_error


def query(
    sql: str,
    params=None,
) -> pd.DataFrame:
    connection = _connection()

    try:
        return pd.read_sql_query(
            sql,
            connection,
            params=params,
        )

    finally:
        connection.close()


def load_dashboard_snapshot() -> dict[str, pd.DataFrame]:
    current = query(
        """
        SELECT
            StationKey,
            StationReference,
            StationName,
            RiverName,
            Town,
            Latitude,
            Longitude,
            Parameter,
            Qualifier,
            UnitName,
            ReadingDateTimeUTC,
            CurrentValue,
            PreviousValue,
            AbsoluteChange,
            TypicalRangeLow,
            TypicalRangeHigh,
            CurrentStatus
        FROM dbo.vw_CurrentStationStatus
        """
    )

    high_levels = query(
        """
        SELECT
            StationKey,
            StationName,
            RiverName,
            Town,
            ReadingDateTimeUTC,
            CurrentValue,
            TypicalRangeHigh,
            CurrentStatus
        FROM dbo.vw_HighRiverLevelStations
        WHERE LOWER(Parameter) = 'level'
        ORDER BY
            CurrentStatus DESC,
            CurrentValue DESC
        """
    )

    rainfall = query(
        """
        SELECT
            StationKey,
            StationName,
            RiverName,
            Town,
            ReadingDateTimeUTC,
            CurrentValue,
            UnitName
        FROM dbo.vw_CurrentRainfall
        ORDER BY CurrentValue DESC
        """
    )

    warnings = query(
        """
        SELECT
            Severity,
            SeverityLevel,
            WarningCount,
            LatestUpdateUTC
        FROM dbo.vw_FloodWarningSummary
        ORDER BY SeverityLevel
        """
    )

    etl = query(
        """
        SELECT TOP 20
            RunId,
            PipelineName,
            StartTimeUTC,
            EndTimeUTC,
            RowsExtracted,
            RowsLoaded,
            RowsRejected,
            StationRows,
            ReadingRows,
            WarningRows,
            Status,
            DurationSeconds,
            ErrorMessage
        FROM dbo.vw_ETLPerformance
        ORDER BY StartTimeUTC DESC
        """
    )

    return {
        "current": current,
        "high_levels": high_levels,
        "rainfall": rainfall,
        "warnings": warnings,
        "etl": etl,
    }


def get_river_names() -> list[str]:
    frame = query(
        """
        SELECT DISTINCT RiverName
        FROM dbo.vw_CurrentRiverLevels
        WHERE RiverName IS NOT NULL
          AND LTRIM(RTRIM(RiverName)) <> ''
        ORDER BY RiverName
        """
    )

    return (
        frame["RiverName"]
        .dropna()
        .astype(str)
        .tolist()
    )


def get_river_history(
    river_name: str,
    limit: int = 2500,
) -> pd.DataFrame:
    safe_limit = max(
        100,
        min(int(limit), 5000),
    )

    return query(
        f"""
        SELECT TOP {safe_limit}
            s.StationName,
            s.RiverName,
            s.Town,
            r.MeasureId,
            r.Qualifier,
            r.UnitName,
            r.ReadingDateTimeUTC,
            r.ReadingValue,
            s.TypicalRangeLow,
            s.TypicalRangeHigh
        FROM dbo.FactRiverReading r
        INNER JOIN dbo.DimStation s
            ON s.StationKey = r.StationKey
        WHERE LOWER(r.Parameter) = 'level'
          AND s.RiverName = %s
        ORDER BY r.ReadingDateTimeUTC DESC
        """,
        params=(river_name,),
    )


def get_current_river_stations(
    river_name: str,
) -> pd.DataFrame:
    return query(
        """
        SELECT
            StationName,
            RiverName,
            Town,
            ReadingDateTimeUTC,
            CurrentValue,
            PreviousValue,
            AbsoluteChange,
            UnitName,
            TypicalRangeLow,
            TypicalRangeHigh,
            CurrentStatus
        FROM dbo.vw_CurrentRiverLevels
        WHERE RiverName = %s
        ORDER BY
            CASE CurrentStatus
                WHEN 'ABOVE TYPICAL RANGE' THEN 1
                WHEN 'ELEVATED' THEN 2
                ELSE 3
            END,
            StationName
        """,
        params=(river_name,),
    )
