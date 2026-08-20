# Greater Manchester Flood Monitoring SQL Model

## Architecture

Environment Agency API

Python ingestion

Raw immutable JSON snapshots

Validation and normalisation

SQL staging tables

Dimensional SQL Server model

T SQL analytical layer

SSIS orchestration

SSRS operational reporting

## Staging layer

The staging schema contains:

* stg.Station
* stg.RiverReading
* stg.FloodWarning

## Dimensional layer

### DimStation

One row per monitoring station.

Business key:

StationReference

### FactRiverReading

One row per station, measure and observation timestamp.

Business grain:

StationReference + MeasureId + ReadingDateTimeUTC

### FactFloodWarning

Stores the latest ingested state of each Environment Agency flood warning.

Business key:

WarningId

### audit.ETLRunLog

Stores pipeline execution metadata, row counts, duration, status and error details.

## Reporting views

* vw_CurrentStationStatus
* vw_HighRiverLevelStations
* vw_FloodWarningSummary
* vw_ETLPerformance

## Stored procedures

* usp_LoadStationDimension
* usp_LoadRiverReadings
* usp_LoadFloodWarnings
* usp_BuildFloodMonitoringSummary
* audit.usp_LogETLExecution
