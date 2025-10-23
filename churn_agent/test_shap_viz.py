"""
Test SHAP visualization to ensure it works correctly.
"""
import pandas as pd
from predictor import ChurnPredictor
import shap
import matplotlib.pyplot as plt

def test_shap_visualization():
    print("Testing SHAP Visualization...")
    print("=" * 60)
    
    # Load predictor
    predictor = ChurnPredictor()
    
    # Create single test sample
    test_data = pd.DataFrame({
        'customer_id': ['C001'],
        'seats': [5],
        'mrr_amount': [50],
        'arr_amount': [600],
        'plan_tier': ['basic'],
        'is_trial': [1],
        'upgrade_flag': [0],
        'downgrade_flag': [0],
        'billing_frequency': ['monthly'],
        'auto_renew_flag': [1]
    })
    
    print("Making prediction with SHAP explanation...")
    predictions_df, shap_explanation = predictor.predict_and_explain(test_data)
    
    print("✓ Prediction successful")
    print(f"  Customer: {predictions_df['customer_id'].iloc[0]}")
    print(f"  Churn Prediction: {predictions_df['churn_prediction'].iloc[0]}")
    print(f"  Churn Probability: {predictions_df['churn_probability'].iloc[0]:.4f}")
    print()
    
    print(f"SHAP Explanation Details:")
    print(f"  Values shape: {shap_explanation.values.shape}")
    print(f"  Base value: {shap_explanation.base_values}")
    print(f"  Feature names: {len(shap_explanation.feature_names)} features")
    print()
    
    # Test waterfall plot
    print("Creating waterfall plot...")
    try:
        fig, ax = plt.subplots(figsize=(10, 4))
        shap.plots.waterfall(shap_explanation[0], show=False)
        plt.savefig('./test_waterfall.png', bbox_inches='tight', dpi=150)
        plt.close()
        print("✓ Waterfall plot created successfully (saved as test_waterfall.png)")
    except Exception as e:
        print(f"✗ Waterfall plot failed: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✓ SHAP VISUALIZATION TEST PASSED!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_shap_visualization()
    exit(0 if success else 1)
