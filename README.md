# Greater Manchester Flood & River Monitoring Data Platform

![Flood Monitoring ETL](https://github.com/kamilkenny/greater-manchester-flood-monitoring-data-platform/actions/workflows/flood-monitoring-refresh.yml/badge.svg)

An end-to-end environmental data engineering, monitoring and operational intelligence platform for Greater Manchester.

The platform collects near real-time river level, rainfall and flood warning information from the Environment Agency, preserves immutable source snapshots, performs automated validation and transformation, loads a dimensional Azure SQL data warehouse, records ETL execution history, and delivers interactive operational reporting through SSRS and Power BI Service.

The project was designed as a practical demonstration of how cloud data engineering, SQL analytics and Microsoft reporting technologies can be combined to transform public environmental data into reliable, auditable and decision-ready information.

---

## Project Status

### ✅ End-to-End Platform Operational

The complete platform has now been implemented and tested across:

- Python data ingestion
- Environment Agency API integration
- automated data validation
- immutable raw-data preservation
- Azure SQL Database
- dimensional data modelling
- T-SQL stored procedures and analytical views
- GitHub Actions orchestration
- Azure OIDC authentication
- SSIS ETL implementation
- SSRS paginated reporting
- Power BI Service deployment
- automated testing and ETL auditing

The production pipeline can be executed manually or automatically through GitHub Actions, while the reporting layer connects to the curated Azure SQL warehouse.

---

# Why This Project Matters

Flood and river monitoring information is operationally important, but raw environmental datasets are not automatically ready for decision-making.

This project focuses on the engineering layer between **public data availability** and **usable operational intelligence**.

It demonstrates how environmental monitoring data can be:

1. collected automatically;
2. preserved for traceability;
3. validated before use;
4. structured into analytical models;
5. monitored for ETL quality and reliability;
6. transformed into reporting-ready information;
7. presented through interactive operational dashboards.

The architecture is particularly relevant to public-sector and regional organisations that need reliable data pipelines to support environmental monitoring, resilience, infrastructure planning, place-based analysis and evidence-led decision-making.

---

# Greater Manchester Focus

The platform monitors Environment Agency stations within a defined geographic radius around Greater Manchester.

It provides an analytical view of:

- river monitoring stations;
- river-level observations;
- rainfall measurements;
- high river-level conditions;
- active flood warnings;
- latest monitoring readings;
- changes in river conditions;
- ETL performance and pipeline health.

The project demonstrates how locally relevant public data can be engineered into a structured regional intelligence platform.

---

# Key Capabilities

## Data Engineering

- Automated Environment Agency API ingestion
- Near real-time monitoring data retrieval
- Immutable JSON source snapshots
- Normalised staging datasets
- Repeatable ETL execution
- Dimensional warehouse design
- Fact and dimension loading
- Incremental operational refresh capability
- Automated data-quality validation
- ETL execution auditing

## Cloud Engineering

- Azure SQL Database
- Serverless compute
- Automatic database resume and auto-pause
- GitHub Actions orchestration
- Azure Managed Identity
- GitHub OpenID Connect authentication
- Temporary GitHub runner firewall access
- Environment-based secret management

## SQL Engineering

- T-SQL staging logic
- Stored procedures
- Dimensional modelling
- reporting views
- data-quality queries
- ETL audit tables
- operational KPI calculations
- analytical transformations

## Microsoft Data Platform

- SQL Server Integration Services (SSIS)
- SQL Server Reporting Services (SSRS)
- Visual Studio / SQL Server Data Tools
- Azure SQL Database
- Power BI Service paginated reporting

## Reporting and Operational Intelligence

- monitored station KPIs;
- high river-level indicators;
- active flood-warning summaries;
- latest observation timestamps;
- parameterised river selection;
- river-level trend visualisation;
- current station status;
- flood-warning summary;
- ETL health and execution metrics.

---

# Technology Stack

| Layer | Technology |
| --- | --- |
| Environmental Data Source | Environment Agency Flood Monitoring API |
| Programming | Python |
| Data Transformation | Python, pandas |
| Cloud Database | Azure SQL Database |
| SQL Development | T-SQL |
| Data Modelling | Dimensional modelling / star-schema principles |
| ETL | Python, SSIS |
| Workflow Automation | GitHub Actions |
| Cloud Authentication | GitHub OIDC, Azure Managed Identity |
| Reporting | SSRS Paginated Reports |
| Cloud Reporting | Power BI Service |
| Testing | pytest |
| Source Control | Git, GitHub |
| Development Environment | Visual Studio, SQL Server Data Tools |
| Cloud Platform | Microsoft Azure |

---

# Platform Architecture

The platform follows a layered data-engineering architecture:

```text
Environment Agency Flood Monitoring API
                │
                ▼
        Python Data Ingestion
                │
                ▼
      Immutable Raw Snapshots
                │
                ▼
   Validation and Data Quality
                │
                ▼
       Normalised Staging
                │
                ▼
        Azure SQL Database
                │
       ┌────────┴────────┐
       ▼                 ▼
 T-SQL Procedures    ETL Audit Layer
       │                 │
       └────────┬────────┘
                ▼
       Reporting Views
                │
                ▼
        SSRS Paginated Report
                │
                ▼
        Power BI Service
