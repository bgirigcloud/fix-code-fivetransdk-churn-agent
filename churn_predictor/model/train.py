"""
This script connects to BigQuery, loads the churn and subscriptions data,
trains a logistic regression model to predict churn, and saves the model.
"""

import os
from google.cloud import bigquery
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import joblib

# --- Configuration ---
PROJECT_ID = "hackathon-475722"
DATASET_ID = "saas"
SUBSCRIPTIONS_TABLE_ID = "ravenstack_subscriptions"
ACCOUNTS_TABLE_ID = "ravenstack_accounts"
MODEL_DIR = "/Users/projects/fivetransdk/churn_predictor/model"
MODEL_PATH = os.path.join(MODEL_DIR, "churn_model.joblib")

def load_data_from_bigquery(project_id, dataset_id, subscriptions_table_id, accounts_table_id):
    """Loads and merges subscriptions and accounts data from BigQuery."""
    client = bigquery.Client(project=project_id)
    
    query = f"""
    SELECT
        s.plan_tier,
        s.seats,
        s.mrr_amount,
        a.industry,
        a.country,
        s.churn_flag
    FROM
        `{project_id}.{dataset_id}.{subscriptions_table_id}` AS s
    JOIN
        `{project_id}.{dataset_id}.{accounts_table_id}` AS a
    ON
        s.account_id = a.account_id
    """
    
    try:
        df = client.query(query).to_dataframe()
        return df
    except Exception as e:
        print(f"Error loading data from BigQuery: {e}")
        return None

def train_and_save_model(df):
    """Trains a logistic regression model and saves it."""
    if df is None:
        print("DataFrame is None. Cannot train model.")
        return

    # --- Feature Engineering and Preprocessing ---
    # This is a simple example. You may need more complex feature engineering.
    df['churn_flag'] = df['churn_flag'].astype(int)
    df = pd.get_dummies(df, columns=['plan_tier', 'industry', 'country'], drop_first=True)

    # --- Model Training ---
    X = df.drop("churn_flag", axis=1)
    y = df["churn_flag"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = LogisticRegression()
    model.fit(X_train, y_train)
    
    # --- Save Model ---
    if not os.path.exists(MODEL_DIR):
        os.makedirs(MODEL_DIR)
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")

def get_distinct_values(project_id, dataset_id, table_id, column_name):
    """Gets distinct values for a column from a BigQuery table."""
    client = bigquery.Client(project=project_id)
    query = f"""
    SELECT DISTINCT {column_name}
    FROM `{project_id}.{dataset_id}.{table_id}`
    """
    try:
        query_job = client.query(query)
        results = query_job.result()
        return [row[0] for row in results]
    except Exception as e:
        print(f"Error getting distinct values: {e}")
        return []

if __name__ == "__main__":
    plan_tiers = get_distinct_values(PROJECT_ID, DATASET_ID, SUBSCRIPTIONS_TABLE_ID, "plan_tier")
    industries = get_distinct_values(PROJECT_ID, DATASET_ID, ACCOUNTS_TABLE_ID, "industry")
    countries = get_distinct_values(PROJECT_ID, DATASET_ID, ACCOUNTS_TABLE_ID, "country")
    
    print("Distinct Plan Tiers:", plan_tiers)
    print("Distinct Industries:", industries)
    print("Distinct Countries:", countries)

    # Load data
    data = load_data_from_bigquery(PROJECT_ID, DATASET_ID, SUBSCRIPTIONS_TABLE_ID, ACCOUNTS_TABLE_ID)
    
    # Train and save model
    train_and_save_model(data)