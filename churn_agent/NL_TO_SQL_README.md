# Natural Language to SQL RAG Interface

## Overview

The **NL-to-SQL RAG (Retrieval-Augmented Generation) Interface** allows users to query BigQuery data using plain English questions. The system automatically translates natural language queries into SQL, executes them on BigQuery, and presents results with intelligent visualizations.

## Features

### 🤖 Natural Language Understanding
- **Semantic Query Matching**: Uses TF-IDF vectorization and cosine similarity to understand user intent
- **Entity Extraction**: Automatically extracts parameters like amounts, plan types, dates
- **Confidence Scoring**: Provides confidence scores for query understanding
- **16 Pre-defined Query Templates**: Covers common analytics questions

### 🔍 Supported Query Types

#### 1. **Counting Queries**
- "How many customers do we have?"
- "What is the total number of subscriptions?"
- "Count active customers"

#### 2. **Revenue Queries**
- "What is the total revenue?"
- "Show me average MRR per customer"
- "What is monthly recurring revenue?"

#### 3. **Churn Analysis**
- "Show me churned customers"
- "What is the churn rate?"
- "Who cancelled their subscriptions?"

#### 4. **Risk Assessment**
- "Show me high-risk customers"
- "List customers likely to churn"
- "Get at-risk accounts"

#### 5. **Segmentation**
- "Group customers by plan type"
- "Show subscriptions by plan"
- "Breakdown revenue by plan"

#### 6. **Top Customers**
- "Who are our top 10 customers?"
- "Show highest paying customers"
- "List best customers by revenue"

#### 7. **Time-based Queries**
- "Show new customers this month"
- "What is the monthly revenue trend?"
- "Revenue by month"

#### 8. **Filtered Queries**
- "Show me customers spending more than $500"
- "Get customers in premium plan"
- "Who has enterprise plan?"

#### 9. **Tenure Analysis**
- "Show customers by tenure"
- "Who are our long-term customers?"
- "List customer tenure"

#### 10. **General Data Retrieval**
- "Show me all customers"
- "Get all subscription data"
- "List all records"

## Architecture

```
User Query (Plain English)
    ↓
[Query Preprocessing]
    ↓
[TF-IDF Vectorization]
    ↓
[Similarity Matching] → Find Best Template
    ↓
[Entity Extraction] → Extract Parameters
    ↓
[SQL Generation] → Populate Template
    ↓
[BigQuery Execution]
    ↓
[Result Formatting]
    ↓
[Auto-Visualization]
    ↓
User Interface Display
```

## Components

### 1. **NLtoSQLRAG Class** (`nl_to_sql_rag.py`)

Main RAG system with the following methods:

- `__init__(project_id, dataset_id, table_id)`: Initialize with BigQuery connection
- `generate_sql(user_query)`: Translate natural language to SQL
- `execute_query(sql_query)`: Execute SQL on BigQuery
- `process_user_query(user_query)`: End-to-end processing
- `get_schema_description()`: Get table schema info
- `get_example_queries()`: Get example questions

### 2. **Query Templates**

Each template contains:
- **Patterns**: List of natural language variations
- **SQL Template**: Parameterized SQL query
- **Description**: Human-readable intent
- **Requirements**: Optional parameters (amount, plan, etc.)

Example template:
```python
{
    "patterns": [
        "how many customers",
        "total customers",
        "customer count"
    ],
    "sql_template": "SELECT COUNT(DISTINCT customer_id) as total_customers FROM `{table_ref}`",
    "description": "Count total customers"
}
```

### 3. **Entity Extraction**

Extracts parameters from queries:
- **Amounts**: `$1000`, `500`, `1,234.56`
- **Plan Types**: `basic`, `premium`, `enterprise`, `pro`
- **Dates**: Implicit (e.g., "this month", "last 30 days")

### 4. **Streamlit Integration** (`app.py`)

