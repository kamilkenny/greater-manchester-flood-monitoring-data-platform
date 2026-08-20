CREATE OR ALTER PROCEDURE audit.usp_LogETLExecution
    @RunId NVARCHAR(100),
    @PipelineName NVARCHAR(255),
    @StartTimeUTC DATETIME2(3),
    @EndTimeUTC DATETIME2(3),
    @RowsExtracted INT,
    @RowsLoaded INT,
    @RowsRejected INT,
    @StationRows INT,
    @ReadingRows INT,
    @WarningRows INT,
    @Status NVARCHAR(50),
    @DurationSeconds DECIMAL(18,3),
    @ErrorMessage NVARCHAR(MAX) = NULL
AS
BEGIN
    SET NOCOUNT ON;

    IF EXISTS (
        SELECT 1
        FROM audit.ETLRunLog
        WHERE RunId = @RunId
    )
    BEGIN
        UPDATE audit.ETLRunLog
        SET
            PipelineName = @PipelineName,
            StartTimeUTC = @StartTimeUTC,
            EndTimeUTC = @EndTimeUTC,
            RowsExtracted = @RowsExtracted,
            RowsLoaded = @RowsLoaded,
            RowsRejected = @RowsRejected,
            StationRows = @StationRows,
            ReadingRows = @ReadingRows,
            WarningRows = @WarningRows,
            Status = @Status,
            DurationSeconds = @DurationSeconds,
            ErrorMessage = @ErrorMessage
        WHERE RunId = @RunId;
    END
    ELSE
    BEGIN
        INSERT INTO audit.ETLRunLog
        (
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
        )
        VALUES
        (
            @RunId,
            @PipelineName,
            @StartTimeUTC,
            @EndTimeUTC,
            @RowsExtracted,
            @RowsLoaded,
            @RowsRejected,
            @StationRows,
            @ReadingRows,
            @WarningRows,
            @Status,
            @DurationSeconds,
            @ErrorMessage
        );
    END;
END;
GO
