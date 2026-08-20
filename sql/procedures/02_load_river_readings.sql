CREATE OR ALTER PROCEDURE dbo.usp_LoadRiverReadings
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    INSERT INTO dbo.FactRiverReading
    (
        StationKey,
        MeasureId,
        MeasureURL,
        Parameter,
        Qualifier,
        UnitName,
        ReadingDateTimeUTC,
        ReadingDate,
        ReadingValue
    )
    SELECT
        station.StationKey,
        source.MeasureId,
        source.MeasureURL,
        source.Parameter,
        source.Qualifier,
        source.UnitName,
        source.ReadingDateTimeUTC,
        source.ReadingDate,
        source.ReadingValue
    FROM stg.RiverReading source
    INNER JOIN dbo.DimStation station
        ON station.StationReference =
           source.StationReference
    WHERE source.MeasureId IS NOT NULL
      AND source.ReadingDateTimeUTC IS NOT NULL
      AND NOT EXISTS
      (
          SELECT 1
          FROM dbo.FactRiverReading target
          WHERE target.StationKey =
                station.StationKey
            AND target.MeasureId =
                source.MeasureId
            AND target.ReadingDateTimeUTC =
                source.ReadingDateTimeUTC
      );
END;
GO
