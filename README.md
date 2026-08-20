# Greater Manchester Flood & River Monitoring ETL & Reporting Platform

![Flood Monitoring ETL](https://github.com/kamilkenny/greater-manchester-flood-monitoring-data-platform/actions/workflows/flood-monitoring-refresh.yml/badge.svg)

An end to end environmental data engineering and operational reporting platform for monitoring river levels, rainfall observations and flood warning information around Greater Manchester.

The platform collects Environment Agency flood monitoring data, preserves raw source snapshots, validates and transforms the data, loads an Azure SQL dimensional warehouse, records ETL execution information and prepares curated reporting views for SSRS.

## Project Status

**Cloud ETL platform: Operational**

The Python, Azure SQL, T SQL and GitHub Actions components have been implemented and successfully tested in production.

SSIS and SSRS implementation specifications are included in the repository. Native Visual Studio SSIS and SSRS project artefacts are the remaining Microsoft desktop implementation phase.

## Key Capabilities

- Environment Agency API ingestion
- Immutable JSON source snapshots
- Automated data validation and quality checks
- Normalised staging datasets
- Azure SQL dimensional warehouse
- T SQL stored procedures
- Analytical reporting views
- ETL execution auditing
- GitHub Actions orchestration
- Passwordless Azure OIDC authentication
- Temporary runner specific SQL firewall access
- Serverless Azure SQL automatic resume and auto pause
- Automated testing with pytest
- SSIS package design
- SSRS operational dashboard design

## Technology Stack

| Layer | Technology |
| --- | --- |
| Source | Environment Agency Flood Monitoring API |
| Ingestion | Python |
| Transformation | Python, pandas |
| Database | Azure SQL Database |
| SQL Development | T SQL |
| Orchestration | GitHub Actions |
| Authentication | GitHub OIDC, Azure Managed Identity |
| ETL | Python, SSIS specification |
| Reporting | SQL views, SSRS specification |
| Testing | pytest |
| Version Control | Git, GitHub |
| Cloud | Microsoft Azure |

## Architecture

The detailed platform architecture is documented in `docs/architecture.md`.

Core data flow:

Environment Agency API → Python ingestion → validation → staging → Azure SQL → T SQL procedures → reporting views → SSRS.

Raw source snapshots are preserved separately from validated staging datasets.

## Azure SQL Data Model

The warehouse contains:

- `dbo.DimStation`
- `dbo.FactRiverReading`
- `dbo.FactFloodWarning`
- `audit.ETLRunLog`

The reporting layer includes:

- `dbo.vw_CurrentStationStatus`
- `dbo.vw_CurrentRiverLevels`
- `dbo.vw_CurrentRainfall`
- `dbo.vw_HighRiverLevelStations`
- `dbo.vw_FloodWarningSummary`
- `dbo.vw_ETLPerformance`

## Initial Validated Load

The initial production deployment loaded:

- 259 monitoring stations
- 248 latest local readings
- 0 duplicate stations
- 0 duplicate readings
- 0 orphan readings

## Automation

The production workflow is defined in:

`.github/workflows/flood-monitoring-refresh.yml`

The Azure SQL warehouse refresh is scheduled daily at **02:15 UTC**.

Manual workflow execution is also available through GitHub Actions.

The conservative daily cadence is intentional for the Azure SQL free serverless deployment. The ingestion architecture can support a higher refresh frequency when additional compute capacity is available.

## Security

GitHub Actions authenticates to Azure using:

- GitHub OpenID Connect
- Azure user assigned managed identity
- Repository specific federated identity trust

A temporary IP specific Azure SQL firewall rule is created for each GitHub hosted runner and removed after the ETL finishes.

Database credentials are stored in GitHub Actions Secrets and are never committed to the repository.

## Data Quality

The pipeline checks duplicate records, missing metadata, missing coordinates, missing readings, measure coverage, orphan facts and ETL execution errors.

Automated Python tests are executed using `pytest`.

## SSIS Implementation

The intended package is:

`PKG_Load_Environment_Agency_Data.dtsx`

The implementation specification is available at:

`ssis/GM_Flood_Monitoring_ETL.md`

The package design covers staging loads, dimensional transformations, stored procedure execution, audit logging and failure handling.

## SSRS Reporting

The intended report is:

**Greater Manchester Flood & River Monitoring Dashboard**

The specification is available at:

`ssrs/GM_Flood_Monitoring_Dashboard.md`

The dashboard design includes station status, river levels, rainfall, flood warnings, trends and ETL performance.

## Current Project Status

The Python, Azure SQL, T SQL and GitHub Actions cloud engineering platform is operational and has completed a successful automated production ETL run.

Native Visual Studio SSIS `.dtsx` and SSRS `.rdl` artefacts remain the final desktop implementation phase.

## Important Disclaimer

This project is intended for research, learning and portfolio demonstration.

It is not a replacement for official Environment Agency flood warning or emergency services.
