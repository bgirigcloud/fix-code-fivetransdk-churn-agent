import joblib
import pandas as pd
import os

class ChurnPredictor:
    def __init__(self, model_path: str = './model/churn_model.joblib', feature_names_path: str = './model/feature_names.joblib'):
        self.model = joblib.load(model_path)
        self.feature_names = joblib.load(feature_names_path)

    def predict(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """Makes churn predictions on new data."""
        # Ensure the new data has the same columns as the training data
        # Missing columns will be filled with 0 (for one-hot encoded features) or mean/median (for numerical features)
        # This is a simplified approach; a more robust solution would handle missing features more carefully
        for col in self.feature_names:
            if col not in new_data.columns:
                new_data[col] = 0  # Or a more appropriate default/imputation
        
        # Reorder columns to match the training data
        new_data = new_data[self.feature_names]

        predictions = self.model.predict(new_data)
        probabilities = self.model.predict_proba(new_data)[:, 1]  # Probability of churn
        
        result_df = pd.DataFrame({
            'customer_id': new_data['customer_id'] if 'customer_id' in new_data.columns else range(len(new_data)),
            'churn_prediction': predictions,
            'churn_probability': probabilities
        })
        return result_df
