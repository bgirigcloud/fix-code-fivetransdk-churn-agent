import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

# Placeholder for feature columns - these will need to be defined based on actual data
NUMERIC_FEATURES = ['seats', 'mrr_amount', 'arr_amount']
CATEGORICAL_FEATURES = ['plan_tier', 'is_trial', 'upgrade_flag', 'downgrade_flag', 'billing_frequency', 'auto_renew_flag']
TARGET_FEATURE = 'churn_flag'

def train_model(data: pd.DataFrame, model_path: str = 'churn_model.joblib'):
    """Trains a logistic regression model and saves it."""
    X = data.drop(columns=[TARGET_FEATURE])
    y = data[TARGET_FEATURE]

    # Identify actual numeric and categorical features present in the data
    actual_numeric_features = [f for f in NUMERIC_FEATURES if f in X.columns]
    actual_categorical_features = [f for f in CATEGORICAL_FEATURES if f in X.columns]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), actual_numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), actual_categorical_features)
        ])

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(solver='liblinear'))
    ])

    model.fit(X, y)
    joblib.dump(model, model_path)
    print(f"Model trained and saved to {model_path}")

    # Also save the list of features used for training
    feature_names = actual_numeric_features + actual_categorical_features
    joblib.dump(feature_names, os.path.join(os.path.dirname(model_path), 'feature_names.joblib'))
    print(f"Feature names saved to {os.path.join(os.path.dirname(model_path), 'feature_names.joblib')}")


if __name__ == '__main__':
    # This is a placeholder for demonstration. In a real scenario, you'd fetch data from BigQuery.
    # For now, let's create some dummy data.
    dummy_data = pd.DataFrame({
        'customer_id': range(100),
        'tenure': [i for i in range(1, 101)],
        'monthly_charges': [10.0 + i for i in range(100)],
        'total_charges': [100.0 + i*10 for i in range(100)],
        'gender': ['Male' if i % 2 == 0 else 'Female' for i in range(100)],
        'senior_citizen': [0 if i % 3 == 0 else 1 for i in range(100)],
        'partner': ['Yes' if i % 4 == 0 else 'No' for i in range(100)],
        'dependents': ['Yes' if i % 5 == 0 else 'No' for i in range(100)],
        'phone_service': ['Yes' for i in range(100)],
        'multiple_lines': ['No' if i % 2 == 0 else 'Yes' for i in range(100)],
        'internet_service': ['DSL' if i % 3 == 0 else 'Fiber optic' for i in range(100)],
        'online_security': ['No' if i % 2 == 0 else 'Yes' for i in range(100)],
        'online_backup': ['Yes' if i % 3 == 0 else 'No' for i in range(100)],
        'device_protection': ['No' if i % 4 == 0 else 'Yes' for i in range(100)],
        'tech_support': ['Yes' if i % 5 == 0 else 'No' for i in range(100)],
        'streaming_tv': ['No' if i % 2 == 0 else 'Yes' for i in range(100)],
        'streaming_movies': ['Yes' if i % 3 == 0 else 'No' for i in range(100)],
        'contract': ['Month-to-month' if i % 2 == 0 else 'Two year' for i in range(100)],
        'paperless_billing': ['Yes' for i in range(100)],
        'payment_method': ['Electronic check' if i % 2 == 0 else 'Mailed check' for i in range(100)],
        'churn': [0 if i % 7 == 0 else 1 for i in range(100)] # Example churn data
    })
    train_model(dummy_data, model_path='./model/churn_model.joblib')
