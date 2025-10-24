# Natural Language to SQL RAG - Visual Guide

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                               │
│                     (Streamlit Web App)                              │
│                                                                      │
│  ┌────────────────┐  ┌─────────────────┐  ┌───────────────────┐   │
│  │ Text Input Box │  │ Example Queries │  │  Schema Viewer    │   │
│  │ "How many      │  │ - Count         │  │  - account_id     │   │
│  │  customers?"   │  │ - Revenue       │  │  - mrr_amount     │   │
│  └────────┬───────┘  │ - Churn rate    │  │  - plan_tier      │   │
│           │          └─────────────────┘  └───────────────────┘   │
│           ▼                                                         │
│  ┌────────────────────────────────────────────────────────┐        │
│  │              Execute Query Button                       │        │
│  └────────────────────┬───────────────────────────────────┘        │
└─────────────────────────┼──────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    NL-TO-SQL RAG ENGINE                              │
│                   (nl_to_sql_rag.py)                                 │
│                                                                      │
│  Step 1: PREPROCESSING                                              │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ "How many customers do we have?"                        │        │
│  │      ↓ Clean & normalize                                │        │
│  │ "how many customers do we have"                         │        │
│  └────────────────┬───────────────────────────────────────┘        │
│                   │                                                  │
│  Step 2: VECTORIZATION (TF-IDF)                                     │
│  ┌────────────────▼───────────────────────────────────────┐        │
│  │ User Query → [0.23, 0.45, 0.12, ..., 0.67]             │        │
│  │                                                          │        │
│  │ Template 1: "how many customers" → [0.89, 0.12, ...]   │        │
│  │ Template 2: "total revenue" → [0.05, 0.78, ...]        │        │
│  │ Template 3: "churn rate" → [0.11, 0.34, ...]           │        │
│  │ ... (16 templates total)                                │        │
│  └────────────────┬───────────────────────────────────────┘        │
│                   │                                                  │
│  Step 3: SIMILARITY MATCHING (Cosine Similarity)                    │
│  ┌────────────────▼───────────────────────────────────────┐        │
│  │ Compare user vector with all template vectors           │        │
│  │                                                          │        │
│  │ Template 1: 90.53% match ✓ BEST MATCH                  │        │
│  │ Template 2: 23.45% match                                │        │
│  │ Template 3: 15.67% match                                │        │
│  │ ...                                                      │        │
│  └────────────────┬───────────────────────────────────────┘        │
│                   │                                                  │
│  Step 4: ENTITY EXTRACTION                                          │
│  ┌────────────────▼───────────────────────────────────────┐        │
│  │ Scan query for:                                         │        │
│  │ - Numbers: $1000, 500, 1,234.56                        │        │
│  │ - Plan types: basic, premium, enterprise               │        │
│  │ - Dates: "this month", "last 30 days"                  │        │
│  │                                                          │        │
│  │ Found: {} (no parameters for this query)               │        │
│  └────────────────┬───────────────────────────────────────┘        │
│                   │                                                  │
│  Step 5: SQL GENERATION                                             │
│  ┌────────────────▼───────────────────────────────────────┐        │
│  │ Template SQL:                                           │        │
│  │ "SELECT COUNT(DISTINCT account_id)                      │        │
│  │  FROM `{table_ref}`"                                    │        │
│  │      ↓ Populate variables                               │        │
│  │ "SELECT COUNT(DISTINCT account_id)                      │        │
│  │  FROM `hackathon-475722.saas.ravenstack_subscriptions`"│        │
│  └────────────────┬───────────────────────────────────────┘        │
└────────────────────┼──────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      BIGQUERY EXECUTION                              │
│                                                                      │
│  ┌────────────────────────────────────────────────────────┐        │
│  │  Google Cloud BigQuery                                  │        │
│  │  ┌──────────────────────────────────────────────┐      │        │
│  │  │ Table: hackathon-475722.saas.                │      │        │
│  │  │        ravenstack_subscriptions              │      │        │
│  │  │                                               │      │        │
│  │  │ Rows: 500 subscriptions                      │      │        │
│  │  │ Columns: account_id, mrr_amount, plan_tier  │      │        │
│  │  └──────────────┬───────────────────────────────┘      │        │
│  │                 │ Execute SQL                            │        │
│  │                 ▼                                        │        │
│  │  ┌──────────────────────────────────────────────┐      │        │
│  │  │ Result: 500 distinct customers                │      │        │
│  │  └──────────────┬───────────────────────────────┘      │        │
│  └─────────────────┼──────────────────────────────────────┘        │
└────────────────────┼──────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESULT FORMATTING                                 │
│                                                                      │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ Detect result type:                                     │        │
│  │ - Single value? → Format as metric card                │        │
│  │ - Multiple rows? → Format as table                     │        │
│  │ - Grouped data? → Add chart options                    │        │
│  │                                                          │        │
│  │ Result: Single value (500)                              │        │
│  │ Format: Metric card "Result: 500"                       │        │
│  └────────────────┬───────────────────────────────────────┘        │
└────────────────────┼──────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    DISPLAY RESULTS                                   │
│                                                                      │
│  ┌────────────────────────────────────────────────────────┐        │
│  │ ✅ Intent: Count total customers (Confidence: 90%)     │        │
│  │                                                          │        │
│  │ 🔧 Generated SQL:                                       │        │
│  │    SELECT COUNT(DISTINCT account_id)                    │        │
│  │    FROM `hackathon-475722.saas...`                      │        │
│  │                                                          │        │
│  │ 📊 Results:                                             │        │
│  │    ┌─────────────────────┐                             │        │
│  │    │  Total Customers    │                             │        │
│  │    │       500           │  ← Large metric card        │        │
│  │    └─────────────────────┘                             │        │
│  │                                                          │        │
│  │ 📥 [Download CSV]  [Copy SQL]                          │        │
│  └────────────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────────────┘
```

## Query Flow Examples

### Example 1: Simple Count Query

```
USER INPUT: "How many customers do we have?"
    ↓
