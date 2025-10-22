from google.cloud import bigquery
import os

project_id = "hackathon-475722"
dataset_id = "saas"
table_id = "ravenstack_subscriptions" # Or any other table

print(f"Attempting to connect to project: {project_id}")

try:
    client = bigquery.Client(project=project_id)
    # Try to list tables to confirm connection
    dataset_ref = client.dataset(dataset_id)
    tables = list(client.list_tables(dataset_ref))
    print(f"Successfully connected to BigQuery. Tables in {dataset_id}: {[t.table_id for t in tables]}")
except Exception as e:
    print(f"Error connecting to BigQuery: {e}")
