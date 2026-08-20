CREATE OR ALTER PROCEDURE dbo.usp_LoadFloodWarnings
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE target
    SET
        FloodAreaId = source.FloodAreaId,
        FloodAreaDescription =
            source.FloodAreaDescription,
        County = source.County,
        RiverOrSea = source.RiverOrSea,
        Severity = source.Severity,
        SeverityLevel = source.SeverityLevel,
        IsTidal = source.IsTidal,
        TimeRaisedUTC = source.TimeRaisedUTC,
        TimeMessageChangedUTC =
            source.TimeMessageChangedUTC,
        TimeSeverityChangedUTC =
            source.TimeSeverityChangedUTC,
        WarningMessage = source.WarningMessage,
        LoadDateTimeUTC = SYSUTCDATETIME()
    FROM dbo.FactFloodWarning target
    INNER JOIN stg.FloodWarning source
        ON target.WarningId = source.WarningId;

    INSERT INTO dbo.FactFloodWarning
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
    SELECT
        source.WarningId,
        source.FloodAreaId,
        source.FloodAreaDescription,
        source.County,
        source.RiverOrSea,
        source.Severity,
        source.SeverityLevel,
        source.IsTidal,
        source.TimeRaisedUTC,
        source.TimeMessageChangedUTC,
        source.TimeSeverityChangedUTC,
        source.WarningMessage
    FROM stg.FloodWarning source
    WHERE source.WarningId IS NOT NULL
      AND NOT EXISTS
      (
          SELECT 1
          FROM dbo.FactFloodWarning target
          WHERE target.WarningId =
                source.WarningId
      );
END;
GO