Features:
- **Interactive Query Interface**: Text area for user input
- **Example Queries**: Clickable examples
- **Schema Viewer**: Shows available columns
- **SQL Display**: Shows generated SQL
- **Results Viewer**: Interactive dataframe
- **Auto-Visualizations**: Charts based on result type
- **CSV Export**: Download query results

## Usage

### Basic Usage in Code

```python
from nl_to_sql_rag import NLtoSQLRAG

# Initialize
rag = NLtoSQLRAG(
    project_id="your-project-id",
    dataset_id="your-dataset",
    table_id="your-table"
)

# Process a query
result = rag.process_user_query("How many customers do we have?")

if result['success']:
    print(f"SQL: {result['sql']}")
    print(f"Results: {result['results']}")
else:
    print(f"Error: {result['message']}")
```

### Using in Streamlit App

1. **Open Interface**: Click "🔍 Query Data with Natural Language" in sidebar
2. **View Schema**: Expand "📊 View Available Data Schema" to see columns
3. **Try Examples**: Click any example query or type your own
4. **Execute**: Click "🚀 Execute Query"
5. **View Results**: See SQL, results table, and auto-generated charts
6. **Export**: Download results as CSV

## Example Queries

### Simple Counts
```
Q: "How many customers do we have?"
SQL: SELECT COUNT(DISTINCT customer_id) as total_customers FROM `project.dataset.table`
```

### Revenue Analysis
```
Q: "What is the total revenue?"
SQL: SELECT SUM(mrr) as total_mrr FROM `project.dataset.table` WHERE status = 'active'
```

### Risk Assessment
```
Q: "Show me high-risk customers"
SQL: SELECT * FROM `project.dataset.table` 
     WHERE churn_risk > 0.7 AND status = 'active' 
     ORDER BY churn_risk DESC
```

### Filtered Queries
```
Q: "Show me customers spending more than $500"
SQL: SELECT * FROM `project.dataset.table` 
     WHERE mrr > 500 AND status = 'active' 
     ORDER BY mrr DESC
```

### Segmentation
```
Q: "Group customers by plan type"
SQL: SELECT plan_type, COUNT(*) as count, SUM(mrr) as total_mrr 
     FROM `project.dataset.table` 
     WHERE status = 'active' 
     GROUP BY plan_type 
     ORDER BY total_mrr DESC
```

## Configuration

### Environment Variables

```bash
# Set Google Cloud credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/key.json"

# Or in code
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"
```

### BigQuery Setup

Ensure your BigQuery table has these columns (or adjust templates):
- `customer_id`: Unique customer identifier
- `subscription_id`: Subscription identifier
- `mrr`: Monthly recurring revenue
- `status`: Subscription status (active, cancelled, churned)
- `plan_type`: Plan tier (basic, premium, etc.)
- `churn_risk`: Predicted churn probability (0-1)
- `start_date`: Subscription start date
- `tenure_months`: Customer tenure in months

## Visualizations

The system automatically generates visualizations based on query results:

### Single Metric Results
- Displayed as large metric cards
- Example: "Total Customers: 1,234"

### Grouped Results (Bar Chart)
- Revenue by plan type
- Customer count by status
- Monthly trends

### Time Series (Line Chart)
- Monthly revenue trends
- Churn rate over time
- Growth metrics

### Distributions (Pie Chart)
- Plan type distribution
- Revenue distribution
- Status breakdown

### Detailed Results (Table)
- Customer lists
- Detailed subscription data
- With sortable columns and search

## Error Handling

### Query Understanding Errors
```
❌ I couldn't understand your query. Please try rephrasing.
Suggestions:
- How many customers do we have?
- What is the total revenue?
- Show me high-risk customers
```

### Missing Parameters
```
❌ Please specify an amount (e.g., 'more than $1000')
```

### Execution Errors
```
❌ Error executing query: [BigQuery error message]
```

## Testing

Run the test suite:
```bash
cd churn_agent
python test_nl_to_sql.py
```

