"""
Test script to verify the churn prediction system works correctly.
"""
import pandas as pd
from predictor import ChurnPredictor

def test_predictor():
    print("=" * 60)
    print("Testing Churn Predictor")
    print("=" * 60)
    print()
    
    # Load the predictor
    print("1. Loading model...")
    try:
        predictor = ChurnPredictor()
        print("   ✓ Model loaded successfully")
    except Exception as e:
        print(f"   ✗ Failed to load model: {e}")
        return False
    
    # Create test data
    print()
    print("2. Creating test data...")
    test_data = pd.DataFrame({
        'customer_id': ['C001', 'C002', 'C003'],
        'seats': [5, 10, 1],
        'mrr_amount': [50, 100, 10],
        'arr_amount': [600, 1200, 120],
        'plan_tier': ['basic', 'premium', 'basic'],
        'is_trial': [0, 0, 1],
        'upgrade_flag': [0, 1, 0],
        'downgrade_flag': [0, 0, 0],
        'billing_frequency': ['monthly', 'annual', 'monthly'],
        'auto_renew_flag': [1, 1, 0]
    })
    print("   ✓ Test data created (3 samples)")
    
    # Test basic prediction
    print()
    print("3. Testing basic prediction...")
    try:
        result = predictor.predict(test_data)
        print("   ✓ Prediction successful")
        print()
        print("   Results:")
        print(result.to_string(index=False))
    except Exception as e:
        print(f"   ✗ Prediction failed: {e}")
        return False
    
    # Test prediction with explanations
    print()
    print("4. Testing prediction with explanations...")
    try:
        result_df, shap_explanation = predictor.predict_and_explain(test_data)
        print("   ✓ Prediction with explanations successful")
        print(f"   ✓ SHAP values shape: {shap_explanation.values.shape}")
    except Exception as e:
        print(f"   ✗ Prediction with explanations failed: {e}")
        return False
    
    print()
    print("=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    return True

if __name__ == '__main__':
    success = test_predictor()
    exit(0 if success else 1)
