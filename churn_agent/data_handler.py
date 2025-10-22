import pandas as pd
from google.cloud import bigquery

def get_churn_data(project_id: str, dataset_id: str, table_id: str) -> pd.DataFrame:
    client = bigquery.Client(project=project_id)
    query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_id}`"
    df = client.query(query).to_dataframe()
    return df

def get_subscription_data(project_id: str, dataset_id: str, table_id: str) -> pd.DataFrame:
    """Fetches subscription data from BigQuery."""
    client = bigquery.Client(project=project_id)
    query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_id}`"
    df = client.query(query).to_dataframe()
    return df

def store_predictions(project_id: str, dataset_id: str, table_id: str, predictions_df: pd.DataFrame):
    """Stores churn predictions in BigQuery."""
    client = bigquery.Client(project=project_id)
    table_ref = client.dataset(dataset_id).table(table_id)
    job_config = bigquery.LoadJobConfig(write_disposition="WRITE_APPEND")
    job = client.load_table_from_dataframe(predictions_df, table_ref, job_config=job_config)
    job.result()
    print(f"Stored {len(predictions_df)} predictions to {project_id}.{dataset_id}.{table_id}")
