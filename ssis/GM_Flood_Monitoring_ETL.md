# SSIS Package: GM_Flood_Monitoring_ETL

## Package

PKG_Load_Environment_Agency_Data.dtsx

## Objective

Load validated Greater Manchester Environment Agency flood monitoring datasets into Azure SQL and execute the dimensional transformation layer.

## Control Flow

1. Execute Process Task
   Run Python Environment Agency ingestion.

2. Data Flow Task
   Load stations.csv into stg.Station.

3. Data Flow Task
   Load latest_readings.csv into stg.RiverReading.

4. Data Flow Task
   Load flood_warnings.csv into stg.FloodWarning.

5. Execute SQL Task
   EXEC dbo.usp_LoadStationDimension;

6. Execute SQL Task
   EXEC dbo.usp_LoadRiverReadings;

7. Execute SQL Task
   EXEC dbo.usp_LoadFloodWarnings;

8. Execute SQL Task
   EXEC dbo.usp_BuildFloodMonitoringSummary;

9. Execute SQL Task
   Write successful execution to audit.ETLRunLog.

## Failure Path

Every critical task uses an OnError precedence path.

On failure:

1. Capture package name.
2. Capture task name.
3. Capture execution start and end time.
4. Capture SSIS error description.
5. Write FAILED status to audit.ETLRunLog.

## Connection Managers

EA_Staging_Files

AzureSQL_GMFloodMonitoring

## Deployment Target

SQL Server Integration Services project deployment model.
