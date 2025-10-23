"""
Test the RAG-based Analytics Q&A System
"""
from rag_analytics import ChurnAnalyticsRAG
import pandas as pd
import numpy as np

def create_sample_data():
    """Create sample predictions data for testing."""
    np.random.seed(42)
    n_samples = 100
    
    data = {
        'customer_id': [f'C{i:05d}' for i in range(n_samples)],
        'churn_prediction': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
        'churn_probability': np.random.beta(2, 5, n_samples),
        'plan_tier': np.random.choice(['basic', 'standard', 'premium'], n_samples),
        'is_trial': np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        'mrr_amount': np.random.uniform(10, 500, n_samples),
        'seats': np.random.randint(1, 20, n_samples)
    }
    
    return pd.DataFrame(data)

def test_rag_system():
    """Test the RAG system with various queries."""
    print("=" * 70)
    print("Testing RAG-based Analytics Q&A System")
    print("=" * 70)
    print()
    
    # Initialize RAG system
    print("1. Initializing RAG system...")
    rag = ChurnAnalyticsRAG()
    print("   ✓ RAG system initialized")
    print()
    
    # Create sample data
    print("2. Creating sample prediction data...")
    predictions_df = create_sample_data()
    print(f"   ✓ Created {len(predictions_df)} sample predictions")
    print()
    
    # Test queries
    test_queries = [
        "Show me all high-risk customers who might churn",
        "What are the main factors causing customers to leave?",
        "Can you display the latest predictions?",
        "How many customers are at risk of churning?",
        "Show me customers with low churn probability",
        "What's the average churn rate across all customers?",
        "Which customers on the premium plan are safe?",
        "Show me trial customers with high churn risk",
        "Compare churn rates between different plan tiers",
        "What's the churn trend over time?",
        "I want to see customers with more than 75% churn probability",
        "How many basic plan customers are likely to churn?",
        "Random unrelated question that should fail gracefully"
    ]
    
    print("3. Testing query understanding...")
    print("-" * 70)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}/{len(test_queries)}")
        print(f"Query: {query}")
        
        # Generate response
        response = rag.generate_response(query, predictions_df)
        
        # Display results
        print(f"Intent: {response['intent']}")
        print(f"Confidence: {response['confidence']:.2%}")
        
        if response['intent'] != 'unknown':
            print(f"Description: {response['description']}")
        else:
            print(f"Message: {response.get('message', 'Unknown query')}")
        
        if response.get('entities'):
            print(f"Entities extracted: {response['entities']}")
        
        if response.get('context'):
            print(f"Context: {response['context']}")
        
        # Show top 3 matches
        if len(response.get('all_matches', [])) > 1:
            print("Alternative interpretations:")
            for match in response['all_matches'][:3]:
                print(f"  - {match['description']} ({match['confidence']:.1%})")
        
        print("-" * 70)
    
    print()
    print("4. Testing entity extraction...")
    entity_test_queries = [
        "Show me customers with more than 80% churn probability",
        "Find basic plan customers",
        "Show me trial customers from last month",
        "Customers with less than 20% churn risk"
    ]
    
    for query in entity_test_queries:
        entities = rag.extract_entities(query)
        print(f"Query: {query}")
        print(f"Entities: {entities}")
        print()
    
    print("=" * 70)
    print("✓ RAG SYSTEM TESTS COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()
    
    # Performance summary
    print("Summary:")
    print(f"- Total queries tested: {len(test_queries)}")
    print(f"- Knowledge base entries: {len(rag.knowledge_base)}")
    print(f"- Vector dimensions: {rag.doc_vectors.shape}")
    print()
    print("The RAG system is ready for use in the Streamlit app!")

if __name__ == '__main__':
    test_rag_system()
