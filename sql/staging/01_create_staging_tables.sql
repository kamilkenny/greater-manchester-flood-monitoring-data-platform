IF OBJECT_ID('stg.Station', 'U') IS NULL
BEGIN
    CREATE TABLE stg.Station
    (
        StationReference NVARCHAR(50) NULL,
        StationName NVARCHAR(255) NULL,
        RiverName NVARCHAR(255) NULL,
        Town NVARCHAR(255) NULL,
        CatchmentName NVARCHAR(255) NULL,
        Latitude DECIMAL(9,6) NULL,
        Longitude DECIMAL(9,6) NULL,
        StationStatus NVARCHAR(100) NULL,
        DateOpened DATE NULL,
        TypicalRangeLow DECIMAL(18,6) NULL,
        TypicalRangeHigh DECIMAL(18,6) NULL
    );
END;
GO


IF OBJECT_ID('stg.RiverReading', 'U') IS NULL
BEGIN
    CREATE TABLE stg.RiverReading
    (
        StationReference NVARCHAR(50) NULL,
        MeasureId NVARCHAR(255) NULL,
        MeasureURL NVARCHAR(1000) NULL,
        Parameter NVARCHAR(100) NULL,
        Qualifier NVARCHAR(255) NULL,
        UnitName NVARCHAR(100) NULL,
        ReadingDateTimeUTC DATETIME2(0) NULL,
        ReadingDate DATE NULL,
        ReadingValue DECIMAL(18,6) NULL
    );
END;
GO


IF OBJECT_ID('stg.FloodWarning', 'U') IS NULL
BEGIN
    CREATE TABLE stg.FloodWarning
    (
        WarningId NVARCHAR(1000) NULL,
        FloodAreaId NVARCHAR(255) NULL,
        FloodAreaDescription NVARCHAR(1000) NULL,
        County NVARCHAR(500) NULL,
        RiverOrSea NVARCHAR(500) NULL,
        Severity NVARCHAR(100) NULL,
        SeverityLevel INT NULL,
        IsTidal BIT NULL,
        TimeRaisedUTC DATETIME2(0) NULL,
        TimeMessageChangedUTC DATETIME2(0) NULL,
        TimeSeverityChangedUTC DATETIME2(0) NULL,
        WarningMessage NVARCHAR(MAX) NULL
    );
END;
GO
