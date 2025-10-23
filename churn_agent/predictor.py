import joblib
import pandas as pd
import numpy as np
import shap

class ChurnPredictor:
    def __init__(self, model_path: str = './model/churn_model.joblib', **kwargs):
        """
        Initializes the ChurnPredictor.

        Args:
            model_path (str): Path to the trained model file.
        """
        self.model = joblib.load(model_path)

    def predict(self, new_data: pd.DataFrame) -> pd.DataFrame:
        """
        Makes churn predictions on new data.

        Args:
            new_data (pd.DataFrame): DataFrame with customer data.

        Returns:
            pd.DataFrame: DataFrame with customer_id, churn_prediction, and churn_probability.
        """
        predictions = self.model.predict(new_data)
        proba = self.model.predict_proba(new_data)
        
        # Handle cases where model might only have one class
        if proba.shape[1] == 1:
            # Only one class predicted, use that probability
            probabilities = proba[:, 0]
        else:
            # Normal case: get probability of positive class (churn)
            probabilities = proba[:, 1]

        result_df = pd.DataFrame({
            'customer_id': new_data['customer_id'] if 'customer_id' in new_data.columns else range(len(new_data)),
            'churn_prediction': predictions,
            'churn_probability': probabilities
        })
        return result_df

    def predict_and_explain(self, new_data: pd.DataFrame):
        """
        Makes churn predictions and generates SHAP explanations.

        Args:
            new_data (pd.DataFrame): DataFrame with customer data.

        Returns:
            tuple: A tuple containing:
                - pd.DataFrame: DataFrame with predictions.
                - shap.Explanation: SHAP explanation object.
        """
        predictions = self.model.predict(new_data)
        proba = self.model.predict_proba(new_data)
        
        # Handle cases where model might only have one class
        if proba.shape[1] == 1:
            # Only one class predicted, use that probability
            probabilities = proba[:, 0]
        else:
            # Normal case: get probability of positive class (churn)
            probabilities = proba[:, 1]

        predictions_df = pd.DataFrame({
            'customer_id': new_data['customer_id'] if 'customer_id' in new_data.columns else range(len(new_data)),
            'churn_prediction': predictions,
            'churn_probability': probabilities
        })

        preprocessor = self.model.named_steps['preprocessor']
        classifier = self.model.named_steps['classifier']
        
        transformed_data = preprocessor.transform(new_data)
        if hasattr(transformed_data, "toarray"):
            transformed_data = transformed_data.toarray()

        feature_names = preprocessor.get_feature_names_out()

        # Use KernelExplainer for generic pipelines
        if transformed_data.shape[0] > 1:
            background_data = shap.kmeans(transformed_data, min(10, transformed_data.shape[0]))
        else:
            background_data = transformed_data
        
        explainer = shap.KernelExplainer(classifier.predict_proba, background_data)
        
        shap_values = explainer.shap_values(transformed_data)

        # Handle different SHAP value formats
        # For binary classification, shap_values can be:
        # 1. A list of 2 arrays: [negative_class_values, positive_class_values]
        # 2. A 3D array: (n_samples, n_features, n_classes)
        # 3. A 2D array: (n_samples, n_features) - for single output
        
        if isinstance(shap_values, list):
            # List format: take the positive class (index 1)
            if len(shap_values) > 1:
                shap_values_churn = shap_values[1]
                base_value_churn = explainer.expected_value[1] if isinstance(explainer.expected_value, (list, tuple, np.ndarray)) else explainer.expected_value
            else:
                shap_values_churn = shap_values[0]
                base_value_churn = explainer.expected_value[0] if isinstance(explainer.expected_value, (list, tuple, np.ndarray)) else explainer.expected_value
        elif len(shap_values.shape) == 3:
            # 3D array format: (n_samples, n_features, n_classes)
            # Take the positive class (last dimension, index 1)
            shap_values_churn = shap_values[:, :, 1]
            base_value_churn = explainer.expected_value[1] if isinstance(explainer.expected_value, (list, tuple, np.ndarray)) and len(explainer.expected_value) > 1 else explainer.expected_value
        else:
            # 2D array format: (n_samples, n_features)
            shap_values_churn = shap_values
            base_value_churn = explainer.expected_value if not isinstance(explainer.expected_value, (list, tuple, np.ndarray)) else explainer.expected_value[0]

        # Ensure base_value is a scalar
        if isinstance(base_value_churn, (list, tuple, np.ndarray)):
            base_value_churn = float(base_value_churn[0]) if len(base_value_churn) > 0 else 0.0
        
        # Create Explanation object for the positive class (churn)
        shap_explanation = shap.Explanation(
            values=shap_values_churn,
            base_values=base_value_churn,
            data=transformed_data,
            feature_names=feature_names
        )

        return predictions_df, shap_explanation