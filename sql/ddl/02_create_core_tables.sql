IF OBJECT_ID('dbo.DimStation', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.DimStation
    (
        StationKey INT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_DimStation PRIMARY KEY,

        StationReference NVARCHAR(50) NOT NULL,
        StationName NVARCHAR(255) NULL,
        RiverName NVARCHAR(255) NULL,
        Town NVARCHAR(255) NULL,
        CatchmentName NVARCHAR(255) NULL,

        Latitude DECIMAL(9,6) NULL,
        Longitude DECIMAL(9,6) NULL,

        StationStatus NVARCHAR(100) NULL,
        DateOpened DATE NULL,

        TypicalRangeLow DECIMAL(18,6) NULL,
        TypicalRangeHigh DECIMAL(18,6) NULL,

        CreatedAtUTC DATETIME2(0) NOT NULL
            CONSTRAINT DF_DimStation_CreatedAtUTC
            DEFAULT SYSUTCDATETIME(),

        UpdatedAtUTC DATETIME2(0) NOT NULL
            CONSTRAINT DF_DimStation_UpdatedAtUTC
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT UQ_DimStation_StationReference
            UNIQUE (StationReference)
    );
END;
GO


IF OBJECT_ID('dbo.FactRiverReading', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.FactRiverReading
    (
        ReadingKey BIGINT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_FactRiverReading PRIMARY KEY,

        StationKey INT NOT NULL,

        MeasureId NVARCHAR(255) NOT NULL,
        MeasureURL NVARCHAR(1000) NULL,

        Parameter NVARCHAR(100) NULL,
        Qualifier NVARCHAR(255) NULL,
        UnitName NVARCHAR(100) NULL,

        ReadingDateTimeUTC DATETIME2(0) NOT NULL,
        ReadingDate DATE NULL,

        ReadingValue DECIMAL(18,6) NULL,

        LoadDateTimeUTC DATETIME2(0) NOT NULL
            CONSTRAINT DF_FactRiverReading_LoadDateTimeUTC
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT FK_FactRiverReading_DimStation
            FOREIGN KEY (StationKey)
            REFERENCES dbo.DimStation(StationKey)
    );
END;
GO


IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE name = 'UX_FactRiverReading_BusinessKey'
      AND object_id = OBJECT_ID('dbo.FactRiverReading')
)
BEGIN
    CREATE UNIQUE INDEX UX_FactRiverReading_BusinessKey
    ON dbo.FactRiverReading
    (
        StationKey,
        MeasureId,
        ReadingDateTimeUTC
    );
END;
GO


IF OBJECT_ID('dbo.FactFloodWarning', 'U') IS NULL
BEGIN
    CREATE TABLE dbo.FactFloodWarning
    (
        FloodWarningKey BIGINT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_FactFloodWarning PRIMARY KEY,

        WarningId NVARCHAR(1000) NOT NULL,
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

        WarningMessage NVARCHAR(MAX) NULL,

        LoadDateTimeUTC DATETIME2(0) NOT NULL
            CONSTRAINT DF_FactFloodWarning_LoadDateTimeUTC
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT UQ_FactFloodWarning_WarningId
            UNIQUE (WarningId)
    );
END;
GO


IF OBJECT_ID('audit.ETLRunLog', 'U') IS NULL
BEGIN
    CREATE TABLE audit.ETLRunLog
    (
        RunKey BIGINT IDENTITY(1,1) NOT NULL
            CONSTRAINT PK_ETLRunLog PRIMARY KEY,

        RunId NVARCHAR(100) NOT NULL,
        PipelineName NVARCHAR(255) NOT NULL,

        StartTimeUTC DATETIME2(3) NOT NULL,
        EndTimeUTC DATETIME2(3) NULL,

        RowsExtracted INT NULL,
        RowsLoaded INT NULL,
        RowsRejected INT NULL,

        StationRows INT NULL,
        ReadingRows INT NULL,
        WarningRows INT NULL,

        Status NVARCHAR(50) NOT NULL,
        DurationSeconds DECIMAL(18,3) NULL,

        ErrorMessage NVARCHAR(MAX) NULL,

        CreatedAtUTC DATETIME2(0) NOT NULL
            CONSTRAINT DF_ETLRunLog_CreatedAtUTC
            DEFAULT SYSUTCDATETIME(),

        CONSTRAINT UQ_ETLRunLog_RunId
            UNIQUE (RunId)
    );
END;
GO
