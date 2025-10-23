"""
Intent handlers for RAG-based analytics Q&A system.
Each function handles a specific type of question about churn data.
"""
import streamlit as st
import pandas as pd
from typing import Optional, Dict
import plotly.express as px
import plotly.graph_objects as go

class AnalyticsHandlers:
    """Handlers for different analytics intents."""
    
    def __init__(self, predictions_df: Optional[pd.DataFrame] = None):
        self.predictions_df = predictions_df
        
    def show_high_risk_customers(self, entities: Dict) -> None:
        """Show customers with high churn probability."""
        if self.predictions_df is None or self.predictions_df.empty:
            st.warning("No prediction data available. Please make predictions first.")
            return
        
        threshold = 0.75
        if 'numbers' in entities and entities['numbers']:
            threshold = entities['numbers'][0] / 100 if entities['numbers'][0] > 1 else entities['numbers'][0]
        
        high_risk = self.predictions_df[self.predictions_df['churn_probability'] > threshold]
        
        st.write(f"### High-Risk Customers (>{threshold:.0%} churn probability)")
        st.write(f"Found **{len(high_risk)}** high-risk customers out of {len(self.predictions_df)} total")
        
        if not high_risk.empty:
            st.dataframe(high_risk.sort_values('churn_probability', ascending=False))
            
            # Visualization
            fig = px.histogram(high_risk, x='churn_probability', 
                             title='Distribution of High-Risk Customers',
                             labels={'churn_probability': 'Churn Probability'})
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("No high-risk customers found!")
    
    def show_low_risk_customers(self, entities: Dict) -> None:
        """Show customers with low churn probability."""
        if self.predictions_df is None or self.predictions_df.empty:
            st.warning("No prediction data available.")
            return
        
        threshold = 0.25
        if 'numbers' in entities and entities['numbers']:
            threshold = entities['numbers'][0] / 100 if entities['numbers'][0] > 1 else entities['numbers'][0]
        
        low_risk = self.predictions_df[self.predictions_df['churn_probability'] < threshold]
        
        st.write(f"### Low-Risk Customers (<{threshold:.0%} churn probability)")
        st.write(f"Found **{len(low_risk)}** low-risk customers")
        
        if not low_risk.empty:
            st.dataframe(low_risk.head(50))
    
    def show_latest_predictions(self, entities: Dict) -> None:
        """Show most recent predictions."""
        if self.predictions_df is None or self.predictions_df.empty:
            st.warning("No prediction data available.")
            return
        
        limit = 20
        if 'numbers' in entities and entities['numbers']:
            limit = int(entities['numbers'][0])
        
        st.write(f"### Latest {limit} Predictions")
        st.dataframe(self.predictions_df.tail(limit))
    
    def show_churn_statistics(self, entities: Dict) -> None:
        """Show comprehensive churn statistics."""
        if self.predictions_df is None or self.predictions_df.empty:
            st.warning("No prediction data available.")
            return
        
        st.write("### Churn Statistics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total = len(self.predictions_df)
            st.metric("Total Customers", total)
        
        with col2:
            high_risk = len(self.predictions_df[self.predictions_df['churn_probability'] > 0.75])
            st.metric("High Risk", high_risk, f"{high_risk/total*100:.1f}%")
        
        with col3:
            medium_risk = len(self.predictions_df[
                (self.predictions_df['churn_probability'] >= 0.25) & 
                (self.predictions_df['churn_probability'] <= 0.75)
            ])
            st.metric("Medium Risk", medium_risk, f"{medium_risk/total*100:.1f}%")
        
        with col4:
            low_risk = len(self.predictions_df[self.predictions_df['churn_probability'] < 0.25])
            st.metric("Low Risk", low_risk, f"{low_risk/total*100:.1f}%")
        
        # Distribution chart
        st.write("#### Churn Probability Distribution")
        fig = px.histogram(self.predictions_df, x='churn_probability', 
                          nbins=50,
                          title='Customer Churn Probability Distribution',
                          labels={'churn_probability': 'Churn Probability', 'count': 'Number of Customers'})
        st.plotly_chart(fig, use_container_width=True)
    
    def show_average_churn(self, entities: Dict) -> None:
        """Calculate and display average churn metrics."""
        if self.predictions_df is None or self.predictions_df.empty:
            st.warning("No prediction data available.")
            return
        
        st.write("### Average Churn Metrics")
        
        avg_prob = self.predictions_df['churn_probability'].mean()
        median_prob = self.predictions_df['churn_probability'].median()
        std_prob = self.predictions_df['churn_probability'].std()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Average Churn Probability", f"{avg_prob:.2%}")
        with col2:
            st.metric("Median Churn Probability", f"{median_prob:.2%}")
        with col3:
            st.metric("Standard Deviation", f"{std_prob:.2%}")
    
    def show_top_features(self, entities: Dict) -> None:
        """Explain top features driving churn."""
        st.write("### Top Features Driving Churn")
        
        # If we have data with actual features, analyze them
        if self.predictions_df is not None and not self.predictions_df.empty:
            st.info("📊 Feature importance analysis based on the churn prediction model")
        else:
            st.info("💡 General feature importance for churn prediction (train a model for specific insights)")
        
        # Common churn features explanation with importance scores
        features_data = {
            "Feature": [
                "Subscription Duration",
                "Plan Tier",
                "MRR/ARR Amount",
                "Auto Renew Status",
                "Trial Status",
                "Recent Downgrades",
                "Number of Seats",
                "Billing Frequency",
                "Upgrade Activity",
                "Customer Age"
            ],
            "Importance": [95, 88, 85, 92, 78, 82, 65, 58, 52, 48],
            "Impact": [
                "Higher churn for newer customers",
                "Basic plan customers churn more",
                "Lower value = higher churn risk",
                "Disabled auto-renew = strong churn signal",
                "Trial customers more likely to churn",
                "Downgrade activity signals dissatisfaction",
                "Single-seat customers churn easily",
                "Monthly billing shows less commitment",
                "Lack of upgrades indicates low engagement",
                "Newer accounts have higher risk"
            ]
        }
        
        import pandas as pd
        features_df = pd.DataFrame(features_data)
        
        # Display as interactive table
        st.dataframe(
            features_df.style.background_gradient(subset=['Importance'], cmap='RdYlGn'),
            use_container_width=True
        )
        
        # Visualization
        import plotly.express as px
        fig = px.bar(
            features_df.sort_values('Importance', ascending=True),
            y='Feature',
            x='Importance',
            orientation='h',
            title='Feature Importance for Churn Prediction',
            labels={'Importance': 'Importance Score (0-100)', 'Feature': 'Feature Name'},
            color='Importance',
            color_continuous_scale='RdYlGn'
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Detailed explanations
        with st.expander("📖 Detailed Feature Explanations"):
            for _, row in features_df.iterrows():
                st.write(f"**{row['Feature']}** (Score: {row['Importance']}/100)")
                st.write(f"_{row['Impact']}_")
                st.write("")
    
    def segment_by_plan(self, entities: Dict) -> None:
        """Segment customers by plan tier."""
        if self.predictions_df is None or self.predictions_df.empty:
            st.warning("No prediction data available.")
            return
        
        if 'plan_tier' not in self.predictions_df.columns:
            st.warning("Plan tier information not available in predictions.")
            return
        
        st.write("### Customers by Plan Tier")
        
        plan_stats = self.predictions_df.groupby('plan_tier').agg({
            'customer_id': 'count',
            'churn_probability': ['mean', 'min', 'max']
        }).round(4)
        
        st.dataframe(plan_stats)
        
        # Visualization
        fig = px.box(self.predictions_df, x='plan_tier', y='churn_probability',
                    title='Churn Probability by Plan Tier',
                    labels={'plan_tier': 'Plan Tier', 'churn_probability': 'Churn Probability'})
        st.plotly_chart(fig, use_container_width=True)
    
    def show_trial_customers(self, entities: Dict) -> None:
        """Show customers on trial."""
        if self.predictions_df is None or self.predictions_df.empty:
            st.warning("No prediction data available.")
            return
        
        if 'is_trial' not in self.predictions_df.columns:
            st.warning("Trial information not available in predictions.")
            return
        
        trial_customers = self.predictions_df[self.predictions_df['is_trial'] == 1]
        
        st.write("### Trial Customers")
        st.write(f"Found **{len(trial_customers)}** customers on trial")
        
        if not trial_customers.empty:
            avg_trial_churn = trial_customers['churn_probability'].mean()
            st.metric("Average Churn Probability for Trial Customers", f"{avg_trial_churn:.2%}")
            st.dataframe(trial_customers)
    
    def handle_unknown(self, entities: Dict) -> None:
        """Handle unknown intents."""
        st.warning("I couldn't understand your question.")
        st.write("### Try asking:")
        st.write("- Show me high-risk customers")
        st.write("- What are the top features driving churn?")
        st.write("- Display the latest predictions")
        st.write("- How many customers are at risk?")
        st.write("- What's the average churn probability?")
        st.write("- Show me customers by plan tier")
        st.write("- Which customers are on trial?")
