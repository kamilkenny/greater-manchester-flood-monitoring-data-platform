# Greater Manchester Flood & River Monitoring Data Platform

<img width="1567" height="1129" alt="Greater Manchester Flood Monitoring Platform" src="https://github.com/user-attachments/assets/bca66ede-cc5d-4403-93d5-16c3376b709a" />

<img width="1672" height="941" alt="Greater Manchester Flood Monitoring Intelligence" src="https://github.com/user-attachments/assets/068c3860-2ea4-4565-a8bf-8e58ca3665c9" />

![Flood Monitoring ETL](https://github.com/kamilkenny/greater-manchester-flood-monitoring-data-platform/actions/workflows/flood-monitoring-refresh.yml/badge.svg)

## Greater Manchester Flood & River Intelligence

An end-to-end environmental **data engineering, monitoring and operational intelligence platform** for Greater Manchester, developed using Python, Azure SQL, T-SQL, SSIS, SSRS, Power BI, Dash, GitHub Actions and Microsoft Azure.

The platform transforms near real-time Environment Agency river, rainfall and flood-warning data into a governed, auditable and reporting-ready analytical system.

It automatically:

- collects environmental monitoring data from public APIs;
- preserves immutable source snapshots;
- validates incoming records;
- normalises operational datasets;
- loads a dimensional Azure SQL warehouse;
- executes T-SQL transformations and stored procedures;
- records ETL execution history and data-quality results;
- exposes governed analytical views;
- supports SSRS and Power BI reporting;
- delivers a public-facing interactive flood intelligence application through Microsoft Azure.

Rather than focusing only on dashboard development, the project demonstrates the **complete data engineering lifecycle**, from source-system ingestion and data validation through dimensional modelling, orchestration, monitoring, reporting and cloud deployment.

---

# Live Platform

## Public Flood Intelligence Dashboard

**Greater Manchester Flood & River Intelligence**

https://gm-flood-intelligence-kamil-898341.azurewebsites.net/

The live application provides operational visibility of:

- monitored Environment Agency stations;
- current river conditions;
- rainfall observations;
- elevated river levels;
- flood-warning status;
- geographical monitoring locations;
- historical river-level behaviour;
- latest observation timestamps;
- ETL execution health;
- pipeline refresh status.

---

# Project Status

## ✅ End-to-End Platform Operational

<img width="1156" height="436" alt="Flood Monitoring Pipeline" src="https://github.com/user-attachments/assets/f4f06eec-bd97-417f-8ce5-46fe07358d33" />

<img width="1490" height="528" alt="Flood Monitoring Data Engineering" src="https://github.com/user-attachments/assets/bc454018-b1e6-476c-b880-cebdc837f802" />

<img width="1154" height="452" alt="Flood Monitoring Reporting" src="https://github.com/user-attachments/assets/cf1748ed-d088-4c43-b56e-e08d5c442659" />

<img width="1152" height="697" alt="Flood Monitoring Analytics" src="https://github.com/user-attachments/assets/0005ef9a-481c-4904-ad52-972be4f26631" />

The complete platform has been implemented across the following layers:

- Python data ingestion
- Environment Agency Flood Monitoring API integration
- immutable source-data preservation
- automated data validation
- staging and transformation
- Azure SQL Database
- dimensional data modelling
- T-SQL stored procedures
- analytical reporting views
- GitHub Actions orchestration
- Azure OpenID Connect authentication
- ETL audit logging
- SSIS ETL implementation
- SSRS paginated reporting
- Power BI reporting
- Dash operational intelligence application
- Azure web deployment
- automated testing
- data-quality monitoring
- pipeline-health monitoring

The production-style pipeline can be executed manually or automatically through GitHub Actions, while multiple presentation technologies consume governed data from the Azure SQL reporting layer.

---

# Engineering Achievement

This project was developed as a **production-style environmental data platform**, rather than as a standalone visualisation exercise.

The main engineering achievement was designing and implementing a complete pathway from raw public environmental data to reliable operational intelligence.

The platform demonstrates:

**API ingestion → raw-data preservation → validation → staging → transformation → dimensional modelling → Azure SQL → orchestration → monitoring → reporting → cloud deployment**

This architecture allows the same governed data layer to support multiple downstream consumers without reproducing transformation logic independently inside each reporting application.

---

# Why This Project Matters

Flood and river monitoring information is operationally important, but raw environmental datasets are not automatically suitable for decision-making.

Public APIs may expose useful information, but an operational organisation still requires processes for:

- reliable ingestion;
- validation;
- traceability;
- transformation;
- historical retention;
- analytical modelling;
- exception identification;
- automated refresh;
- monitoring;
- reporting;
- governance.

This project focuses on the engineering layer between **public data availability** and **decision-ready operational intelligence**.

It demonstrates how environmental monitoring data can be transformed into a structured regional intelligence system that supports:

- environmental monitoring;
- flood resilience;
- infrastructure planning;
- regional analysis;
- operational reporting;
- public-sector data intelligence;
- place-based decision-making;
- evidence-led planning.

---

# Greater Manchester Focus

The platform monitors Environment Agency stations within a defined geographic area around Greater Manchester.

It provides an analytical view of:

- river monitoring stations;
- rivers and catchments;
- river-level observations;
- rainfall measurements;
- high river-level conditions;
- flood-warning information;
- latest monitoring readings;
- historical river behaviour;
- geographical station locations;
- ETL execution performance;
- pipeline health.

The project demonstrates how national public datasets can be engineered into **locally relevant regional intelligence**.

This is particularly applicable to organisations working across:

- local government;
- combined authorities;
- environmental resilience;
- transport and infrastructure;
- planning;
- emergency preparedness;
- sustainability;
- public-sector analytics;
- regional digital transformation.

---

# Engineering Achievements and Outcomes

Key achievements delivered through the project include:

- Designed and implemented an end-to-end environmental data pipeline from the Environment Agency Flood Monitoring API through ingestion, validation, transformation, Azure SQL warehousing and operational reporting.

- Built automated ingestion workflows for river levels, rainfall observations, monitoring stations and flood-warning information using Python.

- Implemented immutable raw-data preservation so that source extracts can be retained for traceability, reproducibility and audit.

- Developed normalised staging datasets to separate source ingestion from downstream analytical processing.

- Designed dimensional data structures in Azure SQL using fact and dimension modelling principles.

- Implemented T-SQL stored procedures to support repeatable warehouse loading and transformation.

- Created governed analytical views that provide reporting-ready datasets to downstream applications.

- Developed automated data-quality validation to identify incomplete, invalid and duplicate records before they reach analytical reporting.

- Implemented ETL execution logging to record pipeline status, refresh timestamps, processing duration and loaded-row information.

- Automated recurring pipeline execution through GitHub Actions.

- Implemented secure Azure authentication using GitHub OpenID Connect rather than embedding long-lived Azure credentials within source code.

- Developed an SSIS implementation of the ETL workflow to demonstrate enterprise Microsoft data-integration capability alongside the Python pipeline.

- Developed SSRS paginated reporting using curated Azure SQL datasets.

- Integrated Power BI reporting with the governed SQL analytical layer.

- Built and deployed an Azure-hosted Dash application for public-facing river, rainfall, flood-warning and pipeline-health intelligence.

- Implemented geographical station monitoring using latitude and longitude information.

- Developed parameterised river exploration so users can select rivers and inspect recent monitoring observations.

- Implemented exception-focused analysis for elevated river levels and flood-warning conditions.

- Built dynamic visual handling for operational states, including no-rainfall and no-active-warning conditions.

- Created a reusable reporting architecture in which Dash, SSRS and Power BI consume the same governed SQL reporting layer.

- Applied Git-based source control, feature branching, automated validation and controlled cloud deployment throughout development.

---

# Key Capabilities

## Data Engineering

- Environment Agency API ingestion
- automated near real-time data retrieval
- JSON source snapshot preservation
- staging-layer processing
- data normalisation
- transformation pipelines
- incremental operational refresh
- dimensional warehouse loading
- automated data validation
- ETL execution auditing
- exception monitoring
- reusable analytical datasets

## Cloud Engineering

- Microsoft Azure
- Azure SQL Database
- Azure-hosted application deployment
- GitHub Actions orchestration
- GitHub OpenID Connect authentication
- environment-based configuration
- secure secret handling
- cloud application configuration
- automated deployment validation

## SQL Engineering

- T-SQL development
- stored procedures
- reporting views
- staging logic
- dimensional modelling
- analytical queries
- ETL audit tables
- data-quality queries
- KPI calculations
- historical analysis
- reporting transformations

## Microsoft Data Platform

- Azure SQL Database
- SQL Server Integration Services
- SQL Server Reporting Services
- SQL Server Data Tools
- Visual Studio
- Power BI
- T-SQL
- Microsoft Azure

## Data Quality and Governance

- source snapshot preservation
- invalid-record detection
- duplicate detection
- completeness checking
- staging controls
- governed reporting views
- ETL execution history
- reproducible transformations
- secret separation from source code
- auditable pipeline execution

## Reporting and Operational Intelligence

- monitored-station KPIs
- river-level monitoring
- elevated-level indicators
- flood-warning summaries
- rainfall monitoring
- latest observation timestamps
- geographical station maps
- river selection
- historical hydrographs
- current station status
- exception monitoring
- ETL health reporting
- pipeline refresh monitoring

---

# Technology Stack

| Layer | Technology |
| --- | --- |
| Environmental Data Source | Environment Agency Flood Monitoring API |
| Programming | Python |
| Data Processing | pandas |
| Application Framework | Dash |
| Visualisation | Plotly |
| Cloud Database | Azure SQL Database |
| SQL Development | T-SQL |
| Data Modelling | Dimensional modelling / star-schema principles |
| ETL | Python, SSIS |
| Workflow Automation | GitHub Actions |
| Cloud Authentication | GitHub OIDC |
| Operational Reporting | SSRS Paginated Reports |
| Analytical Reporting | Power BI |
| Testing | pytest |
| Source Control | Git, GitHub |
| Development Environment | Visual Studio, SQL Server Data Tools |
| Web Hosting | Azure App Service |
| Cloud Platform | Microsoft Azure |

---

# Platform Architecture

The platform follows a layered data-engineering architecture.

```text
                Environment Agency
              Flood Monitoring API
                       │
                       ▼
               Python Ingestion
                       │
                       ▼
            Immutable Raw Snapshots
                       │
                       ▼
          Validation & Data Quality
                       │
                       ▼
              Normalised Staging
                       │
                       ▼
               Azure SQL Database
                       │
            ┌──────────┴──────────┐
            │                     │
            ▼                     ▼
     T-SQL Procedures        ETL Audit Layer
            │                     │
            └──────────┬──────────┘
                       │
                       ▼
               Reporting Views
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
       SSRS         Power BI     Dash Web App
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
             Operational Intelligence
```

The important architectural principle is that business and transformation logic is concentrated within the ingestion, transformation and SQL layers.

Reporting tools therefore consume **governed reporting datasets** instead of reproducing independent versions of the same calculations.

---

# Data Pipeline

## 1. Source Acquisition

The platform retrieves publicly available environmental monitoring information from the Environment Agency Flood Monitoring API.

The ingestion layer collects datasets relating to:

- monitoring stations;
- river-level readings;
- rainfall observations;
- flood warnings.

---

## 2. Raw Data Preservation

Source responses are preserved before transformation.

This provides:

- traceability;
- reproducibility;
- historical evidence;
- debugging capability;
- protection against source-system changes.

The raw layer is treated as an immutable representation of received source data.

---

## 3. Validation

Before analytical processing, records pass through validation checks.

Validation includes checks for:

- missing values;
- invalid records;
- incomplete observations;
- malformed fields;
- duplicate data;
- unexpected source conditions.

This prevents poor-quality data from silently entering the analytical layer.

---

## 4. Staging

Validated data is transformed into normalised staging datasets.

The staging layer separates external API structures from downstream warehouse structures and provides a controlled interface for loading Azure SQL.

---

## 5. Azure SQL Warehouse

Validated information is loaded into Azure SQL Database.

The warehouse supports:

- monitoring station dimensions;
- river observations;
- rainfall information;
- flood-warning information;
- historical analysis;
- operational reporting;
- ETL execution logging.

The design uses dimensional modelling principles to separate descriptive entities from analytical events.

---

## 6. Transformation

T-SQL stored procedures perform repeatable transformation and warehouse-loading operations.

The SQL layer supports:

- staging-to-core transformation;
- fact loading;
- dimension loading;
- analytical calculations;
- current-state reporting;
- exception identification;
- ETL monitoring.

---

## 7. Analytical Views

Curated SQL views expose reporting-ready information.

Examples include analytical datasets for:

- current station status;
- current river levels;
- current rainfall;
- high river-level stations;
- flood-warning summaries;
- ETL performance.

These views provide a consistent data contract for reporting applications.

---

## 8. Reporting

The analytical layer feeds multiple reporting technologies.

### Dash

The Azure-hosted Dash application provides interactive public-facing operational intelligence.

### SSRS

SSRS provides structured and parameterised paginated operational reporting.

### Power BI

Power BI provides analytical and stakeholder-focused reporting using governed datasets from Azure SQL.

---

# Operational Intelligence Dashboard

The public application presents the data as an operational flood and river intelligence interface rather than simply reproducing raw API records.

It includes:

## Monitoring Overview

- monitored station count;
- elevated river-level count;
- flood-warning state;
- latest observation timestamp.

## Geographic Intelligence

Monitoring locations are displayed geographically using station latitude and longitude.

This allows users to understand where monitoring activity and elevated conditions are occurring across Greater Manchester.

## River Explorer

Users can select individual rivers and examine recent monitoring history.

The hydrograph provides a clearer view of:

- observation trends;
- latest river level;
- historical movement;
- available typical-range context.

## Rainfall Intelligence

Rainfall observations are ranked when measurable rainfall exists.

When no measurable rainfall is detected, the platform displays a clear operational status rather than a meaningless zero-value chart.

## Flood Warning Intelligence

Active warning conditions are prioritised according to operational severity.

Where Environment Agency information indicates that a warning is no longer in force, the dashboard reports that state clearly rather than presenting it as an active warning.

## Pipeline Health

The application also exposes data-engineering health information including:

- ETL state;
- latest refresh;
- loaded rows;
- execution duration;
- pipeline status.

This allows the dashboard to communicate not only **what the environmental data says**, but also whether the underlying data pipeline is operating correctly.

---

# ETL Monitoring and Observability

Reliable data engineering requires visibility into pipeline execution.

The project therefore records ETL execution information including:

- run status;
- execution timestamp;
- refresh timestamp;
- rows processed;
- rows loaded;
- execution duration;
- pipeline messages.

This provides an auditable operational history and makes pipeline failures easier to investigate.

Monitoring the engineering process alongside the analytical output is an important part of the platform design.

---

# Automation

The platform supports automated execution through GitHub Actions.

The automated workflow can:

1. authenticate securely with Azure;
2. retrieve Environment Agency monitoring data;
3. preserve source snapshots;
4. validate incoming datasets;
5. transform staging information;
6. load Azure SQL;
7. execute analytical transformations;
8. record ETL execution;
9. validate the resulting data state.

This demonstrates how development workflows and cloud orchestration can be integrated into a practical data-engineering solution.

---

# Security Approach

The project avoids storing sensitive Azure credentials directly within the source repository.

Security practices include:

- environment-based configuration;
- GitHub secret management;
- OpenID Connect authentication;
- separation of credentials from application code;
- exclusion of local `.env` files from source control and deployment packages.

This supports a more secure deployment model than embedding long-lived credentials in scripts or configuration committed to Git.

---

# SSIS Implementation

An SSIS implementation was developed alongside the Python pipeline to demonstrate enterprise Microsoft data-integration capability.

This provides practical evidence of working with:

- SQL Server Integration Services;
- Visual Studio;
- SQL Server Data Tools;
- ETL package design;
- source-to-destination mappings;
- transformation workflows;
- SQL-based integration processes.

The Python and SSIS implementations demonstrate the ability to work across both modern code-based pipelines and established enterprise Microsoft data-integration technologies.

---

# SSRS Reporting

The project includes SSRS paginated reporting connected to the curated analytical layer.

The reporting approach demonstrates:

- parameterised reports;
- SQL datasets;
- structured operational reporting;
- reusable analytical views;
- stakeholder-focused information presentation.

SSRS complements the interactive Dash and Power BI reporting layers by providing structured enterprise-style reporting.

---

# Power BI

Power BI consumes governed analytical information from Azure SQL rather than independently reconstructing the transformation logic.

This demonstrates an important data-platform principle:

> **Business intelligence should consume trusted analytical data products rather than reproduce data-engineering logic within individual dashboards.**

The architecture therefore separates:

- ingestion;
- transformation;
- modelling;
- reporting.

---

# Skills Demonstrated

| Capability | Evidence in This Project |
| --- | --- |
| Python Data Engineering | API ingestion, transformation, validation and pipeline automation |
| SQL / T-SQL | Stored procedures, analytical views, queries and warehouse loading |
| ETL / ELT | Raw → staging → warehouse → reporting workflow |
| Azure SQL | Cloud-hosted relational and analytical serving layer |
| Data Modelling | Fact and dimension design using dimensional principles |
| API Integration | Environment Agency Flood Monitoring API |
| Data Quality | Validation, completeness checking and duplicate handling |
| Data Governance | Immutable source snapshots and governed reporting views |
| Workflow Automation | GitHub Actions orchestration |
| Cloud Authentication | GitHub OpenID Connect |
| SSIS | Enterprise Microsoft ETL implementation |
| SSRS | Parameterised paginated operational reporting |
| Power BI | Analytical reporting from governed SQL datasets |
| Dash | Interactive operational intelligence application |
| Plotly | River, rainfall, warning and geographical visualisation |
| Monitoring | ETL audit logging and pipeline-health reporting |
| DevOps | Git, GitHub, branching, automated deployment and validation |
| Cloud Deployment | Azure-hosted operational intelligence application |
| Public Data Engineering | Transformation of national environmental data into regional intelligence |

---

# Professional Relevance

This project demonstrates capabilities relevant to a range of data and analytics roles.

## Data Engineering

The platform provides practical evidence of:

- API ingestion;
- Python ETL;
- SQL development;
- dimensional modelling;
- automated pipelines;
- Azure SQL;
- workflow orchestration;
- testing;
- monitoring;
- cloud deployment.

## Public-Sector Data and Intelligence

The platform demonstrates how publicly available national data can be transformed into locally relevant regional intelligence.

This is applicable to organisations working in:

- combined authorities;
- local government;
- infrastructure;
- environmental services;
- resilience;
- planning;
- transport;
- sustainability;
- regional intelligence.

## Microsoft Data Platform

The project demonstrates practical use of:

- Azure SQL;
- T-SQL;
- SSIS;
- SSRS;
- Power BI;
- Visual Studio;
- SQL Server Data Tools.

## Analytics and Business Intelligence

The project demonstrates how trusted analytical datasets can support multiple downstream presentation technologies while retaining consistent underlying business logic.

---

# Why the Architecture Is Reusable

Although this project focuses on flood and river monitoring, the architectural pattern is reusable for many operational-data scenarios.

The same design could be adapted for:

- transport monitoring;
- air-quality monitoring;
- weather intelligence;
- infrastructure monitoring;
- energy-system monitoring;
- environmental compliance;
- public-health indicators;
- asset monitoring;
- regional performance reporting.

The reusable pattern is:

```text
External Data Source
        │
        ▼
Automated Ingestion
        │
        ▼
Immutable Raw Layer
        │
        ▼
Validation
        │
        ▼
Staging
        │
        ▼
Analytical Warehouse
        │
        ▼
Governed Reporting Views
        │
        ▼
Operational Intelligence
```

---

# Design Principles

The project follows several practical data-engineering principles.

## Preserve the Source

Raw source responses are retained before transformation.

## Validate Before Reporting

Data-quality checks are applied before records reach analytical reporting.

## Separate Pipeline Layers

Raw, staging, warehouse and reporting responsibilities are kept conceptually distinct.

## Centralise Analytical Logic

Transformation and business logic are implemented upstream rather than independently inside each visualisation tool.

## Monitor the Pipeline

ETL execution is treated as operational data in its own right.

## Secure the Deployment

Credentials and secrets are separated from application source code.

## Support Multiple Consumers

One governed analytical layer supports Dash, SSRS and Power BI.

---

# Project Outcomes

The completed platform demonstrates the ability to take an environmental-data problem from initial source exploration through to an operational cloud implementation.

The project brings together:

- public API integration;
- Python engineering;
- SQL engineering;
- data modelling;
- Microsoft data-platform technologies;
- automation;
- data quality;
- observability;
- reporting;
- cloud deployment.

The result is not simply a collection of scripts or visualisations.

It is a **complete data platform that converts public environmental monitoring data into structured, governed and operationally useful intelligence**.

---

# Data Source

Environmental monitoring information is obtained from the publicly available:

**Environment Agency Flood Monitoring API**

The Environment Agency remains the authoritative source for official flood-warning and environmental-monitoring information.

This project processes that publicly available information for educational, research and portfolio purposes.

---

# Disclaimer

This platform is an independent data-engineering and analytical project.

It is **not an official flood-warning service** and should not be used as a substitute for official Environment Agency flood alerts, warnings or emergency guidance.

For safety-critical flood information, users should always refer to official Environment Agency and UK Government services.

---

# Author

**Kamil Ridwan Kehinde**

Engineering Researcher | Data Engineer | Energy & Infrastructure Data Intelligence

Areas of interest include:

- data engineering;
- cloud analytics;
- energy systems;
- infrastructure intelligence;
- environmental data;
- predictive analytics;
- operational monitoring;
- Microsoft data platforms;
- artificial intelligence for engineering systems.

---

# Repository Purpose

This repository was developed as a practical demonstration of end-to-end data engineering using real-world public environmental data.

It demonstrates the integration of:

**Python + SQL + Azure + SSIS + SSRS + Power BI + GitHub Actions + Dash**

within a single operational data-platform project.

The repository is intended to demonstrate practical engineering capability across the full data lifecycle, from source acquisition to cloud-hosted operational intelligence.