Test coverage:
- ✓ System initialization
- ✓ Schema fetching
- ✓ Query translation (10 test queries)
- ✓ Entity extraction
- ✓ SQL generation
- ✓ End-to-end execution

## Performance

### Query Translation
- **Speed**: < 100ms for query understanding
- **Accuracy**: ~90% for pre-defined patterns
- **Confidence**: Scores provided for each match

### SQL Execution
- **Speed**: Depends on BigQuery performance
- **Optimization**: Queries include LIMIT clauses where appropriate
- **Caching**: Streamlit caches RAG system initialization

## Extending the System

### Adding New Query Templates

Edit `nl_to_sql_rag.py`:

```python
{
    "patterns": [
        "your pattern 1",
        "your pattern 2"
    ],
    "sql_template": "SELECT ... FROM `{table_ref}` WHERE ...",
    "description": "What this query does",
    "requires_custom_param": True  # Optional
}
```

### Adding Custom Entity Extractors

Add to `_extract_entities()` method:

```python
def _extract_entities(self, query: str) -> Dict:
    entities = {}
    
    # Add custom extraction logic
    if "your_pattern" in query.lower():
        entities['your_param'] = extracted_value
    
    return entities
```

### Custom Visualizations

Modify the visualization section in `app.py`:

```python
if "your_condition" in result:
    # Add custom chart
    fig = px.your_chart_type(...)
    st.plotly_chart(fig)
```

## Best Practices

### For Users

1. **Be Specific**: "Show customers spending more than $500" vs "show customers"
2. **Use Examples**: Start with example queries to understand capabilities
3. **Check SQL**: Review generated SQL before trusting results
4. **Iterate**: If query fails, rephrase or check schema

### For Developers

1. **Test New Templates**: Use `test_nl_to_sql.py` to validate
2. **Monitor Confidence**: Low confidence scores indicate need for more patterns
3. **Handle Edge Cases**: Add error handling for unexpected inputs
4. **Document Patterns**: Keep query templates well-documented
5. **Optimize SQL**: Ensure generated queries are efficient

## Troubleshooting

### Issue: "Could not initialize RAG system"
**Solution**: Check BigQuery credentials and project ID

### Issue: "No results found"
**Solution**: Verify table has data and column names match

### Issue: "Low confidence scores"
**Solution**: Add more pattern variations to templates

### Issue: "Entity not extracted"
**Solution**: Check entity extraction regex patterns

### Issue: "SQL execution failed"
**Solution**: Check BigQuery permissions and table access

## Future Enhancements

- [ ] Support for JOIN queries across multiple tables
- [ ] Date range parsing (e.g., "last quarter", "this year")
- [ ] Advanced aggregations (PERCENTILE, STDDEV)
- [ ] Query history and favorites
- [ ] Custom SQL editor mode
- [ ] Query performance analytics
- [ ] Multi-language support
- [ ] Voice input for queries
- [ ] AI-suggested follow-up questions

## API Reference

### NLtoSQLRAG

#### `__init__(project_id, dataset_id, table_id)`
Initialize RAG system with BigQuery connection.

#### `generate_sql(user_query) -> (sql, description, metadata)`
Generate SQL from natural language query.

**Returns:**
- `sql`: Generated SQL string or None
- `description`: Intent description
- `metadata`: Confidence score and entities

#### `execute_query(sql_query) -> (dataframe, status)`
Execute SQL query on BigQuery.

**Returns:**
- `dataframe`: pandas DataFrame with results
- `status`: "success" or error message

#### `process_user_query(user_query) -> dict`
End-to-end query processing.

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "sql": str,
    "results": pd.DataFrame,
    "metadata": dict
}
```

## License

Part of the Fivetran SDK Churn Agent project.

## Support

For issues or questions:
1. Check this documentation
2. Run test suite: `python test_nl_to_sql.py`
3. Review example queries
4. Check BigQuery logs for execution errors
