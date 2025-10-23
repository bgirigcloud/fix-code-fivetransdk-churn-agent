import pandas as pd
from google.cloud import bigquery
import os
from typing import Optional

def get_churn_data(project_id: str, dataset_id: str, table_id: str) -> pd.DataFrame:
    """
    Fetch churn data from BigQuery with fallback to local cache.
    
    Args:
        project_id: GCP project ID
        dataset_id: BigQuery dataset ID
        table_id: BigQuery table ID
        
    Returns:
        DataFrame with churn data
    """
    # Check for local cache first
    local_cache_path = './data/predictions_cache.csv'
    
    try:
        # Try BigQuery first
        client = bigquery.Client(project=project_id)
        query = f"SELECT * FROM `{project_id}.{dataset_id}.{table_id}` LIMIT 1000"
        df = client.query(query).to_dataframe()
        
        # Save to cache for future use
        os.makedirs('./data', exist_ok=True)
        df.to_csv(local_cache_path, index=False)
        return df
        
    except Exception as e:
        # Fall back to local cache
        if os.path.exists(local_cache_path):
            print(f"Using local cache due to BigQuery error: {e}")
            return pd.read_csv(local_cache_path)
        else:
            # Return sample data for demo
            print("No BigQuery access and no local cache. Using sample data.")
            return _get_sample_predictions()

def _get_sample_predictions() -> pd.DataFrame:
    """Generate sample prediction data for demo purposes."""
    import numpy as np
    np.random.seed(42)
    n_samples = 50
    
    return pd.DataFrame({
        'customer_id': [f'C{i:05d}' for i in range(n_samples)],
        'churn_prediction': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'churn_probability': np.random.beta(2, 5, n_samples),
        'plan_tier': np.random.choice(['basic', 'standard', 'premium'], n_samples),
        'is_trial': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'auto_renew_flag': np.random.choice([0, 1], n_samples, p=[0.3, 0.7]),
        'mrr_amount': np.random.uniform(10, 500, n_samples),
        'seats': np.random.randint(1, 20, n_samples),
        'billing_frequency': np.random.choice(['monthly', 'annual'], n_samples)
    })

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
