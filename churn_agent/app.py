import streamlit as st
import pandas as pd
from data_handler import get_churn_data, get_subscription_data, store_predictions
from model_trainer import train_model
from predictor import ChurnPredictor
import os
import matplotlib.pyplot as plt
import shap

# --- Configuration --- #
PROJECT_ID = "hackathon-475722"
CHURN_DATASET_ID = "saas"
CHURN_TABLE_ID = "ravenstack_subscriptions"
SUBSCRIPTION_DATASET_ID = "saas"
SUBSCRIPTION_TABLE_ID = "ravenstack_subscriptions"
PREDICTIONS_DATASET_ID = "churn_predictions_dataset"
PREDICTIONS_TABLE_ID = "churn_predictions"

MODEL_PATH = './model/churn_model.joblib'

def take_action(predictions_df):
    st.subheader("Agentic Actions")
    high_risk_customers = predictions_df[predictions_df['churn_probability'] > 0.75]

    if not high_risk_customers.empty:
        st.write("High-risk customers identified. Suggested actions:")
        for index, row in high_risk_customers.iterrows():
            st.write(f"- **Customer {row['customer_id']}**: High churn probability ({row['churn_probability']:.2f}).")
            st.write("  - Action: Send a personalized retention email.")
            st.write("  - Action: Offer a 10% discount on the next bill.")
            st.write("  - Action: Schedule a follow-up call from a customer success manager.")
    else:
        st.write("No high-risk customers identified.")

def answer_question(question):
    st.subheader("Augmented Analytics Answer")
    question = question.lower()

    if "high-risk" in question or "high risk" in question:
        st.write("Fetching high-risk customers...")
        try:
            predictions_df = get_churn_data(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID)
            high_risk_customers = predictions_df[predictions_df['churn_probability'] > 0.75]
        except Exception as e:
            st.error(f"Could not fetch predictions from table {PREDICTIONS_DATASET_ID}.{PREDICTIONS_TABLE_ID}.")
            st.error(f"Reason: {e}")

    elif "top features" in question or "driving churn" in question:
        st.write("Identifying top features driving churn...")
        st.write("This feature requires a trained model and data to analyze. Please make a prediction first to see the summary plot.")

    elif "latest predictions" in question:
        st.write("Fetching latest predictions...")
        try:
            predictions_df = get_churn_data(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID)
            st.dataframe(predictions_df.tail())
        except Exception as e:
            st.error(f"Could not fetch predictions from table {PREDICTIONS_DATASET_ID}.{PREDICTIONS_TABLE_ID}.")
            st.error(f"Reason: {e}")

    else:
        st.write("Sorry, I don't understand that question. Try questions like:")
        st.write("- 'Show me high-risk customers'")
        st.write("- 'What are the top features driving churn?'")
        st.write("- 'Show me the latest predictions'")

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
    ("Manual Input", "Upload CSV", "Real-time Prediction")
)

predictor = None
if os.path.exists(MODEL_PATH):
    try:
        predictor = ChurnPredictor(model_path=MODEL_PATH)
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
        plan_tier = st.selectbox("Plan Tier", ['basic', 'standard', 'premium']) # Example values, adjust as per your data
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
            'is_trial': [int(is_trial)],
            'upgrade_flag': [int(upgrade_flag)],
            'downgrade_flag': [int(downgrade_flag)],
            'auto_renew_flag': [int(auto_renew_flag)],
        })
        manual_input_data['plan_tier'] = plan_tier.lower()
        manual_input_data['billing_frequency'] = billing_frequency.lower()

        if st.button("Predict Churn (Manual)"):
            try:
                predictions_df, shap_explanation = predictor.predict_and_explain(manual_input_data)
                st.write("### Prediction Results:")
                st.dataframe(predictions_df)

                st.write("### Prediction Explanations:")
                st.pyplot(shap.force_plot(shap_explanation[0]))

                if st.checkbox("Store Predictions in BigQuery?"):
                    store_predictions(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID, predictions_df)
                    st.success("Predictions stored in BigQuery.")

                if st.button("Take Action"):
                    take_action(predictions_df)

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
                    predictions_df, shap_explanation = predictor.predict_and_explain(df_to_predict)
                    st.write("### Prediction Results:")
                    st.dataframe(predictions_df)

                    st.write("### Prediction Explanations (Summary Plot):")
                    st.pyplot(shap.summary_plot(shap_explanation, df_to_predict))

                    if st.checkbox("Store Predictions in BigQuery?"):
                        store_predictions(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID, predictions_df)
                        st.success("Predictions stored in BigQuery.")

                    if st.button("Take Action"):
                        take_action(predictions_df)
            except Exception as e:
                st.error(f"Error during CSV prediction: {e}")

    elif prediction_mode == "Real-time Prediction":
        st.subheader("Real-time Churn Prediction Simulation")
        st.write("Simulating a real-time stream of customer events...")

        if st.button("Start Real-time Simulation"):
            import time
            import random

            placeholder = st.empty()

            for i in range(100): # Simulate 100 events
                with placeholder.container():
                    customer_id = f"C{random.randint(10000, 99999)}"
                    seats = random.randint(1, 10)
                    mrr_amount = random.randint(10, 200)
                    arr_amount = mrr_amount * 12
                    plan_tier = random.choice(['Basic', 'Standard', 'Premium'])
                    is_trial = random.choice([True, False])
                    upgrade_flag = random.choice([True, False])
                    downgrade_flag = random.choice([True, False])
                    billing_frequency = random.choice(['Monthly', 'Annually'])
                    auto_renew_flag = random.choice([True, False])

                    real_time_data = pd.DataFrame({
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

                    st.write(f"**New Event for Customer {customer_id}**")
                    predictions_df, _ = predictor.predict_and_explain(real_time_data)
                    st.dataframe(predictions_df)

                    if predictions_df['churn_probability'].iloc[0] > 0.75:
                        st.warning(f"High churn risk detected for customer {customer_id}!")
                        take_action(predictions_df)

                    time.sleep(2) # Wait for 2 seconds before the next event
st.sidebar.header("Augmented Analytics")
question = st.sidebar.text_input("Ask a question about your churn data")
if st.sidebar.button("Get Answer"):
    answer_question(question)
