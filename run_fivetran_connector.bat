@echo off
REM Fivetran GCS to BigQuery Connector Test Script

echo ===============================================================================
echo Fivetran GCS to BigQuery Data Loader
echo ===============================================================================
echo.

cd /d D:\CloudHeroWithAI\Hackthon-DEVPOST-AI-accelarate\fivetransdk-churn-agent

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running Fivetran connector...
echo.

python fivetran_gcs_to_bigquery.py

echo.
echo ===============================================================================
echo Connector execution complete
echo ===============================================================================
echo.

pause
