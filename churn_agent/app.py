import streamlit as st
import pandas as pd
from data_handler import get_churn_data, get_subscription_data, store_predictions
from model_trainer import train_model
from predictor import ChurnPredictor
from rag_analytics import ChurnAnalyticsRAG
from analytics_handlers import AnalyticsHandlers
from nl_to_sql_rag import NLtoSQLRAG, format_query_results
from chatbot_assistant import ChurnChatbot
import os
import matplotlib.pyplot as plt
import shap
import plotly.express as px

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

@st.cache_resource
def get_rag_system():
    """Initialize and cache the RAG system."""
    return ChurnAnalyticsRAG()

@st.cache_resource
def get_chatbot():
    """Initialize and cache the chatbot assistant."""
    # Set use_gemini=True if you have GOOGLE_API_KEY configured
    return ChurnChatbot(project_id=PROJECT_ID, use_gemini=False)

def answer_question(question):
    """
    RAG-based question answering system with semantic understanding.
    Uses vector embeddings and NLP to understand natural language queries.
    """
    st.subheader("🤖 Augmented Analytics Answer")
    
    # Initialize RAG system
    rag = get_rag_system()
    
    # Fetch predictions data
    predictions_df = None
    try:
        predictions_df = get_churn_data(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID)
    except Exception as e:
        st.warning(f"Could not fetch predictions from BigQuery: {e}")
        st.info("Using RAG system without live data. Train a model and make predictions for full functionality.")
    
    # Generate response using RAG
    with st.spinner("Understanding your question..."):
        response = rag.generate_response(question, predictions_df)
    
    # Display understanding
    confidence_color = "🟢" if response['confidence'] > 0.5 else "🟡" if response['confidence'] > 0.3 else "🔴"
    st.write(f"{confidence_color} **Intent:** {response['description']} (Confidence: {response['confidence']:.0%})")
    
    # Show extracted entities if any
    if response['entities']:
        with st.expander("📊 Extracted Parameters"):
            st.json(response['entities'])
    
    # Show context if available
    if response.get('context'):
        st.info(f"📈 Context: {response['context']}")
    
    # Execute the appropriate handler
    if response['intent'] != 'unknown' and predictions_df is not None:
        st.write("---")
        handlers = AnalyticsHandlers(predictions_df)
        handler_name = rag.get_intent_handler(response['intent'])
        
        if hasattr(handlers, handler_name):
            handler_method = getattr(handlers, handler_name)
            handler_method(response['entities'])
        else:
            handlers.handle_unknown(response['entities'])
    elif response['intent'] == 'unknown':
        st.error(response['message'])
        st.write("### Suggestions:")
        for suggestion in response['suggestions']:
            st.write(f"- {suggestion}")
    else:
        st.warning("No prediction data available. Please train a model and make predictions first.")
    
    # Show alternative interpretations
    if len(response.get('all_matches', [])) > 1:
        with st.expander("🔍 Alternative Interpretations"):
            for i, match in enumerate(response['all_matches'][1:], 2):
                st.write(f"{i}. {match['description']} (confidence: {match['confidence']:.0%})")

# --- Streamlit App --- #
# Display header image (contains all branding and title)
st.image(
    "https://storage.googleapis.com/devpost-ai-accelerate/Hackothon-devpost-ai-accelerate/ai-accelrate3.png",
    use_container_width=True
)

# Add some spacing
st.write("")

st.sidebar.header("Actions")

# --- AI Chatbot Assistant ---
if st.sidebar.button("💬 AI Assistant Chat", key="chatbot_toggle"):
    if 'show_chatbot' not in st.session_state:
        st.session_state.show_chatbot = True
    else:
        st.session_state.show_chatbot = not st.session_state.show_chatbot

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
        st.sidebar.success("✓ Model loaded successfully!")
    except Exception as e:
        st.error(f"Error loading model: {e}")
        st.error("This usually happens when the model was trained with a different scikit-learn version.")
        st.info("**Solution:** Please click 'Train New Model' in the sidebar to retrain the model with the current environment.")
        st.warning("No predictions can be made until a new model is trained.")
