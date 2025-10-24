# Fivetran GCS to BigQuery Connector

## Overview

This custom Fivetran-style connector loads CSV data from Google Cloud Storage (GCS) to BigQuery, following Fivetran's data pipeline patterns.

## Configuration

### Fivetran API Credentials
- **API Key**: `GovOjgyu2dCEF51Q`
- **API Secret**: `EgwDk1ukUVCHcCc9NlFM7YBArPqbspdd`

### Source (GCS)
- **Bucket**: `fivetran-hackathon`
- **Default File**: `subscriptions.csv`

### Destination (BigQuery)
- **Project ID**: `hackathon-475722`
- **Dataset**: `test_fivetran`
- **Table**: `gcs_subscriptions` (default)

## Features

✅ **Automatic Dataset Creation** - Creates BigQuery dataset if it doesn't exist  
✅ **Schema Auto-Detection** - Automatically detects column types from CSV  
✅ **Fivetran JSON Output** - Outputs data in Fivetran's JSON lines format  
✅ **Error Handling** - Comprehensive error handling and logging  
✅ **Configurable** - Uses environment variables for flexible configuration  

## Usage

### Method 1: Run with defaults

```bash
python fivetran_gcs_to_bigquery.py
```

### Method 2: Run with batch script (Windows)

```bash
run_fivetran_connector.bat
```

### Method 3: Run with environment variables

```bash
# Set configuration
set GCS_BUCKET_NAME=fivetran-hackathon
set GCS_FILE_PATH=subscriptions.csv
set BIGQUERY_PROJECT_ID=hackathon-475722
set BIGQUERY_DATASET_ID=test_fivetran
set BIGQUERY_TABLE_NAME=gcs_subscriptions

# Run connector
python fivetran_gcs_to_bigquery.py
```

### Method 4: Use as Python module

```python
from fivetran_gcs_to_bigquery import FivetranGCSConnector

# Initialize connector
connector = FivetranGCSConnector(
    project_id="hackathon-475722",
    dataset_id="test_fivetran"
)

# Sync data
df = connector.sync(
    bucket_name="fivetran-hackathon",
    file_path="subscriptions.csv",
    table_name="gcs_subscriptions",
    output_json=True
)
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GCS_BUCKET_NAME` | GCS bucket name | `fivetran-hackathon` |
| `GCS_FILE_PATH` | Path to CSV file in bucket | `subscriptions.csv` |
| `BIGQUERY_PROJECT_ID` | BigQuery project ID | `hackathon-475722` |
| `BIGQUERY_DATASET_ID` | BigQuery dataset name | `test_fivetran` |
| `BIGQUERY_TABLE_NAME` | Target table name | `gcs_subscriptions` |

## Connector Flow

```
1. Initialize Connector
   ↓
2. Ensure BigQuery Dataset Exists
   ↓
3. Load CSV from GCS Bucket
   ↓
4. Parse CSV into DataFrame
   ↓
5. Load DataFrame to BigQuery
   ↓
6. Output JSON Lines (Fivetran Format)
   ↓
7. Complete
```

## Output Format

The connector outputs data in two formats:

### 1. BigQuery Table
Data is loaded directly into BigQuery table with auto-detected schema.

### 2. JSON Lines (stdout)
Each row is output as a JSON object on a single line:
```json
{"subscription_id": "SUB001", "account_id": "ACC001", "mrr_amount": 100}
{"subscription_id": "SUB002", "account_id": "ACC002", "mrr_amount": 200}
```

## Error Handling

The connector handles common errors:

- **GCS Bucket Not Found**: Ensures bucket exists and is accessible
- **File Not Found**: Verifies file exists in GCS bucket
- **BigQuery Permission**: Checks BigQuery write permissions
- **Schema Mismatch**: Auto-detects schema to avoid conflicts
- **Network Issues**: Retries with exponential backoff

## Example Output

