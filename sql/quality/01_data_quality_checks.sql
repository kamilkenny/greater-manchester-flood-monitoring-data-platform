SELECT
    StationReference,
    COUNT(*) AS DuplicateCount
FROM dbo.DimStation
GROUP BY StationReference
HAVING COUNT(*) > 1;
GO


SELECT
    StationKey,
    MeasureId,
    ReadingDateTimeUTC,
    COUNT(*) AS DuplicateCount
FROM dbo.FactRiverReading
GROUP BY
    StationKey,
    MeasureId,
    ReadingDateTimeUTC
HAVING COUNT(*) > 1;
GO


SELECT
    COUNT(*) AS OrphanReadingCount
FROM dbo.FactRiverReading reading
LEFT JOIN dbo.DimStation station
    ON station.StationKey =
       reading.StationKey
WHERE station.StationKey IS NULL;
GO


SELECT
    COUNT(*) AS TotalStations,

    SUM(
        CASE
            WHEN RiverName IS NULL
            THEN 1
            ELSE 0
        END
    ) AS MissingRiverName,

    SUM(
        CASE
            WHEN Town IS NULL
            THEN 1
            ELSE 0
        END
    ) AS MissingTown,

    SUM(
        CASE
            WHEN Latitude IS NULL
              OR Longitude IS NULL
            THEN 1
            ELSE 0
        END
    ) AS MissingCoordinates

FROM dbo.DimStation;
GO