VECTORIZE: [0.23, 0.45, 0.12, 0.67, ...]
    ↓
MATCH: Template #1 "Count customers" (90.53% confidence)
    ↓
EXTRACT: No entities needed
    ↓
GENERATE SQL: SELECT COUNT(DISTINCT account_id) FROM table
    ↓
EXECUTE: BigQuery returns 500
    ↓
FORMAT: "Result: 500"
    ↓
DISPLAY: Metric card with value
```

### Example 2: Filtered Query with Entity

```
USER INPUT: "Show me customers spending more than $1000"
    ↓
VECTORIZE: [0.15, 0.67, 0.23, 0.89, ...]
    ↓
MATCH: Template #14 "Customers with MRR above threshold" (87.78%)
    ↓
EXTRACT: amount = 1000.0
    ↓
GENERATE SQL: SELECT * FROM table WHERE mrr_amount > 1000 
              ORDER BY mrr_amount DESC
    ↓
EXECUTE: BigQuery returns 45 rows
    ↓
FORMAT: DataFrame with columns [account_id, mrr_amount, plan_tier, ...]
    ↓
DISPLAY: Interactive table + bar chart option
```

### Example 3: Grouped Query with Visualization

```
USER INPUT: "List customers by plan type"
    ↓
VECTORIZE: [0.34, 0.12, 0.78, 0.45, ...]
    ↓
MATCH: Template #8 "Group by plan type" (71.28%)
    ↓
EXTRACT: No entities needed
    ↓
GENERATE SQL: SELECT plan_tier, COUNT(*), SUM(mrr_amount)
              FROM table GROUP BY plan_tier
              ORDER BY SUM(mrr_amount) DESC
    ↓
EXECUTE: BigQuery returns 3 rows:
         Basic: 150 customers, $30,000
         Premium: 200 customers, $80,000
         Enterprise: 150 customers, $90,000
    ↓
FORMAT: DataFrame with aggregated data
    ↓
DISPLAY: Table + Auto-generated bar chart showing revenue by plan
```

## Component Interactions

```
┌──────────────────┐
│  Streamlit UI    │ ← User interacts here
└────────┬─────────┘
         │ calls
         ▼
┌──────────────────┐
│ NLtoSQLRAG       │ ← Main RAG engine
│  .process_query()│
└────────┬─────────┘
         │ uses
         ├──→ ┌─────────────────┐
         │    │ TfidfVectorizer │ ← Converts text to vectors
         │    └─────────────────┘
         │
         ├──→ ┌─────────────────┐
         │    │ Cosine Similarity│ ← Matches templates
         │    └─────────────────┘
         │
         ├──→ ┌─────────────────┐
         │    │ Entity Extractor│ ← Finds amounts, plans
         │    └─────────────────┘
         │
         └──→ ┌─────────────────┐
              │ BigQuery Client │ ← Executes SQL
              └─────────────────┘