else:
    st.warning("No trained model found. Please train a model first by clicking 'Train New Model' in the sidebar.")

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
                # For single prediction, use waterfall plot
                import matplotlib.pyplot as plt
                fig, ax = plt.subplots(figsize=(10, 4))
                shap.plots.waterfall(shap_explanation[0], show=False)
                st.pyplot(fig)
                plt.close()

                if st.checkbox("Store Predictions in BigQuery?"):
                    store_predictions(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID, predictions_df)
                    st.success("Predictions stored in BigQuery.")

                if st.button("Take Action"):
                    take_action(predictions_df)

            except Exception as e:
                st.error(f"Error during manual prediction: {e}")
                import traceback
                st.error(traceback.format_exc())

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
                    fig, ax = plt.subplots(figsize=(10, 6))
                    shap.plots.beeswarm(shap_explanation, show=False)
                    st.pyplot(fig)
                    plt.close()

                    if st.checkbox("Store Predictions in BigQuery?"):
                        store_predictions(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID, predictions_df)
                        st.success("Predictions stored in BigQuery.")

                    if st.button("Take Action"):
                        take_action(predictions_df)
            except Exception as e:
                st.error(f"Error during CSV prediction: {e}")
                import traceback
                st.error(traceback.format_exc())

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

# --- Natural Language to SQL RAG Interface ---
st.sidebar.header("🔍 Query Data with Natural Language")
if st.sidebar.button("Open SQL Query Interface"):
    st.session_state.show_sql_interface = True

if st.session_state.get('show_sql_interface', False):
    st.markdown("---")
    st.header("🤖 Natural Language to SQL Query Interface")
    st.write("Ask questions in plain English, and I'll translate them to SQL and execute them on BigQuery!")
    
    # Initialize NL-to-SQL RAG system
    @st.cache_resource
    def get_nl_to_sql_rag():
        """Initialize and cache the NL-to-SQL RAG system."""
        try:
            return NLtoSQLRAG(project_id=PROJECT_ID, dataset_id=CHURN_DATASET_ID, table_id=CHURN_TABLE_ID)
        except Exception as e:
            st.error(f"Error initializing SQL RAG system: {e}")
            return None
    
    nl_sql_rag = get_nl_to_sql_rag()
    
    if nl_sql_rag:
        # Show schema information
        with st.expander("📊 View Available Data Schema"):
            st.markdown(nl_sql_rag.get_schema_description())
        
        # Show example queries
        with st.expander("💡 Example Questions You Can Ask"):
            examples = nl_sql_rag.get_example_queries()
            cols = st.columns(2)
            for i, example in enumerate(examples):
                with cols[i % 2]:
                    if st.button(example, key=f"example_{i}"):
                        st.session_state.nl_query = example
            st.info("Click any example to use it, or type your own question below!")
        
        # Query input
        user_nl_query = st.text_area(
            "🗣️ Ask your question in plain English:",
            value=st.session_state.get('nl_query', ''),
            height=100,
            placeholder="e.g., How many customers do we have? What is the total revenue? Show me high-risk customers..."
        )
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            execute_query = st.button("🚀 Execute Query", type="primary")
        with col2:
            if st.button("🔄 Clear"):
                st.session_state.nl_query = ''
                st.rerun()
        with col3:
            if st.button("❌ Close Interface"):
                st.session_state.show_sql_interface = False
                st.rerun()
        
        if execute_query and user_nl_query:
            with st.spinner("🧠 Understanding your question and generating SQL..."):
                result = nl_sql_rag.process_user_query(user_nl_query)
            
            # Display understanding
            st.subheader("📝 Query Understanding")
            col1, col2 = st.columns(2)
            
            with col1:
                if result['success']:
                    st.success(f"✅ {result['message']}")
                else:
                    st.error(f"❌ {result['message']}")
            
            with col2:
                if result['metadata'].get('confidence'):
                    confidence = result['metadata']['confidence']
                    confidence_pct = confidence * 100
                    st.metric("Confidence", f"{confidence_pct:.1f}%")
            
            # Show extracted entities
            if result['metadata'].get('entities'):
                with st.expander("🎯 Extracted Parameters"):
                    st.json(result['metadata']['entities'])
            
            # Display generated SQL
            if result['sql']:
                st.subheader("🔧 Generated SQL Query")
                st.code(result['sql'], language='sql')
                
                # Add copy button functionality
                st.caption("💡 Tip: You can copy this SQL query and use it directly in BigQuery console")
            
            # Display results
            if result['success'] and result['results'] is not None:
                st.subheader("📊 Query Results")
                
                results_df = result['results']
                
                if not results_df.empty:
                    # Format and display results
                    formatted_result = format_query_results(results_df)
                    
                    if isinstance(formatted_result, str):
                        st.markdown(formatted_result)
                    else:
                        # Display as interactive dataframe
                        st.dataframe(results_df, use_container_width=True)
                        
                        # Add download button
                        csv = results_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Results as CSV",
                            data=csv,
                            file_name="query_results.csv",
                            mime="text/csv",
                        )
                        
                        # Auto-generate visualizations for certain result types
                        st.subheader("📈 Visualizations")
                        
                        # If results have numeric columns, show charts
                        numeric_cols = results_df.select_dtypes(include=['number']).columns.tolist()
                        
                        if len(numeric_cols) > 0:
                            # For grouped results (e.g., by plan, by month)
                            if len(results_df) > 1 and len(results_df.columns) >= 2:
                                chart_type = st.selectbox(
                                    "Select Chart Type:",
                                    ["Bar Chart", "Line Chart", "Pie Chart", "Table Only"]
                                )
                                
                                if chart_type == "Bar Chart":
                                    x_col = results_df.columns[0]
                                    y_col = numeric_cols[0]
                                    fig = px.bar(results_df, x=x_col, y=y_col, 
                                               title=f"{y_col} by {x_col}")
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                elif chart_type == "Line Chart":
                                    x_col = results_df.columns[0]
                                    y_col = numeric_cols[0]
                                    fig = px.line(results_df, x=x_col, y=y_col,
                                                title=f"{y_col} Trend")
                                    st.plotly_chart(fig, use_container_width=True)
                                
                                elif chart_type == "Pie Chart":
                                    x_col = results_df.columns[0]
                                    y_col = numeric_cols[0]
                                    fig = px.pie(results_df, names=x_col, values=y_col,
                                               title=f"Distribution of {y_col}")
                                    st.plotly_chart(fig, use_container_width=True)
                            
                            # For single metrics, show as metric cards
                            elif len(results_df) == 1:
                                cols = st.columns(len(numeric_cols))
                                for idx, col_name in enumerate(numeric_cols):
                                    with cols[idx]:
                                        value = results_df[col_name].iloc[0]
                                        st.metric(label=col_name, value=f"{value:,.2f}")
                        
                        # Show row count
                        st.caption(f"📝 Showing {len(results_df)} rows")
                
                else:
                    st.info("Query executed successfully but returned no results.")
        
        elif execute_query and not user_nl_query:
            st.warning("Please enter a question first!")

