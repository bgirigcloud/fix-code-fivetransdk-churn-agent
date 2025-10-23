"""
Simulate the exact Streamlit manual prediction workflow.
"""
import pandas as pd
from predictor import ChurnPredictor
import shap
import matplotlib.pyplot as plt

def simulate_streamlit_manual_prediction():
    print("=" * 60)
    print("Simulating Streamlit Manual Prediction Workflow")
    print("=" * 60)
    print()
    
    # Simulate the exact data structure from Streamlit form
    print("1. Creating manual input data (like Streamlit form)...")
    manual_input_data = pd.DataFrame({
        'customer_id': ['C12345'],
        'seats': [1],
        'mrr_amount': [50],
        'arr_amount': [600],
        'is_trial': [1],  # True = 1
        'upgrade_flag': [1],  # True = 1
        'downgrade_flag': [1],  # True = 1
        'auto_renew_flag': [1],  # True = 1
    })
    manual_input_data['plan_tier'] = 'basic'
    manual_input_data['billing_frequency'] = 'monthly'
    
    print("   ✓ Data created")
    print(f"   Columns: {list(manual_input_data.columns)}")
    print()
    
    # Load predictor
    print("2. Loading predictor...")
    predictor = ChurnPredictor(model_path='./model/churn_model.joblib')
    print("   ✓ Model loaded")
    print()
    
    # Make prediction with explanation
    print("3. Making prediction with explanations...")
    try:
        predictions_df, shap_explanation = predictor.predict_and_explain(manual_input_data)
        print("   ✓ Prediction successful")
        print()
        
        print("   Prediction Results:")
        print(f"     Customer ID: {predictions_df['customer_id'].iloc[0]}")
        print(f"     Churn Prediction: {predictions_df['churn_prediction'].iloc[0]}")
        print(f"     Churn Probability: {predictions_df['churn_probability'].iloc[0]:.4f}")
        print()
        
    except Exception as e:
        print(f"   ✗ Prediction failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Create visualization (like Streamlit does)
    print("4. Creating SHAP waterfall visualization...")
    try:
        fig, ax = plt.subplots(figsize=(10, 4))
        shap.plots.waterfall(shap_explanation[0], show=False)
        plt.savefig('./streamlit_simulation_waterfall.png', bbox_inches='tight', dpi=150)
        plt.close()
        print("   ✓ Waterfall plot created (saved as streamlit_simulation_waterfall.png)")
    except Exception as e:
        print(f"   ✗ Visualization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print()
    print("=" * 60)
    print("✓ SUCCESS! Streamlit workflow simulation passed.")
    print("  The app should now work correctly.")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = simulate_streamlit_manual_prediction()
    exit(0 if success else 1)
