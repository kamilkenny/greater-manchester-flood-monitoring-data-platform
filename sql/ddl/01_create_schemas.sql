IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'stg'
)
    EXEC('CREATE SCHEMA stg');
GO

IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = 'audit'
)
    EXEC('CREATE SCHEMA audit');
GO
