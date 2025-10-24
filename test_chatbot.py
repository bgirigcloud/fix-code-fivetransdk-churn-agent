"""
Quick test script for the AI Chatbot Assistant
"""

import sys
sys.path.insert(0, r'D:\CloudHeroWithAI\Hackthon-DEVPOST-AI-accelarate\fivetransdk-churn-agent\churn_agent')

from chatbot_assistant import ChurnChatbot
import pandas as pd

def test_chatbot():
    """Test the chatbot with sample questions."""
    
    print("=" * 80)
    print("AI Chatbot Assistant - Test Suite")
    print("=" * 80)
    
    # Initialize chatbot (fallback mode)
    print("\n1. Initializing Chatbot (Fallback Mode)...")
    chatbot = ChurnChatbot(project_id="hackathon-475722", use_gemini=False)
    print("   ✓ Chatbot initialized successfully")
    
    # Create sample prediction data
    print("\n2. Creating Sample Prediction Data...")
    sample_data = pd.DataFrame({
        'customer_id': ['CUST_001', 'CUST_002', 'CUST_003', 'CUST_004', 'CUST_005'],
        'churn_probability': [0.85, 0.45, 0.25, 0.92, 0.15],
        'churn_prediction': [1, 0, 0, 1, 0],
        'plan_tier': ['Enterprise', 'Pro', 'Basic', 'Enterprise', 'Pro'],
        'mrr_amount': [2500, 750, 250, 3200, 890],
        'seats': [50, 15, 5, 75, 20]
    })
    print(f"   ✓ Created sample data with {len(sample_data)} customers")
    
    # Test questions
    test_questions = [
        "Hello, how can you help me?",
        "Which customers are most likely to churn?",
        "How does the churn prediction model work?",
        "Show me high-risk customers",
        "How much revenue is at risk?",
        "What can you do?",
    ]
    
    print("\n3. Testing Chatbot Responses...")
    print("-" * 80)
    
    for i, question in enumerate(test_questions, 1):
        print(f"\nQuestion {i}: {question}")
        print("-" * 80)
        
        response = chatbot.generate_response(question, sample_data)
        print(response)
        print("-" * 80)
    
    # Test data context generation
    print("\n4. Testing Data Context Generation...")
    context = chatbot.get_data_context(sample_data)
    print(context)
    print("   ✓ Context generated successfully")
    
    print("\n" + "=" * 80)
    print("All Tests Completed Successfully!")
    print("=" * 80)
    
    print("\n📋 Summary:")
    print(f"   - Chatbot Mode: Fallback (rule-based)")
    print(f"   - Test Questions: {len(test_questions)}")
    print(f"   - Sample Customers: {len(sample_data)}")
    print(f"   - High Risk Customers: {len(sample_data[sample_data['churn_probability'] > 0.7])}")
    print(f"   - Total MRR: ${sample_data['mrr_amount'].sum():,}")
    print(f"   - At-risk MRR: ${sample_data[sample_data['churn_prediction'] == 1]['mrr_amount'].sum():,}")
    
    print("\n✅ Chatbot is ready for integration into Streamlit app!")

if __name__ == "__main__":
    test_chatbot()
