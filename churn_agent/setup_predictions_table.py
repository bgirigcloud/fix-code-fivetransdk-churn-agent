"""
Script to create the churn_predictions dataset and table in BigQuery
"""
from google.cloud import bigquery
import sys

# Configuration
PROJECT_ID = "hackathon-475722"
DATASET_ID = "churn_predictions_dataset"
TABLE_ID = "churn_predictions"

def create_dataset_and_table():
    """Create the BigQuery dataset and predictions table if they don't exist"""
    
    print("=" * 80)
    print("Setting up BigQuery Predictions Storage")
    print("=" * 80)
    
    # Initialize BigQuery client
    try:
        client = bigquery.Client(project=PROJECT_ID)
        print(f"\n✓ Connected to BigQuery project: {PROJECT_ID}")
    except Exception as e:
        print(f"\n✗ Error connecting to BigQuery: {e}")
        print("\nMake sure:")
        print("1. key.json exists in the project root")
        print("2. GOOGLE_APPLICATION_CREDENTIALS environment variable is set")
        return False
    
    # Create dataset if it doesn't exist
    print(f"\n1. Checking dataset: {DATASET_ID}")
    dataset_ref = f"{PROJECT_ID}.{DATASET_ID}"
    
    try:
        dataset = client.get_dataset(dataset_ref)
        print(f"   ✓ Dataset '{DATASET_ID}' already exists")
    except Exception:
        print(f"   → Creating dataset '{DATASET_ID}'...")
        try:
            dataset = bigquery.Dataset(dataset_ref)
            dataset.location = "US"
            dataset = client.create_dataset(dataset, timeout=30)
            print(f"   ✓ Dataset '{DATASET_ID}' created successfully")
        except Exception as e:
            print(f"   ✗ Error creating dataset: {e}")
            return False
    
    # Create table if it doesn't exist
    print(f"\n2. Checking table: {TABLE_ID}")
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    
    try:
        table = client.get_table(table_ref)
        print(f"   ✓ Table '{TABLE_ID}' already exists")
        print(f"   → Schema: {[f.name for f in table.schema]}")
    except Exception:
        print(f"   → Creating table '{TABLE_ID}'...")
        try:
            # Define schema for predictions table
            schema = [
                bigquery.SchemaField("prediction_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("prediction_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("account_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("subscription_id", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("churn_probability", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("churn_prediction", "BOOLEAN", mode="REQUIRED"),
                bigquery.SchemaField("plan_tier", "STRING", mode="NULLABLE"),
                bigquery.SchemaField("mrr_amount", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("seats", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("is_trial", "BOOLEAN", mode="NULLABLE"),
                bigquery.SchemaField("model_version", "STRING", mode="NULLABLE"),
            ]
            
            table = bigquery.Table(table_ref, schema=schema)
            table = client.create_table(table)
            print(f"   ✓ Table '{TABLE_ID}' created successfully")
            print(f"   → Schema: {[f.name for f in table.schema]}")
        except Exception as e:
            print(f"   ✗ Error creating table: {e}")
            return False
    
    print("\n" + "=" * 80)
    print("✓ Setup Complete!")
    print("=" * 80)
    print(f"\nPredictions will be stored in:")
    print(f"  Project: {PROJECT_ID}")
    print(f"  Dataset: {DATASET_ID}")
    print(f"  Table: {TABLE_ID}")
    print(f"  Full path: {table_ref}")
    
    return True

if __name__ == "__main__":
    success = create_dataset_and_table()
    sys.exit(0 if success else 1)
