"""
Natural Language to SQL RAG System
Translates user queries in plain English to BigQuery SQL queries
"""

import re
from typing import Dict, List, Tuple, Optional
from google.cloud import bigquery
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


class NLtoSQLRAG:
    """RAG system for converting natural language to BigQuery SQL queries"""
    
    def __init__(self, project_id: str, dataset_id: str = "saas", table_id: str = "ravenstack_subscriptions"):
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.table_id = table_id
        self.client = bigquery.Client(project=project_id)
        
        # Initialize schema information
        self.schema_info = self._get_schema_info()
        
        # SQL query templates with natural language patterns
        self.query_templates = self._initialize_query_templates()
        
        # Initialize TF-IDF vectorizer for semantic matching
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 3), max_features=500)
        self._train_vectorizer()
        
    def _get_schema_info(self) -> Dict:
        """Fetch and cache BigQuery table schema"""
        try:
            table_ref = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            table = self.client.get_table(table_ref)
            
            schema_info = {
                "columns": [field.name for field in table.schema],
                "column_types": {field.name: field.field_type for field in table.schema},
                "table_ref": table_ref
            }
            
            return schema_info
        except Exception as e:
            print(f"Error fetching schema: {e}")
            # Default schema based on actual table structure
            return {
                "columns": ["subscription_id", "account_id", "start_date", "end_date", "plan_tier", 
                           "seats", "mrr_amount", "arr_amount", "is_trial", "upgrade_flag", 
                           "downgrade_flag", "churn_flag", "billing_frequency", "auto_renew_flag"],
                "column_types": {},
                "table_ref": f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            }
    
    def _initialize_query_templates(self) -> List[Dict]:
        """Initialize SQL query templates with NL patterns"""
        templates = [
            {
                "patterns": [
                    "how many customers",
                    "total customers",
                    "count customers",
                    "number of customers",
                    "customer count",
                    "how many accounts"
                ],
                "sql_template": "SELECT COUNT(DISTINCT account_id) as total_customers FROM `{table_ref}`",
                "description": "Count total customers"
            },
            {
                "patterns": [
                    "how many subscriptions",
                    "total subscriptions",
                    "count subscriptions",
                    "number of subscriptions"
                ],
                "sql_template": "SELECT COUNT(*) as total_subscriptions FROM `{table_ref}`",
                "description": "Count total subscriptions"
            },
            {
                "patterns": [
                    "total revenue",
                    "total mrr",
                    "sum of revenue",
                    "revenue total",
                    "monthly recurring revenue"
                ],
                "sql_template": "SELECT SUM(mrr_amount) as total_mrr FROM `{table_ref}`",
                "description": "Calculate total MRR"
            },
            {
                "patterns": [
                    "average revenue",
                    "average mrr",
                    "mean revenue",
                    "avg mrr per customer"
                ],
                "sql_template": "SELECT AVG(mrr_amount) as avg_mrr FROM `{table_ref}`",
                "description": "Calculate average MRR"
            },
            {
                "patterns": [
                    "churned customers",
                    "customers who churned",
                    "cancelled subscriptions",
                    "inactive customers",
                    "lost customers"
                ],
                "sql_template": "SELECT * FROM `{table_ref}` WHERE churn_flag = TRUE",
                "description": "Get churned customers"
            },
            {
                "patterns": [
                    "active customers",
                    "current customers",
                    "active subscriptions",
                    "paying customers"
                ],
                "sql_template": "SELECT * FROM `{table_ref}` WHERE churn_flag = FALSE",
                "description": "Get active customers"
            },
            {
                "patterns": [
                    "high risk customers",
                    "at risk customers",
                    "likely to churn",
                    "churn risk high",
                    "customers at risk"
                ],
                "sql_template": "SELECT * FROM `{table_ref}` WHERE churn_flag = FALSE ORDER BY mrr_amount DESC LIMIT 20",
                "description": "Get potential high-value customers"
            },
            {
                "patterns": [
                    "customers by plan",
                    "subscriptions by plan type",
                    "breakdown by plan",
                    "group by plan"
                ],
                "sql_template": "SELECT plan_tier, COUNT(*) as count, SUM(mrr_amount) as total_mrr FROM `{table_ref}` GROUP BY plan_tier ORDER BY total_mrr DESC",
                "description": "Group customers by plan type"
            },
            {
                "patterns": [
                    "top customers",
                    "highest paying customers",
                    "best customers",
                    "largest revenue customers",
                    "top 10 customers"
                ],
                "sql_template": "SELECT account_id, mrr_amount, plan_tier FROM `{table_ref}` ORDER BY mrr_amount DESC LIMIT 10",
                "description": "Get top customers by revenue"
            },
            {
                "patterns": [
                    "new customers",
                    "recent subscriptions",
                    "customers this month",
                    "latest customers"
                ],
                "sql_template": "SELECT * FROM `{table_ref}` WHERE PARSE_DATE('%Y-%m-%d', start_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY) ORDER BY start_date DESC",
                "description": "Get new customers in last 30 days"
            },
            {
                "patterns": [
                    "customers with tenure",
                    "long term customers",
                    "customer tenure",
                    "how long have customers"
                ],
                "sql_template": "SELECT account_id, start_date, mrr_amount FROM `{table_ref}` ORDER BY start_date ASC LIMIT 20",
                "description": "Get longest tenure customers"
            },
            {
                "patterns": [
                    "churn rate",
                    "percentage churned",
                    "churn percentage",
                    "what is the churn rate"
                ],
                "sql_template": """
                    SELECT 
                        COUNT(CASE WHEN churn_flag = TRUE THEN 1 END) as churned_count,
                        COUNT(*) as total_count,
                        ROUND(COUNT(CASE WHEN churn_flag = TRUE THEN 1 END) * 100.0 / COUNT(*), 2) as churn_rate_percent
                    FROM `{table_ref}`
                """,
                "description": "Calculate churn rate"
            },
            {
                "patterns": [
                    "revenue by month",
                    "monthly revenue",
                    "mrr by month",
                    "revenue trend"
                ],
                "sql_template": """
                    SELECT 
                        SUBSTR(start_date, 1, 7) as month,
                        SUM(mrr_amount) as monthly_revenue,
                        COUNT(*) as subscription_count
                    FROM `{table_ref}`
                    GROUP BY month
                    ORDER BY month DESC
                    LIMIT 12
                """,
                "description": "Get monthly revenue trend"
            },
            {
                "patterns": [
                    "show me all",
                    "get all data",
                    "show everything",
                    "list all records"
                ],
                "sql_template": "SELECT * FROM `{table_ref}` LIMIT 100",
                "description": "Get all records (limited to 100)"
            },
            {
                "patterns": [
                    "customers spending more than",
                    "mrr greater than",
                    "revenue above",
                    "customers with high mrr"
                ],
                "sql_template": "SELECT * FROM `{table_ref}` WHERE mrr_amount > {amount} ORDER BY mrr_amount DESC",
                "description": "Get customers with MRR above threshold",
                "requires_amount": True
            },
            {
                "patterns": [
                    "customers in plan",
                    "subscriptions with plan type",
                    "who has plan",
                    "show me plan"
                ],
                "sql_template": "SELECT * FROM `{table_ref}` WHERE LOWER(plan_tier) LIKE '%{plan}%'",
                "description": "Get customers by plan type",
                "requires_plan": True
            }
        ]
        
        return templates
    
    def _train_vectorizer(self):
        """Train TF-IDF vectorizer on query patterns"""
        all_patterns = []
        for template in self.query_templates:
            all_patterns.extend(template["patterns"])
        
        self.vectorizer.fit(all_patterns)
        self.pattern_vectors = self.vectorizer.transform(all_patterns)
        
        # Create mapping from pattern to template
        self.pattern_to_template = {}
        idx = 0
        for template in self.query_templates:
            for pattern in template["patterns"]:
                self.pattern_to_template[idx] = template
                idx += 1
    
    def _extract_entities(self, query: str) -> Dict:
        """Extract entities from query (amounts, plan types, etc.)"""
        entities = {}
        
        # Extract numeric amounts
        amount_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', query)
        if amount_match:
            entities['amount'] = float(amount_match.group(1).replace(',', ''))
        
        # Extract plan types (common plan names)
        plan_keywords = ['basic', 'premium', 'enterprise', 'pro', 'starter', 'business', 'free']
        for keyword in plan_keywords:
            if keyword in query.lower():
                entities['plan'] = keyword
                break
        
        return entities
    
    def find_best_template(self, user_query: str) -> Tuple[Optional[Dict], float]:
        """Find the best matching SQL template for user query"""
        query_vector = self.vectorizer.transform([user_query.lower()])
        similarities = cosine_similarity(query_vector, self.pattern_vectors)[0]
        
        best_idx = np.argmax(similarities)
        best_score = similarities[best_idx]
        
        if best_score > 0.1:  # Threshold for matching
            return self.pattern_to_template[best_idx], best_score
        
        return None, 0.0
    
    def generate_sql(self, user_query: str) -> Tuple[Optional[str], str, Dict]:
        """Generate SQL query from natural language"""
        # Find best matching template
        template, confidence = self.find_best_template(user_query)
        
        if template is None:
            return None, "I couldn't understand your query. Please try rephrasing.", {}
        
        # Extract entities if needed
        entities = self._extract_entities(user_query)
        
        # Check if required entities are present
        if template.get('requires_amount') and 'amount' not in entities:
            return None, "Please specify an amount (e.g., 'more than $1000')", {}
        
        if template.get('requires_plan') and 'plan' not in entities:
            return None, "Please specify a plan type (e.g., 'basic', 'premium', 'enterprise')", {}
        
        # Generate SQL from template
        sql_query = template['sql_template'].format(
            table_ref=self.schema_info['table_ref'],
            amount=entities.get('amount', 0),
            plan=entities.get('plan', '')
        )
        
        return sql_query, template['description'], {"confidence": confidence, "entities": entities}
    
    def execute_query(self, sql_query: str) -> Tuple[pd.DataFrame, str]:
        """Execute SQL query on BigQuery"""
        try:
            query_job = self.client.query(sql_query)
            df = query_job.to_dataframe()
            return df, "success"
        except Exception as e:
            error_msg = f"Error executing query: {str(e)}"
            print(error_msg)
            return pd.DataFrame(), error_msg
    
    def process_user_query(self, user_query: str) -> Dict:
        """Process user query end-to-end: NL -> SQL -> Execute -> Results"""
        # Generate SQL
        sql_query, description, metadata = self.generate_sql(user_query)
        
        if sql_query is None:
            return {
                "success": False,
                "message": description,
                "sql": None,
                "results": None,
                "metadata": metadata
            }
        
        # Execute query
        results_df, status = self.execute_query(sql_query)
        
        if status == "success":
            return {
                "success": True,
                "message": description,
                "sql": sql_query,
                "results": results_df,
                "metadata": metadata
            }
        else:
            return {
                "success": False,
                "message": status,
                "sql": sql_query,
                "results": None,
                "metadata": metadata
            }
    
    def get_schema_description(self) -> str:
        """Get human-readable schema description"""
        columns = self.schema_info['columns']
        desc = f"**Available Data Columns:**\n\n"
        for col in columns:
            col_type = self.schema_info['column_types'].get(col, 'UNKNOWN')
            desc += f"- `{col}` ({col_type})\n"
        return desc
    
    def get_example_queries(self) -> List[str]:
        """Get list of example queries users can ask"""
        examples = [
            "How many customers do we have?",
            "What is the total revenue?",
            "Show me high-risk customers",
            "List customers by plan type",
            "Who are our top 10 customers?",
            "What is the churn rate?",
            "Show me customers spending more than $500",
            "Get customers in premium plan",
            "Show new customers this month",
            "What is the monthly revenue trend?"
        ]
        return examples


def format_query_results(results_df: pd.DataFrame, query_type: str = "table") -> str:
    """Format query results for display"""
    if results_df is None or results_df.empty:
        return "No results found."
    
    # For single value results
    if len(results_df) == 1 and len(results_df.columns) == 1:
        value = results_df.iloc[0, 0]
        return f"**Result:** {value:,.2f}" if isinstance(value, (int, float)) else f"**Result:** {value}"
    
    # For summary results (like count, sum, avg)
    if len(results_df) == 1:
        result_text = "**Results:**\n\n"
        for col in results_df.columns:
            value = results_df[col].iloc[0]
            if isinstance(value, (int, float)):
                result_text += f"- **{col}:** {value:,.2f}\n"
            else:
                result_text += f"- **{col}:** {value}\n"
        return result_text
    
    # For tabular results
    return results_df
