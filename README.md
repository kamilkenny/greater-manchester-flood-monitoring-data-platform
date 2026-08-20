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