```

## Data Flow Diagram

```
┌──────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│  Query   │ --> │  Vector  │ --> │   SQL    │ --> │  Result  │
│ "How     │     │ [0.23,   │     │ SELECT   │     │   500    │
│  many    │     │  0.45,   │     │ COUNT... │     │          │
│  cust?"  │     │  ...]    │     │          │     │          │
└──────────┘     └──────────┘     └──────────┘     └──────────┘
     │                │                 │                │
     │                │                 │                │
     └────────┬───────┴────────┬────────┴────────┬───────┘
              │                │                 │
         Preprocessing   Matching &          Execution &
         & Extraction    Generation          Formatting
```

## Template Matching Visualization

```
User Query: "How many customers?"
      ↓
[Vectorize into 500 dimensions]
      ↓
Compare with 16 templates:

Template 1: "Count customers"
Vector: [0.89, 0.12, 0.34, ...]
Similarity: ████████████████████ 90.53% ✓ SELECTED

Template 2: "Total revenue"
Vector: [0.05, 0.78, 0.11, ...]
Similarity: ████░░░░░░░░░░░░░░░░ 23.45%

Template 3: "Churn rate"
Vector: [0.11, 0.34, 0.67, ...]
Similarity: ███░░░░░░░░░░░░░░░░░ 15.67%

[... 13 more templates ...]

Best match: Template 1 (Count customers)
Confidence: 90.53%
SQL: SELECT COUNT(DISTINCT account_id) FROM table
```

## Entity Extraction Process

```
Input: "Show me customers spending more than $1,234.56 in premium plan"
              ↓
    ┌─────────┴──────────┐
    │                    │
    ▼                    ▼
[Number Pattern]    [Plan Pattern]
"$1,234.56"         "premium"
    ↓                    ↓
Parse & Clean       Normalize
1234.56             "premium"
    ↓                    ↓
    └─────────┬──────────┘
              ▼
Entities: {
  "amount": 1234.56,
  "plan": "premium"
}
              ↓
SQL: SELECT * FROM table 
     WHERE mrr_amount > 1234.56 
     AND LOWER(plan_tier) LIKE '%premium%'
```

## Visualization Selection Logic

```
Query Result
     ↓
┌────┴────┐
│ Analyze │
│ Result  │
└────┬────┘
     │
     ├─→ Single value? ──→ Metric Card
     │                     ┌───────────┐
     │                     │   500     │
     │                     └───────────┘
     │
     ├─→ Single row, multiple columns? ──→ Multiple Metrics
     │                                     ┌────┬────┬────┐
     │                                     │100 │200 │20% │
     │                                     └────┴────┴────┘
     │
     ├─→ Multiple rows, grouped data? ──→ Bar/Pie Chart
     │                                    ┌─────────────┐
     │                                    │ ▓▓▓▓▓       │
     │                                    │ ▓▓▓▓▓▓▓▓    │
     │                                    │ ▓▓▓▓▓▓▓▓▓▓  │
     │                                    └─────────────┘
     │
     └─→ Time series data? ──→ Line Chart
                              ┌─────────────┐
                              │    ╱╲  ╱╲   │
                              │   ╱  ╲╱  ╲  │
                              └─────────────┘
```

## Complete User Journey

```
1. User opens Streamlit app
   ↓
2. Clicks "Query Data with Natural Language"
   ↓
3. Sees interface with:
   - Text input box
   - Example queries (clickable)
   - Schema viewer
   ↓
4. Types or clicks: "How many customers?"
   ↓
5. Clicks "Execute Query"
   ↓
6. System shows:
   ✅ Understanding: "Count customers (90% confident)"
   🔧 SQL: "SELECT COUNT(DISTINCT account_id)..."
   ↓
7. BigQuery executes query
   ↓
8. System shows:
   📊 Result: 500 (in large metric card)
   📥 Download button
   ↓
9. User can:
   - Try another query
   - Download results
   - Copy SQL
   - View different visualizations
```

## Error Handling Flow

```
User Query
     ↓
 Valid query?
     ├─→ No ──→ Show error + suggestions
     │         "I couldn't understand..."
     │         Suggestions:
     │         - How many customers?
     │         - What is total revenue?
     │
     └─→ Yes ──→ Continue to matching
                      ↓
              High confidence?
                      ├─→ No ──→ Show alternatives
                      │         "Did you mean...?"
                      │
                      └─→ Yes ──→ Generate SQL
                                      ↓
                              Parameters complete?
                                      ├─→ No ──→ Ask for params
                                      │         "Please specify amount"
                                      │
                                      └─→ Yes ──→ Execute query
                                                      ↓
                                              Query success?
                                                      ├─→ No ──→ Show error
                                                      │         + SQL for debug
                                                      │
                                                      └─→ Yes ──→ Show results!
```

---

**This visual guide helps understand the complete flow from user input to result display!** 🎯
