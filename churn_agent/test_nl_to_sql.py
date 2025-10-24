"""
Test script for Natural Language to SQL RAG System
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from nl_to_sql_rag import NLtoSQLRAG, format_query_results
import pandas as pd

def test_nl_to_sql_rag():
    """Test the NL-to-SQL RAG system"""
    
    print("=" * 80)
    print("Testing Natural Language to SQL RAG System")
    print("=" * 80)
    
    # Test configuration
    PROJECT_ID = "hackathon-475722"
    DATASET_ID = "saas"
    TABLE_ID = "ravenstack_subscriptions"
    
    # Initialize RAG system
    print("\n1. Initializing NL-to-SQL RAG system...")
    try:
        rag = NLtoSQLRAG(project_id=PROJECT_ID, dataset_id=DATASET_ID, table_id=TABLE_ID)
        print("✓ RAG system initialized successfully")
    except Exception as e:
        print(f"✗ Error initializing RAG system: {e}")
        return
    
    # Test schema fetching
    print("\n2. Testing schema information...")
    schema_desc = rag.get_schema_description()
    print(schema_desc)
    
    # Test example queries
    print("\n3. Available example queries:")
    examples = rag.get_example_queries()
    for i, example in enumerate(examples, 1):
        print(f"   {i}. {example}")
    
    # Test query templates
    test_queries = [
        "How many customers do we have?",
        "What is the total revenue?",
        "Show me high-risk customers",
        "Who are our top 10 customers?",
        "What is the churn rate?",
        "List customers by plan type",
        "Show me customers spending more than $500",
        "Get customers in premium plan",
        "Show new customers this month",
        "What is the average revenue per customer?"
    ]
    
    print("\n4. Testing query translation (SQL generation)...")
    print("-" * 80)
    
    success_count = 0
    for query in test_queries:
        print(f"\n📝 Query: {query}")
        
        # Generate SQL
        sql, description, metadata = rag.generate_sql(query)
        
        if sql:
            print(f"✓ Intent: {description}")
            print(f"  Confidence: {metadata['confidence']:.2%}")
            if metadata['entities']:
                print(f"  Entities: {metadata['entities']}")
            print(f"\n  Generated SQL:")
            print(f"  {sql[:200]}..." if len(sql) > 200 else f"  {sql}")
            success_count += 1
        else:
            print(f"✗ Could not generate SQL: {description}")
        
        print("-" * 80)
    
    print(f"\n📊 Translation Success Rate: {success_count}/{len(test_queries)} ({success_count/len(test_queries)*100:.1f}%)")
    
    # Test end-to-end query execution (with first query only)
    print("\n5. Testing end-to-end query execution...")
    test_query = "How many customers do we have?"
    print(f"Executing: {test_query}")
    
    try:
        result = rag.process_user_query(test_query)
        
        if result['success']:
            print("✓ Query executed successfully")
            print(f"  SQL: {result['sql']}")
            print(f"  Description: {result['message']}")
            
            if result['results'] is not None and not result['results'].empty:
                print(f"\n  Results:")
                print(format_query_results(result['results']))
            else:
                print("  No results returned")
        else:
            print(f"✗ Query execution failed: {result['message']}")
    
    except Exception as e:
        print(f"✗ Error during execution: {e}")
        print("  Note: This is expected if BigQuery credentials are not configured")
    
    # Test entity extraction
    print("\n6. Testing entity extraction...")
    test_entity_queries = [
        ("Show me customers spending more than $1000", {"amount": 1000.0}),
        ("Get customers in premium plan", {"plan": "premium"}),
        ("Who has enterprise plan with MRR above $5000", {"plan": "enterprise", "amount": 5000.0})
    ]
    
    for query, expected_entities in test_entity_queries:
        print(f"\n📝 Query: {query}")
        entities = rag._extract_entities(query)
        print(f"  Extracted: {entities}")
        print(f"  Expected: {expected_entities}")
        
        # Check if all expected entities were extracted
        match = all(entities.get(k) == v for k, v in expected_entities.items())
        print(f"  {'✓ Match' if match else '✗ Mismatch'}")
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)

if __name__ == "__main__":
    test_nl_to_sql_rag()