```
================================================================================
🚀 Fivetran GCS → BigQuery Sync
================================================================================

📋 Configuration:
   GCS Bucket: fivetran-hackathon
   GCS File: subscriptions.csv
   BigQuery Project: hackathon-475722
   BigQuery Dataset: test_fivetran
   BigQuery Table: gcs_subscriptions

✓ Dataset test_fivetran exists

📥 Loading CSV from GCS...
   Bucket: fivetran-hackathon
   File: subscriptions.csv
✓ Loaded 1000 rows, 14 columns
  Columns: ['subscription_id', 'account_id', 'start_date', ...]

📤 Loading to BigQuery...
   Table: hackathon-475722.test_fivetran.gcs_subscriptions
   Mode: WRITE_APPEND
✓ Loaded 1000 rows to gcs_subscriptions
  Total rows in table: 1000

📋 Fivetran JSON Lines Output:
--------------------------------------------------------------------------------
{"subscription_id": "SUB001", "account_id": "ACC001", ...}
{"subscription_id": "SUB002", "account_id": "ACC002", ...}
...
--------------------------------------------------------------------------------
✓ Output 1000 records

================================================================================
✓ Sync Complete!
================================================================================

✅ Successfully synced 1000 records from GCS to BigQuery!
```

## Class: FivetranGCSConnector

### Methods

#### `__init__(project_id, dataset_id)`
Initialize the connector with BigQuery project and dataset.

#### `ensure_dataset_exists()`
Create BigQuery dataset if it doesn't exist.

#### `load_csv_from_gcs(bucket_name, file_path)`
Load CSV file from GCS bucket and return as DataFrame.

**Returns:** pandas DataFrame

#### `load_to_bigquery(df, table_name, write_disposition='WRITE_APPEND')`
Load DataFrame to BigQuery table.

**Args:**
- `df`: pandas DataFrame
- `table_name`: Target table name
- `write_disposition`: WRITE_TRUNCATE, WRITE_APPEND, or WRITE_EMPTY

#### `output_fivetran_format(df)`
Output DataFrame as JSON lines to stdout (Fivetran format).

#### `sync(bucket_name, file_path, table_name, output_json=True)`
Execute full sync operation from GCS to BigQuery.

**Returns:** pandas DataFrame with synced data

## Requirements

```
google-cloud-storage
google-cloud-bigquery
pandas
```

All requirements are already in `requirements.txt`.

## Troubleshooting

### Issue: "Permission denied" on GCS
**Solution:** Ensure your service account has `Storage Object Viewer` role

### Issue: "Dataset not found"
**Solution:** Connector auto-creates dataset. Ensure BigQuery API is enabled

### Issue: "Schema mismatch"
**Solution:** Use `WRITE_TRUNCATE` to replace table:
```python
connector.load_to_bigquery(df, table_name, write_disposition='WRITE_TRUNCATE')
```

### Issue: "File not found in GCS"
**Solution:** Verify file exists in bucket:
```bash
gsutil ls gs://fivetran-hackathon/
```

## Integration with Streamlit App

To use this connector in the Streamlit app:

```python
from fivetran_gcs_to_bigquery import FivetranGCSConnector

# In your app.py
if st.button("Load Data from GCS"):
    connector = FivetranGCSConnector("hackathon-475722", "test_fivetran")
    df = connector.sync("fivetran-hackathon", "subscriptions.csv", "gcs_data")
    st.success(f"Loaded {len(df)} records!")
    st.dataframe(df)
```

## Next Steps

1. **Run the connector**: `python fivetran_gcs_to_bigquery.py`
2. **Verify in BigQuery**: Check table `hackathon-475722.test_fivetran.gcs_subscriptions`
3. **Query the data**: Use BigQuery console or the NL-to-SQL interface
4. **Automate**: Set up scheduled runs or trigger from Streamlit

## Support

For issues or questions:
1. Check the console output for error messages
2. Verify GCS and BigQuery permissions
3. Review the logs in `fivetran_gcs_to_bigquery.py`

---

**Status**: ✅ Ready to use  
**Version**: 1.0  
**Last Updated**: October 24, 2025
