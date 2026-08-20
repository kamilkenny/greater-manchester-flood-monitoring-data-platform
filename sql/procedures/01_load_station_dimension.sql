CREATE OR ALTER PROCEDURE dbo.usp_LoadStationDimension
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    UPDATE target
    SET
        StationName = source.StationName,
        RiverName = source.RiverName,
        Town = source.Town,
        CatchmentName = source.CatchmentName,
        Latitude = source.Latitude,
        Longitude = source.Longitude,
        StationStatus = source.StationStatus,
        DateOpened = source.DateOpened,
        TypicalRangeLow = source.TypicalRangeLow,
        TypicalRangeHigh = source.TypicalRangeHigh,
        UpdatedAtUTC = SYSUTCDATETIME()
    FROM dbo.DimStation target
    INNER JOIN stg.Station source
        ON target.StationReference = source.StationReference;

    INSERT INTO dbo.DimStation
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
    SELECT DISTINCT
        source.StationReference,
        source.StationName,
        source.RiverName,
        source.Town,
        source.CatchmentName,
        source.Latitude,
        source.Longitude,
        source.StationStatus,
        source.DateOpened,
        source.TypicalRangeLow,
        source.TypicalRangeHigh
    FROM stg.Station source
    WHERE source.StationReference IS NOT NULL
      AND NOT EXISTS
      (
          SELECT 1
          FROM dbo.DimStation target
          WHERE target.StationReference =
              source.StationReference
      );
END;
GO
