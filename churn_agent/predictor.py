import joblib
import pandas as pd
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
        probabilities = self.model.predict_proba(new_data)[:, 1]  # Probability of churn

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
        probabilities = self.model.predict_proba(new_data)[:, 1]

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

        # For binary classification, shap_values is a list of two arrays.
        # We take the values for the positive class (churn).
        shap_values_churn = shap_values[1]

        # expected_value is also an array with two values.
        base_value_churn = explainer.expected_value[1]

        # Create a simple Explanation object for the positive class
        shap_explanation = shap.Explanation(
            values=shap_values_churn,
            base_values=base_value_churn,
            data=transformed_data,
            feature_names=feature_names
        )

        return predictions_df, shap_explanation