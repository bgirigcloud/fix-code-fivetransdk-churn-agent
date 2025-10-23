"""
RAG-based Analytics Question Answering System
Uses sentence embeddings and semantic search for natural language understanding
"""
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from typing import List, Dict, Tuple, Optional
import re

class ChurnAnalyticsRAG:
    """
    RAG (Retrieval-Augmented Generation) system for churn analytics Q&A.
    Uses semantic search with TF-IDF embeddings to understand natural language queries.
    """
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            max_features=500,
            stop_words='english',
            lowercase=True
        )
        
        # Knowledge base with question templates and handlers
        self.knowledge_base = [
            {
                "query": "show me high-risk customers who are likely to churn with high probability",
                "intent": "high_risk_customers",
                "description": "Find customers with high churn probability",
                "keywords": ["high risk", "likely to churn", "high probability", "dangerous customers", "at risk"]
            },
            {
                "query": "what are the top features driving churn prediction most important factors",
                "intent": "top_features",
                "description": "Identify most important features for churn prediction",
                "keywords": ["features", "driving", "important", "factors", "influence", "cause churn"]
            },
            {
                "query": "show me latest predictions recent churn analysis newest results",
                "intent": "latest_predictions",
                "description": "Display most recent churn predictions",
                "keywords": ["latest", "recent", "newest", "last", "current predictions"]
            },
            {
                "query": "how many customers are predicted to churn count statistics total",
                "intent": "churn_statistics",
                "description": "Show statistics about churn predictions",
                "keywords": ["how many", "count", "total", "statistics", "number of customers"]
            },
            {
                "query": "show me customers with low churn probability safe customers",
                "intent": "low_risk_customers",
                "description": "Find customers unlikely to churn",
                "keywords": ["low risk", "safe", "unlikely to churn", "low probability", "stable customers"]
            },
            {
                "query": "what is the average churn probability mean churn rate",
                "intent": "average_churn",
                "description": "Calculate average churn probability",
                "keywords": ["average", "mean", "median", "typical", "churn rate"]
            },
            {
                "query": "show me customers by plan tier subscription type premium basic",
                "intent": "segment_by_plan",
                "description": "Segment customers by plan tier",
                "keywords": ["plan tier", "subscription", "premium", "basic", "standard", "by plan"]
            },
            {
                "query": "which customers are on trial trial customers probation period",
                "intent": "trial_customers",
                "description": "Find customers on trial",
                "keywords": ["trial", "probation", "test period", "evaluation"]
            },
            {
                "query": "show me customers with auto renew enabled disabled",
                "intent": "auto_renew",
                "description": "Filter by auto-renew status",
                "keywords": ["auto renew", "automatic renewal", "subscription renewal"]
            },
            {
                "query": "what features contribute most to churn for high-risk customers",
                "intent": "feature_analysis",
                "description": "Analyze feature contributions for specific customers",
                "keywords": ["feature contribution", "why churning", "explain prediction", "reason"]
            },
            {
                "query": "compare churn rates across different segments groups cohorts",
                "intent": "segment_comparison",
                "description": "Compare churn across customer segments",
                "keywords": ["compare", "difference between", "segments", "groups", "cohorts"]
            },
            {
                "query": "show me trend in churn over time temporal analysis monthly",
                "intent": "churn_trends",
                "description": "Analyze churn trends over time",
                "keywords": ["trend", "over time", "temporal", "monthly", "historical", "timeline"]
            },
            {
                "query": "predict churn for new customer make prediction forecast",
                "intent": "predict_customer",
                "description": "Make churn prediction for a customer",
                "keywords": ["predict", "forecast", "estimate", "what if", "calculate"]
            },
            {
                "query": "retrain model update predictions refresh model new data",
                "intent": "retrain_model",
                "description": "Retrain the churn prediction model",
                "keywords": ["retrain", "update model", "refresh", "rebuild", "train again"]
            }
        ]
        
        # Build the vector index
        self._build_index()
        
    def _build_index(self):
        """Build TF-IDF vectors for all knowledge base entries."""
        documents = [
            f"{item['query']} {item['description']} {' '.join(item['keywords'])}" 
            for item in self.knowledge_base
        ]
        self.doc_vectors = self.vectorizer.fit_transform(documents)
        
    def understand_query(self, query: str, top_k: int = 3) -> List[Dict]:
        """
        Use semantic search to understand the user's query intent.
        
        Args:
            query: Natural language question
            top_k: Number of top matches to return
            
        Returns:
            List of matched intents with confidence scores
        """
        # Vectorize the query
        query_vector = self.vectorizer.transform([query.lower()])
        
        # Calculate cosine similarity
        similarities = cosine_similarity(query_vector, self.doc_vectors)[0]
        
        # Get top-k matches
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        matches = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                matches.append({
                    'intent': self.knowledge_base[idx]['intent'],
                    'description': self.knowledge_base[idx]['description'],
                    'confidence': float(similarities[idx]),
                    'query_template': self.knowledge_base[idx]['query']
                })
        
        return matches
    
    def extract_entities(self, query: str) -> Dict:
        """
        Extract entities and parameters from the query.
        
        Args:
            query: Natural language question
            
        Returns:
            Dictionary of extracted entities
        """
        query_lower = query.lower()
        entities = {}
        
        # Extract numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?\b', query)
        if numbers:
            entities['numbers'] = [float(n) for n in numbers]
        
        # Extract plan tiers
        plans = ['basic', 'standard', 'premium', 'enterprise']
        for plan in plans:
            if plan in query_lower:
                entities['plan_tier'] = plan
                
        # Extract time references
        time_refs = ['today', 'yesterday', 'last week', 'last month', 'this month']
        for time_ref in time_refs:
            if time_ref in query_lower:
                entities['time_reference'] = time_ref
                
        # Extract threshold indicators
        if 'above' in query_lower or 'greater than' in query_lower or 'more than' in query_lower:
            entities['comparison'] = 'greater'
        elif 'below' in query_lower or 'less than' in query_lower or 'fewer than' in query_lower:
            entities['comparison'] = 'less'
            
        # Extract customer segments
        if 'trial' in query_lower:
            entities['is_trial'] = True
        if 'auto renew' in query_lower or 'autorenew' in query_lower:
            entities['has_auto_renew'] = True
            
        return entities
    
    def get_relevant_context(self, predictions_df: pd.DataFrame, intent: str) -> str:
        """
        Generate relevant context based on the data and intent.
        
        Args:
            predictions_df: Predictions dataframe
            intent: Identified intent
            
        Returns:
            Context string with relevant information
        """
        if predictions_df is None or predictions_df.empty:
            return "No prediction data available."
        
        context_parts = []
        
        # Basic statistics
        total_customers = len(predictions_df)
        context_parts.append(f"Total customers analyzed: {total_customers}")
        
        if 'churn_probability' in predictions_df.columns:
            avg_churn = predictions_df['churn_probability'].mean()
            context_parts.append(f"Average churn probability: {avg_churn:.2%}")
            
            high_risk = len(predictions_df[predictions_df['churn_probability'] > 0.75])
            context_parts.append(f"High-risk customers: {high_risk}")
            
            low_risk = len(predictions_df[predictions_df['churn_probability'] < 0.25])
            context_parts.append(f"Low-risk customers: {low_risk}")
        
        return " | ".join(context_parts)
    
    def generate_response(self, query: str, predictions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate a complete response to the user's query.
        
        Args:
            query: Natural language question
            predictions_df: Optional predictions dataframe
            
        Returns:
            Dictionary with intent, confidence, entities, and context
        """
        # Understand the query
        matches = self.understand_query(query)
        
        if not matches:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'message': "I couldn't understand your question. Try asking about high-risk customers, churn features, or latest predictions.",
                'suggestions': [
                    "Show me high-risk customers",
                    "What are the top features driving churn?",
                    "Display the latest predictions"
                ]
            }
        
        # Get top match
        top_match = matches[0]
        
        # Extract entities
        entities = self.extract_entities(query)
        
        # Generate context if data is available
        context = ""
        if predictions_df is not None:
            context = self.get_relevant_context(predictions_df, top_match['intent'])
        
        return {
            'intent': top_match['intent'],
            'confidence': top_match['confidence'],
            'description': top_match['description'],
            'entities': entities,
            'context': context,
            'all_matches': matches
        }
    
    def get_intent_handler(self, intent: str) -> str:
        """
        Get the function name to handle a specific intent.
        
        Args:
            intent: Intent identifier
            
        Returns:
            Function name to call
        """
        intent_handlers = {
            'high_risk_customers': 'show_high_risk_customers',
            'top_features': 'show_top_features',
            'latest_predictions': 'show_latest_predictions',
            'churn_statistics': 'show_churn_statistics',
            'low_risk_customers': 'show_low_risk_customers',
            'average_churn': 'show_average_churn',
            'segment_by_plan': 'segment_by_plan',
            'trial_customers': 'show_trial_customers',
            'auto_renew': 'filter_auto_renew',
            'feature_analysis': 'analyze_features',
            'segment_comparison': 'compare_segments',
            'churn_trends': 'show_trends',
            'predict_customer': 'make_prediction',
            'retrain_model': 'retrain_model'
        }
        
        return intent_handlers.get(intent, 'handle_unknown')


# Example usage and testing
if __name__ == '__main__':
    # Initialize RAG system
    rag = ChurnAnalyticsRAG()
    
    # Test queries
    test_queries = [
        "Show me all customers who are likely to churn",
        "What factors are causing customers to leave?",
        "Can you display the most recent predictions?",
        "How many customers do we have at high risk?",
        "Which customers on the basic plan are safe?",
        "What's the average churn rate?",
        "Show me trial customers with high churn probability"
    ]
    
    print("Testing RAG-based Analytics Q&A System")
    print("=" * 60)
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = rag.generate_response(query)
        print(f"Intent: {response['intent']} (confidence: {response['confidence']:.2%})")
        print(f"Description: {response['description']}")
        if response['entities']:
            print(f"Extracted entities: {response['entities']}")
        print("-" * 60)
