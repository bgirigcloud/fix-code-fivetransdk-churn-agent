import streamlit as st
import joblib
import pandas as pd
import os

# --- Configuration ---
MODEL_PATH = "/Users/projects/fivetransdk/churn_predictor/model/churn_model.joblib"

# --- Load Model ---
@st.cache_resource
def load_model(path):
    """Loads the trained model."""
    if not os.path.exists(path):
        return None
    return joblib.load(path)

model = load_model(MODEL_PATH)

# --- App ---
st.title("Churn Prediction Agent")

st.info("**Note:** Before running the app, please ensure you have trained the model by running the `train.py` script in the `churn_predictor/model` directory. You will need to provide your GCP project ID, dataset ID, and table names in the script.")

if model is None:
    st.error("Model not found. Please train the model first.")
else:
    st.header("Predict Churn")
    
    # --- User Input ---
    plan_type = st.selectbox("Plan Type", ["Basic", "Premium", "Standard"])
    monthly_charge = st.number_input("Monthly Charge", min_value=0.0, value=50.0)
    tenure = st.number_input("Tenure (months)", min_value=0, value=12)
    
    if st.button("Predict"):
        # --- Preprocess Input ---
        # Create a dataframe with the same columns as the training data
        # The model expects one-hot encoded columns for 'plan_type'
        input_data = pd.DataFrame({
            'monthly_charge': [monthly_charge],
            'tenure': [tenure],
            'plan_type_Premium': [1 if plan_type == 'Premium' else 0],
            'plan_type_Standard': [1 if plan_type == 'Standard' else 0]
        })
        
        # --- Predict ---
        prediction = model.predict_proba(input_data)[:, 1]
        churn_probability = prediction[0]
        
        # --- Display Result ---
        st.subheader("Prediction")
        st.write(f"The probability of churn is: {churn_probability:.2f}")
        
        if churn_probability > 0.5:
            st.warning("This customer is likely to churn.")
        else:
            st.success("This customer is not likely to churn.")