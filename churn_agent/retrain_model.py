"""
Standalone script to retrain the churn prediction model.
Run this to fix model compatibility issues.
"""
import os
import sys

# Add the parent directory to the path if needed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from model_trainer import train_model
import pandas as pd

def main():
    print("=" * 60)
    print("Churn Model Retraining Script")
    print("=" * 60)
    print()
    
    # Create dummy training data
    print("Creating dummy training data...")
    dummy_data = pd.DataFrame({
        'seats': [5, 10, 1, 20, 15] * 20,
        'mrr_amount': [50, 100, 10, 200, 150] * 20,
        'arr_amount': [600, 1200, 120, 2400, 1800] * 20,
        'plan_tier': ['basic', 'premium', 'basic', 'standard', 'premium'] * 20,
        'is_trial': [0, 0, 1, 0, 0] * 20,
        'upgrade_flag': [0, 1, 0, 0, 1] * 20,
        'downgrade_flag': [0, 0, 0, 1, 0] * 20,
        'billing_frequency': ['monthly', 'annual', 'monthly', 'annual', 'monthly'] * 20,
        'auto_renew_flag': [1, 1, 0, 1, 1] * 20,
        'churn_flag': [0, 1, 0, 1, 0] * 20
    })
    
    print(f"✓ Created {len(dummy_data)} training samples")
    print()
    
    # Ensure model directory exists
    model_dir = './model'
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
        print(f"✓ Created model directory: {model_dir}")
    
    # Train the model
    print("Training model...")
    print()
    model_path = './model/churn_model.joblib'
    
    try:
        model = train_model(dummy_data, model_path=model_path)
        print()
        print("=" * 60)
        print("✓ SUCCESS! Model has been retrained and saved.")
        print(f"  Model path: {os.path.abspath(model_path)}")
        print()
        print("You can now restart your Streamlit app and the model should load correctly.")
        print("=" * 60)
        return 0
    except Exception as e:
        print()
        print("=" * 60)
        print(f"✗ ERROR: Failed to train model")
        print(f"  Error: {e}")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
