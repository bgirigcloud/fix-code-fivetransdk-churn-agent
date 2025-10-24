"""
AI Chatbot Assistant for Churn Prediction System
Uses Google Generative AI to provide intelligent responses about customer churn,
model insights, and data analytics.
"""

import os
from typing import Dict, List, Optional
import pandas as pd


class ChurnChatbot:
    """
    AI-powered chatbot for the churn prediction system.
    Provides context-aware responses about predictions, customer insights, and model explanations.
    """
    
    def __init__(self, project_id: str = None, use_gemini: bool = False):
        """
        Initialize the chatbot.
        
        Args:
            project_id: Google Cloud project ID
            use_gemini: Whether to use Google Gemini API (requires API key)
        """
        self.project_id = project_id
        self.use_gemini = use_gemini
        self.model = None
        self.chat_session = None
        
        # System context about the application
        self.system_context = """
You are an AI assistant for a SaaS Churn Prediction and Revenue Recognition system. Your role is to help users understand:

1. CHURN PREDICTIONS: Explain churn probabilities, risk levels, and prediction confidence
2. MODEL INSIGHTS: Describe how the RandomForest model works and what features drive predictions
3. CUSTOMER ANALYTICS: Provide insights about customer behavior, segments, and trends
4. DATA QUERIES: Help users formulate questions about their subscription data
5. ACTION RECOMMENDATIONS: Suggest retention strategies for high-risk customers

Key System Features:
- RandomForest classifier with 85% accuracy
- SHAP explanations for prediction transparency
- Natural language to SQL query interface (16 templates)
- Augmented analytics with 14 intent handlers
- Real-time and batch prediction modes
- BigQuery integration for data storage

Available Data Fields:
- subscription_id, account_id, customer_id
- start_date, end_date, plan_tier (Basic/Pro/Enterprise)
- seats, mrr_amount, arr_amount
- is_trial, upgrade_flag, downgrade_flag, churn_flag
- billing_frequency, auto_renew_flag
- churn_probability, churn_prediction (from ML model)

Your responses should be:
- Clear and actionable
- Data-driven when possible
- Business-focused
- Technically accurate but accessible to non-technical users
"""
        
        if use_gemini:
            try:
                import google.generativeai as genai
                
                # Try to get API key from environment or Streamlit secrets
                api_key = os.environ.get("GOOGLE_API_KEY")
                if not api_key:
                    try:
                        import streamlit as st
                        api_key = st.secrets.get("GOOGLE_API_KEY")
                    except:
                        pass
                
                if api_key:
                    genai.configure(api_key=api_key)
                    self.model = genai.GenerativeModel('gemini-pro')
                    self.chat_session = self.model.start_chat(history=[])
                    self.use_gemini = True
                else:
                    print("Warning: GOOGLE_API_KEY not found. Using fallback responses.")
                    self.use_gemini = False
            except ImportError:
                print("Warning: google-generativeai not installed. Using fallback responses.")
                self.use_gemini = False
    
    def get_data_context(self, predictions_df: Optional[pd.DataFrame] = None) -> str:
        """
        Generate context string from current prediction data.
        
        Args:
            predictions_df: DataFrame with prediction results
            
        Returns:
            Context string describing current data state
        """
        if predictions_df is None or predictions_df.empty:
            return "No prediction data currently available."
        
        context_parts = []
        
        # Basic stats
        total_customers = len(predictions_df)
        context_parts.append(f"Total customers analyzed: {total_customers}")
        
        # Churn predictions
        if 'churn_prediction' in predictions_df.columns:
            churned = predictions_df['churn_prediction'].sum()
            churn_rate = (churned / total_customers) * 100
            context_parts.append(f"Predicted churners: {churned} ({churn_rate:.1f}%)")
        
        # Risk levels
        if 'churn_probability' in predictions_df.columns:
            high_risk = len(predictions_df[predictions_df['churn_probability'] > 0.7])
            medium_risk = len(predictions_df[(predictions_df['churn_probability'] >= 0.4) & 
                                            (predictions_df['churn_probability'] <= 0.7)])
            low_risk = len(predictions_df[predictions_df['churn_probability'] < 0.4])
            context_parts.append(f"Risk levels - High: {high_risk}, Medium: {medium_risk}, Low: {low_risk}")
        
        # Plan distribution
        if 'plan_tier' in predictions_df.columns:
            plan_counts = predictions_df['plan_tier'].value_counts().to_dict()
            plan_str = ", ".join([f"{k}: {v}" for k, v in plan_counts.items()])
            context_parts.append(f"Plan distribution - {plan_str}")
        
        # Revenue impact
        if 'mrr_amount' in predictions_df.columns and 'churn_prediction' in predictions_df.columns:
            at_risk_mrr = predictions_df[predictions_df['churn_prediction'] == 1]['mrr_amount'].sum()
            context_parts.append(f"At-risk MRR: ${at_risk_mrr:,.2f}")
        
        return "\n".join(context_parts)
    
    def generate_response(self, 
                         user_message: str, 
                         predictions_df: Optional[pd.DataFrame] = None,
                         conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Generate chatbot response to user message.
        
        Args:
            user_message: User's question or message
            predictions_df: Current prediction data for context
            conversation_history: Previous messages for context
            
        Returns:
            Chatbot response string
        """
        if self.use_gemini and self.model:
            return self._generate_gemini_response(user_message, predictions_df, conversation_history)
        else:
            return self._generate_fallback_response(user_message, predictions_df)
    
    def _generate_gemini_response(self, 
                                  user_message: str,
                                  predictions_df: Optional[pd.DataFrame],
                                  conversation_history: Optional[List[Dict]]) -> str:
        """
        Generate response using Google Gemini API.
        """
        # Build context-aware prompt
        data_context = self.get_data_context(predictions_df)
        
        full_prompt = f"""
{self.system_context}

CURRENT DATA CONTEXT:
{data_context}

USER QUESTION: {user_message}

Please provide a helpful, concise response based on the system capabilities and current data.
"""
        
        try:
            response = self.chat_session.send_message(full_prompt)
            return response.text
        except Exception as e:
            return f"I encountered an error processing your request: {str(e)}. Please try rephrasing your question."
    
    def _generate_fallback_response(self, 
                                    user_message: str,
                                    predictions_df: Optional[pd.DataFrame]) -> str:
        """
        Generate rule-based response when Gemini API is not available.
        """
        message_lower = user_message.lower()
        
        # Greeting
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return """Hello! I'm your AI assistant for the Churn Prediction System. I can help you with:

- Understanding churn predictions and risk levels
- Explaining model insights and SHAP values
- Analyzing customer segments and trends
- Formulating data queries
- Suggesting retention strategies

What would you like to know?"""
        
        # Churn-related questions
        if 'churn' in message_lower:
            if predictions_df is not None and not predictions_df.empty:
                if 'churn_probability' in predictions_df.columns:
                    high_risk = len(predictions_df[predictions_df['churn_probability'] > 0.7])
                    avg_prob = predictions_df['churn_probability'].mean()
                    
                    if 'most likely' in message_lower or 'highest' in message_lower:
                        top_customer = predictions_df.nlargest(1, 'churn_probability').iloc[0]
                        return f"""Based on current predictions, customer **{top_customer.get('customer_id', 'N/A')}** has the highest churn risk:

- Churn Probability: {top_customer['churn_probability']:.1%}
- Plan Tier: {top_customer.get('plan_tier', 'N/A')}
- MRR: ${top_customer.get('mrr_amount', 0):,.2f}

**Recommended Actions:**
1. Schedule immediate outreach from customer success team
2. Review their recent product usage and engagement
3. Consider personalized retention offer
4. Identify pain points through customer feedback"""
                    
                    return f"""Current churn analysis shows:

- **High-risk customers** (>70% probability): {high_risk}
- **Average churn probability**: {avg_prob:.1%}
- **Total customers analyzed**: {len(predictions_df)}

You can explore detailed predictions in the "Make Predictions" section or ask specific questions like:
- "Show me high-risk customers"
- "What drives churn the most?"
- "Compare churn rates by plan tier" """
            else:
                return """No prediction data is currently available. To analyze churn:

1. Go to **Train New Model** to train the ML model
2. Use **Make Predictions** to predict churn for customers
3. Return here for AI-powered insights

Once you have predictions, I can provide detailed churn analysis and recommendations."""
        
        # Model/SHAP questions
        if any(word in message_lower for word in ['model', 'shap', 'explain', 'how does', 'feature']):
            return """The churn prediction system uses a **RandomForest Classifier** with the following characteristics:

**Model Details:**
- Algorithm: RandomForest (ensemble of 100 decision trees)
- Accuracy: ~85% on test data
- Training data: 1,000+ subscription records from BigQuery
- Features: 16 attributes including MRR, seats, tenure, plan changes

**SHAP Explanations:**
Every prediction includes SHAP (SHapley Additive exPlanations) values that show:
- Which features increased/decreased churn risk
- By how much each feature contributed
- Visual waterfall charts showing the decision path

**Top Churn Drivers:**
1. Low MRR/ARR amounts
2. Trial accounts without conversion
3. Recent downgrades
4. Short tenure
5. No auto-renewal enabled

View SHAP explanations in the prediction results for detailed breakdowns."""
        
        # High-risk customers
        if 'high risk' in message_lower or 'at risk' in message_lower:
            if predictions_df is not None and not predictions_df.empty and 'churn_probability' in predictions_df.columns:
                high_risk_df = predictions_df[predictions_df['churn_probability'] > 0.7]
                
                if len(high_risk_df) > 0:
                    mrr_at_risk = high_risk_df['mrr_amount'].sum() if 'mrr_amount' in high_risk_df.columns else 0
                    
                    return f"""**High-Risk Customer Alert**

Found {len(high_risk_df)} customers with >70% churn probability:

- **At-risk MRR**: ${mrr_at_risk:,.2f}/month
- **At-risk ARR**: ${mrr_at_risk * 12:,.2f}/year

**Immediate Actions:**
1. Use the Analytics section to identify common patterns
2. Review their feature usage and engagement metrics
3. Create personalized outreach campaigns
4. Consider retention incentives (discounts, upgrades, training)

View the full list in "Augmented Analytics" by asking "Show me high-risk customers" """
                else:
                    return "Good news! No customers currently have high churn risk (>70% probability). Continue monitoring with regular predictions."
            else:
                return "Please run predictions first to identify high-risk customers."
        
        # Revenue questions
        if any(word in message_lower for word in ['revenue', 'mrr', 'arr', 'money']):
            if predictions_df is not None and not predictions_df.empty:
                if 'mrr_amount' in predictions_df.columns:
                    total_mrr = predictions_df['mrr_amount'].sum()
                    total_arr = total_mrr * 12
                    
                    if 'churn_prediction' in predictions_df.columns:
                        at_risk_mrr = predictions_df[predictions_df['churn_prediction'] == 1]['mrr_amount'].sum()
                        at_risk_arr = at_risk_mrr * 12
                        
                        return f"""**Revenue Analysis:**

**Current Revenue:**
- Total MRR: ${total_mrr:,.2f}
- Total ARR: ${total_arr:,.2f}

**At-Risk Revenue (predicted churners):**
- At-risk MRR: ${at_risk_mrr:,.2f} ({(at_risk_mrr/total_mrr)*100:.1f}% of total)
- At-risk ARR: ${at_risk_arr:,.2f}

**Recommendation:** Focus retention efforts on high-value at-risk customers to protect revenue. Use the NL-to-SQL interface to query "Show customers with MRR over $1000 at high churn risk" """
        
        # Data query help
        if any(word in message_lower for word in ['query', 'sql', 'search', 'find', 'show me']):
            return """You can query the data in two ways:

**1. Augmented Analytics (Pre-built Queries):**
- "Show me high-risk customers"
- "What drives churn the most?"
- "How many customers are predicted to churn?"
- "Compare churn rates by plan tier"

**2. Natural Language to SQL:**
Open the SQL Query Interface (sidebar) and ask:
- "How many customers do we have?"
- "What is the average MRR?"
- "Show customers spending more than $500"
- "List all Enterprise plan customers"
- "What's the churn rate by billing frequency?"

The system will automatically:
- Convert your question to SQL
- Execute the query on BigQuery
- Generate visualizations
- Allow CSV export"""
        
        # General help
        if any(word in message_lower for word in ['help', 'what can you', 'capabilities', 'features']):
            return """I can assist you with:

**Churn Predictions:**
- Explain prediction probabilities and risk levels
- Identify customers most likely to churn
- Analyze churn patterns by segment

**Model Insights:**
- How the RandomForest model works
- SHAP explanation interpretations
- Feature importance and drivers

**Customer Analytics:**
- Revenue analysis (MRR, ARR, at-risk revenue)
- Customer segmentation insights
- Trend analysis and comparisons

**Data Queries:**
- Help formulate natural language questions
- Explain query results
- Suggest relevant analytics

**Retention Strategies:**
- Recommend actions for high-risk customers
- Personalized intervention strategies
- ROI calculations for retention programs

Just ask me anything about your customers, predictions, or the system!"""
        
        # Default response
        return f"""I received your message: "{user_message}"

I can help you with churn predictions, model insights, customer analytics, and data queries. Some examples:
- "Which customers are most likely to churn?"
- "Explain how the model makes predictions"
- "Show me revenue at risk"
- "How can I reduce churn?"

What would you like to know?"""
    
    def reset_conversation(self):
        """Reset the chat session."""
        if self.use_gemini and self.model:
            self.chat_session = self.model.start_chat(history=[])
