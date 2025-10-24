"""
Check if predictions table has data
"""
from google.cloud import bigquery
import pandas as pd

PROJECT_ID = "hackathon-475722"
DATASET_ID = "churn_predictions_dataset"
TABLE_ID = "churn_predictions"

def check_predictions_data():
    print("=" * 80)
    print("Checking Predictions Table Data")
    print("=" * 80)
    
    try:
        client = bigquery.Client(project=PROJECT_ID)
        table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
        
        # Check table exists
        print(f"\n1. Checking table: {table_ref}")
        table = client.get_table(table_ref)
        print(f"   ✓ Table exists")
        print(f"   Schema: {[f.name for f in table.schema]}")
        
        # Count rows
        print(f"\n2. Counting rows...")
        count_query = f"SELECT COUNT(*) as count FROM `{table_ref}`"
        result = client.query(count_query).to_dataframe()
        row_count = result['count'].iloc[0]
        print(f"   Row count: {row_count}")
        
        if row_count == 0:
            print("\n   ⚠ Table is EMPTY - No predictions have been stored yet")
            print("\n   To add predictions:")
            print("   1. Go to Streamlit app")
            print("   2. Make predictions (Manual/CSV/Real-time)")
            print("   3. Check 'Store Predictions in BigQuery'")
            print("   4. Click the store button")
        else:
            print(f"\n   ✓ Table has {row_count} predictions")
            print(f"\n3. Sample data (first 5 rows):")
            query = f"SELECT * FROM `{table_ref}` LIMIT 5"
            df = client.query(query).to_dataframe()
            print(df.to_string())
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False
    
    print("\n" + "=" * 80)
    return True

if __name__ == "__main__":
    check_predictions_data()