# --- AI Chatbot Assistant Interface ---
if st.session_state.get('show_chatbot', False):
    st.markdown("---")
    st.header("💬 AI Assistant Chat")
    st.caption("Ask me anything about churn predictions, customer insights, or the system capabilities")
    
    # Initialize chatbot
    chatbot = get_chatbot()
    
    # Get current prediction data for context
    predictions_df = None
    try:
        predictions_df = get_churn_data(PROJECT_ID, PREDICTIONS_DATASET_ID, PREDICTIONS_TABLE_ID)
    except:
        pass
    
    # Initialize chat history in session state
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []
    
    # Display chat history
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Quick action buttons
    st.write("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Show high-risk customers", key="quick_high_risk"):
            quick_question = "Which customers are most likely to churn?"
            st.session_state.chat_messages.append({"role": "user", "content": quick_question})
            response = chatbot.generate_response(quick_question, predictions_df, st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("🎯 Explain the model", key="quick_model"):
            quick_question = "How does the churn prediction model work?"
            st.session_state.chat_messages.append({"role": "user", "content": quick_question})
            response = chatbot.generate_response(quick_question, predictions_df, st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("💰 Revenue at risk", key="quick_revenue"):
            quick_question = "How much revenue is at risk from churn?"
            st.session_state.chat_messages.append({"role": "user", "content": quick_question})
            response = chatbot.generate_response(quick_question, predictions_df, st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Chat input
    if user_prompt := st.chat_input("Ask me anything about churn predictions..."):
        # Add user message to history and display
        st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
        with st.chat_message("user"):
            st.markdown(user_prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = chatbot.generate_response(
                    user_prompt, 
                    predictions_df,
                    st.session_state.chat_messages
                )
            st.markdown(response)
        
        # Add assistant response to history
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
    
    # Clear chat button
    if st.button("🗑️ Clear Chat History", key="clear_chat"):
        st.session_state.chat_messages = []
        chatbot.reset_conversation()
        st.rerun()
