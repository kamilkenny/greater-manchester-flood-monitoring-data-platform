CREATE OR ALTER VIEW dbo.vw_CurrentStationStatus
AS
WITH RankedReadings AS
(
    SELECT
        s.StationKey,
        s.StationReference,
        s.StationName,
        s.RiverName,
        s.Town,
        s.Latitude,
        s.Longitude,
        s.TypicalRangeLow,
        s.TypicalRangeHigh,

        r.MeasureId,
        r.Parameter,
        r.Qualifier,
        r.UnitName,
        r.ReadingDateTimeUTC,
        r.ReadingValue,

        LAG(r.ReadingValue) OVER
        (
            PARTITION BY s.StationKey, r.MeasureId
            ORDER BY r.ReadingDateTimeUTC
        ) AS PreviousValue,

        ROW_NUMBER() OVER
        (
            PARTITION BY s.StationKey, r.MeasureId
            ORDER BY r.ReadingDateTimeUTC DESC
        ) AS RowNumber
    FROM dbo.DimStation s
    INNER JOIN dbo.FactRiverReading r
        ON r.StationKey = s.StationKey
)
SELECT
    StationKey,
    StationReference,
    StationName,
    RiverName,
    Town,
    Latitude,
    Longitude,
    MeasureId,
    Parameter,
    Qualifier,
    UnitName,
    ReadingDateTimeUTC,
    ReadingValue AS CurrentValue,
    PreviousValue,
    ReadingValue - PreviousValue AS AbsoluteChange,
    TypicalRangeLow,
    TypicalRangeHigh,

    CASE
        WHEN TypicalRangeHigh IS NOT NULL
         AND ReadingValue > TypicalRangeHigh
            THEN 'ABOVE TYPICAL RANGE'

        WHEN TypicalRangeHigh IS NOT NULL
         AND ReadingValue >= TypicalRangeHigh * 0.90
            THEN 'ELEVATED'

        ELSE 'NORMAL'
    END AS CurrentStatus
FROM RankedReadings
WHERE RowNumber = 1;
GO


CREATE OR ALTER VIEW dbo.vw_HighRiverLevelStations
AS
SELECT *
FROM dbo.vw_CurrentStationStatus
WHERE CurrentStatus IN
(
    'ELEVATED',
    'ABOVE TYPICAL RANGE'
);
GO


CREATE OR ALTER VIEW dbo.vw_FloodWarningSummary
AS
SELECT
    Severity,
    SeverityLevel,
    COUNT(*) AS WarningCount,
    MAX(TimeMessageChangedUTC)
        AS LatestUpdateUTC
FROM dbo.FactFloodWarning
GROUP BY
    Severity,
    SeverityLevel;
GO


CREATE OR ALTER VIEW dbo.vw_ETLPerformance
AS
SELECT
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
FROM audit.ETLRunLog;
GO
