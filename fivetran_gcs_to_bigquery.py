"""
Fivetran-style GCS to BigQuery Data Loader
Uses Fivetran SDK structure to load CSV data from GCS bucket to BigQuery
"""
import os
import sys
import json
import io
import pandas as pd
from google.cloud import storage, bigquery
from datetime import datetime

# Fivetran Configuration
FIVETRAN_API_KEY = "GovOjgyu2dCEF51Q"
FIVETRAN_API_SECRET = "EgwDk1ukUVCHcCc9NlFM7YBArPqbspdd"

# GCS Configuration
GCS_BUCKET_NAME = "fivetran-hackathon"

# BigQuery Configuration
BIGQUERY_PROJECT_ID = "hackathon-475722"
BIGQUERY_DATASET_ID = "test_fivetran"

class FivetranGCSConnector:
    """Custom Fivetran connector to load data from GCS to BigQuery"""
    
    def __init__(self, project_id, dataset_id):
        """Initialize the connector"""
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bq_client = bigquery.Client(project=project_id)
        self.gcs_client = storage.Client()
        
    def ensure_dataset_exists(self):
        """Create BigQuery dataset if it doesn't exist"""
        dataset_ref = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.bq_client.get_dataset(dataset_ref)
            print(f"✓ Dataset {self.dataset_id} exists")
        except Exception:
            print(f"→ Creating dataset {self.dataset_id}...")
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            self.bq_client.create_dataset(dataset)
            print(f"✓ Dataset {self.dataset_id} created")
    
    def load_csv_from_gcs(self, bucket_name, file_path):
        """
        Load CSV file from Google Cloud Storage
        
        Args:
            bucket_name: GCS bucket name
            file_path: Path to CSV file in bucket
            
        Returns:
            pandas DataFrame
        """
        print(f"\n📥 Loading CSV from GCS...")
        print(f"   Bucket: {bucket_name}")
        print(f"   File: {file_path}")
        
        try:
            bucket = self.gcs_client.bucket(bucket_name)
            blob = bucket.blob(file_path)
            
            # Download CSV content
            csv_content = blob.download_as_text()
            
            # Parse into DataFrame
            df = pd.read_csv(io.StringIO(csv_content))
            
            print(f"✓ Loaded {len(df)} rows, {len(df.columns)} columns")
            print(f"  Columns: {list(df.columns)}")
            
            return df
            
        except Exception as e:
            print(f"✗ Error loading from GCS: {e}")
            raise
    
    def load_to_bigquery(self, df, table_name, write_disposition='WRITE_APPEND'):
        """
        Load DataFrame to BigQuery table
        
        Args:
            df: pandas DataFrame
            table_name: Target table name
            write_disposition: WRITE_TRUNCATE, WRITE_APPEND, or WRITE_EMPTY
        """
        print(f"\n📤 Loading to BigQuery...")
        print(f"   Table: {self.project_id}.{self.dataset_id}.{table_name}")
        print(f"   Mode: {write_disposition}")
        
        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{table_name}"
            
            job_config = bigquery.LoadJobConfig(
                write_disposition=write_disposition,
                autodetect=True  # Auto-detect schema from DataFrame
            )
            
            job = self.bq_client.load_table_from_dataframe(
                df,
                table_ref,
                job_config=job_config
            )
            
            job.result()  # Wait for job to complete
            
            print(f"✓ Loaded {len(df)} rows to {table_name}")
            
            # Get table info
            table = self.bq_client.get_table(table_ref)
            print(f"  Total rows in table: {table.num_rows}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error loading to BigQuery: {e}")
            raise
    
    def output_fivetran_format(self, df):
        """
        Output data in Fivetran JSON lines format
        
        Args:
            df: pandas DataFrame to output
        """
        print(f"\n📋 Fivetran JSON Lines Output:")
        print("-" * 80)
        
        for idx, row in df.iterrows():
            record = row.to_dict()
            # Convert any datetime objects to strings
            for key, value in record.items():
                if pd.isna(value):
                    record[key] = None
                elif isinstance(value, (pd.Timestamp, datetime)):
                    record[key] = value.isoformat()
            
            print(json.dumps(record))
        
        print("-" * 80)
        print(f"✓ Output {len(df)} records")
    
    def sync(self, bucket_name, file_path, table_name, output_json=True):
        """
        Execute full sync operation from GCS to BigQuery
        
        Args:
            bucket_name: GCS bucket name
            file_path: Path to CSV file
            table_name: Target BigQuery table
            output_json: Whether to output JSON lines
        """
        print("=" * 80)
        print("🚀 Fivetran GCS → BigQuery Sync")
        print("=" * 80)
        
        # Ensure dataset exists
        self.ensure_dataset_exists()
        
        # Load data from GCS
        df = self.load_csv_from_gcs(bucket_name, file_path)
        
        # Load to BigQuery
        self.load_to_bigquery(df, table_name)
        
        # Output JSON lines (Fivetran standard)
        if output_json:
            self.output_fivetran_format(df)
        
        print("\n" + "=" * 80)
        print("✓ Sync Complete!")
        print("=" * 80)
        
        return df

def main():
    """Main function - can be called as Fivetran custom connector"""
    
    # Get configuration from environment variables or use defaults
    gcs_bucket = os.environ.get("GCS_BUCKET_NAME", GCS_BUCKET_NAME)
    gcs_file = os.environ.get("GCS_FILE_PATH", "subscriptions.csv")
    bq_project = os.environ.get("BIGQUERY_PROJECT_ID", BIGQUERY_PROJECT_ID)
    bq_dataset = os.environ.get("BIGQUERY_DATASET_ID", BIGQUERY_DATASET_ID)
    bq_table = os.environ.get("BIGQUERY_TABLE_NAME", "gcs_subscriptions")
    
    print("\n📋 Configuration:")
    print(f"   GCS Bucket: {gcs_bucket}")
    print(f"   GCS File: {gcs_file}")
    print(f"   BigQuery Project: {bq_project}")
    print(f"   BigQuery Dataset: {bq_dataset}")
    print(f"   BigQuery Table: {bq_table}")
    
    try:
        # Initialize connector
        connector = FivetranGCSConnector(
            project_id=bq_project,
            dataset_id=bq_dataset
        )
        
        # Execute sync
        df = connector.sync(
            bucket_name=gcs_bucket,
            file_path=gcs_file,
            table_name=bq_table,
            output_json=True
        )
        
        print(f"\n✅ Successfully synced {len(df)} records from GCS to BigQuery!")
        
    except Exception as e:
        print(f"\n❌ Sync failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
