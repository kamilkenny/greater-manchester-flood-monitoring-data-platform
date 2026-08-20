# Platform Architecture

## Overview

The Greater Manchester Flood & River Monitoring ETL & Reporting Platform collects near real time Environment Agency monitoring data, validates source records, loads analytical data into Azure SQL, and prepares the warehouse for operational reporting through SSIS and SSRS.

## Architecture

```mermaid
flowchart TD
    EA[Environment Agency Flood Monitoring API]
    PY[Python Ingestion Layer]
    RAW[Immutable Raw JSON Snapshots]
    DQ[Validation and Data Quality]
    CSV[Validated Staging CSV Files]

    GH[GitHub Actions Every 15 Minutes]
    OIDC[GitHub OIDC]
    MI[Azure User Assigned Managed Identity]
    RESUME[Resume Azure SQL]
    FW[Temporary Runner Firewall Rule]

    STG[Azure SQL Staging Schema]
    PROC[T SQL Stored Procedures]
    DIM[DimStation]
    READ[FactRiverReading]
    WARN[FactFloodWarning]
    AUDIT[ETLRunLog]
    VIEWS[Reporting Views]

    SSIS[SSIS Package Implementation]
    SSRS[SSRS Operational Reporting]

    CLEAN[Remove Temporary Firewall Rule]
    PAUSE[Pause Azure SQL]

    EA --> PY
    PY --> RAW
    PY --> DQ
    DQ --> CSV

    GH --> OIDC
    OIDC --> MI
    GH --> RESUME
    MI --> FW
    GH --> PY

    CSV --> STG
    STG --> PROC

    PROC --> DIM
    PROC --> READ
    PROC --> WARN
    PROC --> AUDIT

    DIM --> VIEWS
    READ --> VIEWS
    WARN --> VIEWS
    AUDIT --> VIEWS

    CSV --> SSIS
    SSIS --> STG
    VIEWS --> SSRS

    GH --> CLEAN
    CLEAN --> PAUSE
```
