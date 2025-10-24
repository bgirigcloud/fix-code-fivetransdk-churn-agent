"""
Fivetran Custom Connector - GCS to BigQuery
Loads CSV data from Google Cloud Storage to BigQuery using Fivetran SDK
"""
import os
import sys
import json
import io
import pandas as pd
from google.cloud import storage
from fivetran_sdk.bigquery.connector import BigQueryConnector

# Configuration
FIVETRAN_API_KEY = "GovOjgyu2dCEF51Q"
FIVETRAN_API_SECRET = "EgwDk1ukUVCHcCc9NlFM7YBArPqbspdd"
GCS_BUCKET_NAME = "fivetran-hackathon"
BIGQUERY_PROJECT_ID = "hackathon-475722"
BIGQUERY_DATASET_ID = "test_fivetran"

def get_config_value(key, default=None):
    """
    Retrieves a configuration value from environment variables.
    Falls back to default if not set.
    """
    return os.environ.get(key, default)

def load_csv_from_gcs(bucket_name, file_path):
    """
    Load CSV file from Google Cloud Storage
    
    Args:
        bucket_name: GCS bucket name
        file_path: Path to CSV file in the bucket
        
    Returns:
        pandas DataFrame with CSV data
    """
    print(f"Loading CSV from GCS bucket: {bucket_name}/{file_path}")
    
    try:
        # Initialize GCS client
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file_path)
        
        # Download CSV content
        csv_content = blob.download_as_text()
        print(f"✓ Downloaded {len(csv_content)} bytes from GCS")
        
        # Parse CSV into DataFrame
        df = pd.read_csv(io.StringIO(csv_content))
        print(f"✓ Parsed CSV: {len(df)} rows, {len(df.columns)} columns")
        print(f"  Columns: {list(df.columns)}")
        
        return df
        
    except Exception as e:
        print(f"✗ Error loading CSV from GCS: {e}", file=sys.stderr)
        raise

def load_to_bigquery_with_fivetran(df, table_name):
    """
    Load DataFrame to BigQuery using Fivetran SDK
    
    Args:
        df: pandas DataFrame to load
        table_name: Target table name in BigQuery
    """
    print(f"\nLoading data to BigQuery using Fivetran SDK...")
    print(f"  Project: {BIGQUERY_PROJECT_ID}")
    print(f"  Dataset: {BIGQUERY_DATASET_ID}")
    print(f"  Table: {table_name}")
    
    try:
        # Initialize Fivetran BigQuery Connector
        connector = BigQueryConnector(
            project_id=BIGQUERY_PROJECT_ID,
            dataset_id=BIGQUERY_DATASET_ID,
            api_key=FIVETRAN_API_KEY,
            api_secret=FIVETRAN_API_SECRET
        )
        
        # Load data
        connector.load_dataframe(
            dataframe=df,
            table_name=table_name,
            write_disposition='WRITE_APPEND'  # Options: WRITE_TRUNCATE, WRITE_APPEND, WRITE_EMPTY
        )
        
        print(f"✓ Successfully loaded {len(df)} rows to BigQuery")
        print(f"  Table: {BIGQUERY_PROJECT_ID}.{BIGQUERY_DATASET_ID}.{table_name}")
        
    except Exception as e:
        print(f"✗ Error loading to BigQuery: {e}", file=sys.stderr)
        raise

def output_json_lines(df):
    """
    Output DataFrame as JSON lines to stdout (Fivetran format)
    
    Args:
        df: pandas DataFrame to output
    """
    print("\nOutputting data as JSON lines for Fivetran...")
    
    for idx, row in df.iterrows():
        # Convert row to dictionary and output as JSON
        record = row.to_dict()
        print(json.dumps(record))
    
    print(f"✓ Output {len(df)} records as JSON lines")

def main():
    """Main function for Fivetran custom connector"""
    
    print("=" * 80)
    print("Fivetran Custom Connector - GCS to BigQuery")
    print("=" * 80)
    
    # Get configuration from environment variables or use defaults
    gcs_bucket_name = get_config_value("GCS_BUCKET_NAME", GCS_BUCKET_NAME)
    gcs_file_path = get_config_value("GCS_FILE_PATH", "subscriptions.csv")  # Default file
    bigquery_project = get_config_value("BIGQUERY_PROJECT_ID", BIGQUERY_PROJECT_ID)
    bigquery_dataset = get_config_value("BIGQUERY_DATASET_ID", BIGQUERY_DATASET_ID)
    table_name = get_config_value("BIGQUERY_TABLE_NAME", "gcs_data")
    
    # Validate required configuration
    if not gcs_bucket_name or not gcs_file_path:
        print("✗ Error: GCS_BUCKET_NAME and GCS_FILE_PATH must be set", file=sys.stderr)
        print("  Set them as environment variables or use defaults", file=sys.stderr)
        sys.exit(1)
    
    print(f"\nConfiguration:")
    print(f"  GCS Bucket: {gcs_bucket_name}")
    print(f"  GCS File: {gcs_file_path}")
    print(f"  BigQuery Project: {bigquery_project}")
    print(f"  BigQuery Dataset: {bigquery_dataset}")
    print(f"  Target Table: {table_name}")
    
    try:
        # Step 1: Load CSV from GCS
        print(f"\n{'='*80}")
        print("Step 1: Loading CSV from Google Cloud Storage")
        print(f"{'='*80}")
        df = load_csv_from_gcs(gcs_bucket_name, gcs_file_path)
        
        # Step 2: Load to BigQuery using Fivetran SDK
        print(f"\n{'='*80}")
        print("Step 2: Loading to BigQuery via Fivetran SDK")
        print(f"{'='*80}")
        load_to_bigquery_with_fivetran(df, table_name)
        
        # Step 3: Output as JSON lines (Fivetran standard output format)
        print(f"\n{'='*80}")
        print("Step 3: Output JSON Lines (Fivetran Format)")
        print(f"{'='*80}")
        output_json_lines(df)
        
        print(f"\n{'='*80}")
        print("✓ Connector Execution Complete!")
        print(f"{'='*80}")
        
    except Exception as e:
        print(f"\n{'='*80}")
        print(f"✗ Connector Failed: {e}")
        print(f"{'='*80}")
        sys.exit(1)

if __name__ == "__main__":
    main()
