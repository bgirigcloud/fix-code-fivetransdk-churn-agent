from google.cloud import storage, bigquery
import pandas as pd
import io
import os

class FivetranGcsToBigQuery:
    def __init__(self, project_id: str, dataset_id: str, bucket_name: str):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.bucket_name = bucket_name

        self.storage_client = storage.Client(project=project_id)
        self.bigquery_client = bigquery.Client(project=project_id)

    def list_gcs_files(self, prefix: str = None):
        """List all files in GCS bucket (optionally filtered by prefix)."""
        bucket = self.storage_client.bucket(self.bucket_name)
        return [blob.name for blob in bucket.list_blobs(prefix=prefix)]

    def load_csv_to_bq(self, gcs_path: str, table_name: str, write_disposition="WRITE_APPEND"):
        """Load CSV file from GCS → BigQuery."""
        uri = f"gs://{self.bucket_name}/{gcs_path}"
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
            autodetect=True,
            write_disposition=write_disposition,
        )

        load_job = self.bigquery_client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()  # Wait for job to complete

        print(f"✅ Loaded {uri} into {table_id}")

    def load_json_to_bq(self, gcs_path: str, table_name: str, write_disposition="WRITE_APPEND"):
        """Load JSON file from GCS → BigQuery."""
        uri = f"gs://{self.bucket_name}/{gcs_path}"
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"

        job_config = bigquery.LoadJobConfig(
            source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
            autodetect=True,
            write_disposition=write_disposition,
        )

        load_job = self.bigquery_client.load_table_from_uri(uri, table_id, job_config=job_config)
        load_job.result()

        print(f"✅ Loaded {uri} into {table_id}")

    def sync_all(self, prefix: str, table_name: str, file_type="csv"):
        """Sync all GCS files under a prefix into BigQuery (like Fivetran sync)."""
        files = self.list_gcs_files(prefix)
        if not files:
            print("⚠️ No files found in GCS prefix.")
            return

        for f in files:
            if file_type == "csv" and f.endswith(".csv"):
                self.load_csv_to_bq(f, table_name)
            elif file_type == "json" and f.endswith(".json"):
                self.load_json_to_bq(f, table_name)

        print(f"✅ Synced {len(files)} files to {table_name}")



from fivetran_gcs_bq_sdk import FivetranGcsToBigQuery

connector = FivetranGcsToBigQuery(
    project_id="hackathon-475722",
    dataset_id="hackathon-475722.test_fivetran",
    bucket_name="fivetran-hackathon"
)

# Sync all CSV files under /sales_data/
connector.sync_all(prefix="sales_data/", table_name="sales_raw", file_type="csv")
