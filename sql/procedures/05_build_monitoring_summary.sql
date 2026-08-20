CREATE OR ALTER PROCEDURE dbo.usp_BuildFloodMonitoringSummary
AS
BEGIN
    SET NOCOUNT ON;

    SELECT
        COUNT(DISTINCT StationKey) AS StationCount,
        COUNT(*) AS ReadingCount,
        MAX(ReadingDateTimeUTC) AS LatestReadingUTC
    FROM dbo.FactRiverReading;

    SELECT
        COUNT(*) AS ActiveWarningCount,
        MAX(TimeMessageChangedUTC)
            AS LatestWarningUpdateUTC
    FROM dbo.FactFloodWarning;
END;
GO
