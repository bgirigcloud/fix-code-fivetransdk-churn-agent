"""
Quick script to train the churn prediction model
"""
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from data_handler import get_churn_data
from model_trainer import train_model

# Configuration
PROJECT_ID = "hackathon-475722"
DATASET_ID = "saas"
TABLE_ID = "ravenstack_subscriptions"
MODEL_PATH = './model/churn_model.joblib'

def main():
    print("=" * 80)
    print("Training Churn Prediction Model")
    print("=" * 80)
    
    print(f"\n1. Fetching data from BigQuery...")
    print(f"   Project: {PROJECT_ID}")
    print(f"   Dataset: {DATASET_ID}")
    print(f"   Table: {TABLE_ID}")
    
    try:
        training_data = get_churn_data(PROJECT_ID, DATASET_ID, TABLE_ID)
        print(f"   ✓ Fetched {len(training_data)} rows")
        print(f"   ✓ Columns: {list(training_data.columns)}")
    except Exception as e:
        print(f"   ✗ Error fetching data: {e}")
        return
    
    print(f"\n2. Training model...")
    print(f"   Model will be saved to: {MODEL_PATH}")
    
    try:
        model = train_model(training_data, model_path=MODEL_PATH)
        print(f"   ✓ Model trained successfully!")
        print(f"   ✓ Model saved to: {MODEL_PATH}")
        print(f"   ✓ Feature names saved to: ./model/feature_names.joblib")
    except Exception as e:
        print(f"   ✗ Error training model: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("✓ Training Complete!")
    print("=" * 80)
    print("\nYou can now:")
    print("1. Refresh your Streamlit app")
    print("2. Make predictions using the trained model")
    print("3. Use the Natural Language Query interface")

if __name__ == "__main__":
    main()
