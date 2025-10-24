"""
Create sample predictions and store them in BigQuery
"""
import pandas as pd
from google.cloud import bigquery
from datetime import datetime
import uuid

PROJECT_ID = "hackathon-475722"
DATASET_ID = "churn_predictions_dataset"
TABLE_ID = "churn_predictions"

def create_sample_predictions():
    """Create sample predictions data and store in BigQuery"""
    
    print("=" * 80)
    print("Creating Sample Predictions")
    print("=" * 80)
    
    # Create sample predictions
    print("\n1. Generating sample predictions...")
    
    # Generate realistic sample data
    sample_data = []
    for i in range(50):
        customer_id = f"CUST_{i+1:04d}"
        # Mix of low, medium, high risk customers
        if i < 20:
            churn_prob = 0.2 + (i * 0.01)  # Low risk
        elif i < 35:
            churn_prob = 0.4 + (i * 0.01)  # Medium risk
        else:
            churn_prob = 0.7 + (i * 0.01)  # High risk
        
        churn_prediction = churn_prob > 0.5
        
        sample_data.append({
            'customer_id': customer_id,
            'churn_prediction': churn_prediction,
            'churn_probability': churn_prob
        })
    
    predictions_df = pd.DataFrame(sample_data)
    print(f"   ✓ Generated {len(predictions_df)} sample predictions")
    print(f"   → Low risk (< 0.4): {len(predictions_df[predictions_df['churn_probability'] < 0.4])}")
    print(f"   → Medium risk (0.4-0.7): {len(predictions_df[(predictions_df['churn_probability'] >= 0.4) & (predictions_df['churn_probability'] < 0.7)])}")
    print(f"   → High risk (>= 0.7): {len(predictions_df[predictions_df['churn_probability'] >= 0.7])}")
    
    # Store in BigQuery
    print(f"\n2. Storing predictions in BigQuery...")
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND"
        )
        
        job = client.load_table_from_dataframe(
            predictions_df, 
            table_ref, 
            job_config=job_config
        )
        job.result()  # Wait for completion
        
        print(f"   ✓ Stored {len(predictions_df)} predictions to BigQuery")
        print(f"   → Table: {table_ref}")
        
    except Exception as e:
        print(f"   ✗ Error storing predictions: {e}")
        return False
    
    # Verify
    print(f"\n3. Verifying data...")
    try:
        count_query = f"SELECT COUNT(*) as count FROM `{table_ref}`"
        result = client.query(count_query).to_dataframe()
        row_count = result['count'].iloc[0]
        print(f"   ✓ Table now has {row_count} rows")
    except Exception as e:
        print(f"   ✗ Error verifying: {e}")
    
    print("\n" + "=" * 80)
    print("✓ Sample Predictions Created!")
    print("=" * 80)
    print("\nYou can now:")
    print("1. Refresh your Streamlit app")
    print("2. Try 'Augmented Analytics' questions")
    print("3. Use the NL-to-SQL interface")
    print("\nExample questions:")
    print("- Show me high-risk customers")
    print("- How many customers are predicted to churn?")
    print("- What is the average churn probability?")
    
    return True

if __name__ == "__main__":
    create_sample_predictions()
