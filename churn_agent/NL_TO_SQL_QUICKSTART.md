# Quick Start: Natural Language to SQL Interface

## What is this?

The **Natural Language to SQL Interface** lets you query your BigQuery data using plain English. No SQL knowledge required!

## How to Use

### 1. **Start the Streamlit App**

```bash
cd churn_agent
streamlit run app.py
```

### 2. **Open the SQL Query Interface**

- Look for the sidebar on the left
- Click **"🔍 Query Data with Natural Language"**
- Click **"Open SQL Query Interface"**

### 3. **Ask Questions in Plain English**

Type any question like:
- "How many customers do we have?"
- "What is the total revenue?"
- "Show me customers spending more than $1000"
- "Get customers in premium plan"
- "What is the churn rate?"

### 4. **View Results**

The system will:
1. ✅ Understand your question
2. 🔧 Generate the SQL query
3. 📊 Execute it on BigQuery
4. 📈 Show results with auto-generated charts
5. 📥 Let you download as CSV

## Example Queries

### Simple Questions
```
Q: How many customers do we have?
A: Result: 500
```

### Revenue Questions
```
Q: What is the total revenue?
A: Shows total MRR from all subscriptions
```

### Filtered Queries
```
Q: Show me customers spending more than $500
A: Lists all customers with MRR > $500, sorted by amount
```

### Segmentation
```
Q: List customers by plan type
A: Shows breakdown: Basic (150), Premium (200), Enterprise (150)
   with revenue for each plan
```

### Churn Analysis
```
Q: What is the churn rate?
A: Churned: 100, Total: 500, Rate: 20%
```

## Features

### 🎯 Smart Understanding
- Automatically understands variations of questions
- Extracts numbers, plan names, dates from your query
- Shows confidence score for understanding

### 📊 Auto-Visualizations
- Bar charts for grouped data
- Line charts for trends
- Pie charts for distributions
- Metric cards for single values

### 💾 Export Results
- Download any query results as CSV
- Copy generated SQL for use elsewhere

### 🔍 Schema Viewer
- Click "View Available Data Schema" to see all columns
- Understand what data is available to query

## Tips

1. **Start with Examples**: Click any example query to try it out
2. **Be Specific**: "Show customers spending more than $1000" works better than "show customers"
3. **Check the SQL**: Review the generated SQL to understand what's happening
4. **Try Variations**: Multiple ways to ask the same thing work!

## Supported Query Types

✅ Counting (customers, subscriptions)  
✅ Revenue (total, average, by plan)  
✅ Churn analysis (rate, churned customers)  
✅ Filtering (by amount, by plan)  
✅ Top customers (highest revenue)  
✅ Time-based (new customers, trends)  
✅ Segmentation (by plan, by status)  

## Common Questions

**Q: What if my question isn't understood?**  
A: Try rephrasing or click an example to see what works

**Q: Can I see the SQL?**  
A: Yes! Every query shows the generated SQL

**Q: Can I modify the SQL?**  
A: Currently view-only, but you can copy it to BigQuery console

**Q: How accurate is it?**  
A: ~90% accuracy for common patterns. Shows confidence score.

## Need Help?

1. Check "Example Questions" in the interface
2. View "Available Data Schema" to see columns
3. Try one of the example queries
4. Read the full documentation: `NL_TO_SQL_README.md`

## Technical Details

- **Backend**: BigQuery
- **AI**: TF-IDF + Cosine Similarity
- **Templates**: 16 pre-defined query patterns
- **Languages**: Python, SQL

## Next Steps

Want to extend it? Check `NL_TO_SQL_README.md` for:
- Adding new query types
- Custom visualizations
- Advanced entity extraction
- API usage

---

**Happy Querying! 🚀**
