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
    # Ensure the model directory exists
    model_dir = os.path.dirname(model_path)
    if model_dir and not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    X = data.drop(columns=[TARGET_FEATURE])
    y = data[TARGET_FEATURE]

    # Identify actual numeric and categorical features present in the data
    actual_numeric_features = [f for f in NUMERIC_FEATURES if f in X.columns]
    actual_categorical_features = [f for f in CATEGORICAL_FEATURES if f in X.columns]

    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), actual_numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), actual_categorical_features)
        ],
        remainder='drop'  # Explicitly drop other columns
    )

    model = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(solver='liblinear', max_iter=1000))
    ])

    model.fit(X, y)
    
    # Save with protocol 5 for better compatibility
    joblib.dump(model, model_path, compress=3)
    
    # Also save feature names for reference
    feature_names_path = model_path.replace('.joblib', '_features.joblib')
    joblib.dump({
        'numeric_features': actual_numeric_features,
        'categorical_features': actual_categorical_features
    }, feature_names_path)
    
    print(f"Model trained and saved to {model_path}")
    print(f"Feature names saved to {feature_names_path}")
    
    return model



if __name__ == '__main__':
    # This is a placeholder for demonstration. In a real scenario, you'd fetch data from BigQuery.
    # For now, let's create some dummy data.
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
    
    print(f"Training model with {len(dummy_data)} samples...")
    model = train_model(dummy_data, model_path='./model/churn_model.joblib')
    print("Training complete!")
