from __future__ import annotations

import logging
import os
from pathlib import Path

import pandas as pd
import pymssql
from dotenv import load_dotenv

from flood_monitoring.dashboard.live import (
    get_live_current_river_stations,
    get_live_river_history,
    load_live_dashboard_snapshot,
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
load_dotenv(PROJECT_ROOT / ".env")

LOGGER = logging.getLogger(__name__)


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
            "Dashboard database configuration is incomplete."
        )

    server = (
        os.environ["SQL_SERVER"]
        .removeprefix("tcp:")
        .split(",")[0]
    )

    try:
        return pymssql.connect(
            server=server,
            user=os.environ["SQL_USER"],
            password=os.environ["SQL_PASSWORD"],
            database=os.environ["SQL_DATABASE"],
            login_timeout=5,
            timeout=10,
        )
    except pymssql.Error as exc:
        raise RuntimeError(
            "Dashboard SQL source is unavailable."
        ) from exc

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


def _load_sql_dashboard_snapshot() -> dict[str, pd.DataFrame]:
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


def load_dashboard_snapshot() -> dict:
    try:
        snapshot = _load_sql_dashboard_snapshot()
        snapshot["_source"] = "azure_sql"
        return snapshot

    except Exception as sql_error:
        LOGGER.warning(
            "SQL dashboard source unavailable. "
            "Using Environment Agency live API. Reason: %s",
            sql_error,
        )

    try:
        return load_live_dashboard_snapshot()

    except Exception as api_error:
        LOGGER.exception(
            "Environment Agency live fallback failed."
        )
        raise RuntimeError(
            "Live data is temporarily unavailable."
        ) from api_error


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

    try:
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

    except Exception as sql_error:
        LOGGER.warning(
            "SQL river history unavailable. "
            "Using Environment Agency live API. Reason: %s",
            sql_error,
        )

        return get_live_river_history(
            river_name,
            limit=safe_limit,
        )

def get_current_river_stations(
    river_name: str,
) -> pd.DataFrame:
    try:
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

    except Exception as sql_error:
        LOGGER.warning(
            "SQL current river stations unavailable. "
            "Using Environment Agency live API. Reason: %s",
            sql_error,
        )

        return get_live_current_river_stations(
            river_name
        )
