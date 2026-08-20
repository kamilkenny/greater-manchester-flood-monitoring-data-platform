# SSRS Report

Greater Manchester Flood & River Monitoring Dashboard

## Data Source

Azure SQL Database

Database:

gm_flood_monitoring

## Primary Datasets

### CurrentRiverLevels

Source:

dbo.vw_CurrentRiverLevels

### HighRiverLevelStations

Source:

dbo.vw_HighRiverLevelStations

### FloodWarningSummary

Source:

dbo.vw_FloodWarningSummary

### ETLPerformance

Source:

dbo.vw_ETLPerformance

## Report Parameters

RiverName

StationReference

StartDate

EndDate

## KPI Cards

Total monitoring stations

Latest observations

Elevated river level stations

Active flood warnings

Last ETL execution

ETL status

## Main Visuals

River level status table

Current river level by station

River level trend chart

Flood warning severity table

ETL run history

Data quality summary

## Conditional Formatting

NORMAL

ELEVATED

ABOVE TYPICAL RANGE

## Operational Monitoring

Display:

Last successful ETL run

Pipeline duration

Rows extracted

Rows loaded

Rows rejected

Error message when applicable
