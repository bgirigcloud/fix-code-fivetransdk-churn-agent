import streamlit as st
import pandas as pd
from data_handler import get_churn_data, get_subscription_data, store_predictions
from model_trainer import train_model
from predictor import ChurnPredictor
import os

# --- Configuration --- #
PROJECT_ID = "hackathon-475722"
CHURN_DATASET_ID = "saas"
CHURN_TABLE_ID = "ravenstack_subscriptions"
SUBSCRIPTION_DATASET_ID = "saas"
SUBSCRIPTION_TABLE_ID = "ravenstack_subscriptions"
PREDICTIONS_DATASET_ID = "churn_predictions_dataset"
PREDICTIONS_TABLE_ID = "churn_predictions"

MODEL_PATH = './model/churn_model.joblib'
FEATURE_NAMES_PATH = './model/feature_names.joblib'

# --- Streamlit App --- #
st.title("Churn Prediction Agent")

st.sidebar.header("Actions")

# --- Train Model Section ---
if st.sidebar.button("Train New Model"):
    st.subheader("Training Churn Prediction Model...")
    try:
        # In a real scenario, you'd merge churn and subscription data here
        # For simplicity, let's assume get_churn_data returns the combined dataset for training
        # You might need to adjust get_churn_data or add a merge step here
        st.write(f"Using Project ID: {PROJECT_ID}")
        training_data = get_churn_data(PROJECT_ID, CHURN_DATASET_ID, CHURN_TABLE_ID)
        train_model(training_data, model_path=MODEL_PATH)
        st.success("Model trained successfully!")
    except Exception as e:
        st.error(f"Error during model training: {e}")

# --- Make Predictions Section ---
st.sidebar.header("Make Predictions")

prediction_mode = st.sidebar.radio(
    "Select Prediction Input Mode:",
    ("Manual Input", "Upload CSV")
)

predictor = None
if os.path.exists(MODEL_PATH) and os.path.exists(FEATURE_NAMES_PATH):
    try:
        predictor = ChurnPredictor(model_path=MODEL_PATH, feature_names_path=FEATURE_NAMES_PATH)
    except Exception as e:
        st.error(f"Error loading model: {e}. Please train a model first.")
else:
    st.warning("No trained model found. Please train a model first.")

if predictor:
    if prediction_mode == "Manual Input":
        st.subheader("Enter Customer Data for Prediction")
        # Placeholder for manual input fields - this will be extensive
        # For demonstration, let's just ask for a few key features
        st.write("Please provide values for the following features:")
        
        # Example manual inputs (you'll need to expand this based on your actual features)
        customer_id = st.text_input("Customer ID", "C12345")
        seats = st.number_input("Seats", min_value=0, value=1)
        mrr_amount = st.number_input("MRR Amount", min_value=0, value=50)
        arr_amount = st.number_input("ARR Amount", min_value=0, value=600)
        plan_tier = st.selectbox("Plan Tier", ['Basic', 'Standard', 'Premium']) # Example values, adjust as per your data
        is_trial = st.selectbox("Is Trial", [True, False])
        upgrade_flag = st.selectbox("Upgrade Flag", [True, False])
        downgrade_flag = st.selectbox("Downgrade Flag", [True, False])
        billing_frequency = st.selectbox("Billing Frequency", ['Monthly', 'Annually']) # Example values
        auto_renew_flag = st.selectbox("Auto Renew Flag", [True, False])

        # Create a DataFrame from manual input
        manual_input_data = pd.DataFrame({
            'customer_id': [customer_id],
            'seats': [seats],
            'mrr_amount': [mrr_amount],
            'arr_amount': [arr_amount],
            'plan_tier': [plan_tier],
            'is_trial': [is_trial],
            'upgrade_flag': [upgrade_flag],
            'downgrade_flag': [downgrade_flag],
            'billing_frequency': [billing_frequency],
            'auto_renew_flag': [auto_renew_flag],
        })

        if st.button("Predict Churn (Manual)"):
            try:
                predictions_df = predictor.predict(manual_input_data)
                st.write("### Prediction Results:")
                st.dataframe(predictions_df)
                
                if st.checkbox("Store Predictions in BigQuery?"):
                    store_predictions(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID, predictions_df)
                    st.success("Predictions stored in BigQuery.")
            except Exception as e:
                st.error(f"Error during manual prediction: {e}")

    elif prediction_mode == "Upload CSV":
        st.subheader("Upload CSV for Batch Prediction")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

        if uploaded_file is not None:
            try:
                df_to_predict = pd.read_csv(uploaded_file)
                st.write("### Uploaded Data Preview:")
                st.dataframe(df_to_predict.head())

                if st.button("Predict Churn (CSV)"):
                    predictions_df = predictor.predict(df_to_predict)
                    st.write("### Prediction Results:")
                    st.dataframe(predictions_df)

                    if st.checkbox("Store Predictions in BigQuery?"):
                        store_predictions(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID, predictions_df)
                        st.success("Predictions stored in BigQuery.")
            except Exception as e:
                st.error(f"Error during CSV prediction: {e}")


