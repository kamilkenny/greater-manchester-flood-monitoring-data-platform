#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

source .venv/bin/activate

set -a
source .env
set +a

echo "=========================================="
echo "GREATER MANCHESTER FLOOD MONITORING ETL"
echo "=========================================="

python -m flood_monitoring.pipeline

python -m flood_monitoring.database.azure_sql_loader

python -m pytest -q

echo
echo "ETL PIPELINE COMPLETED SUCCESSFULLY"
