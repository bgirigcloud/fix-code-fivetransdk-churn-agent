# AI Chatbot Assistant - Configuration Guide

## Overview

The AI Chatbot Assistant provides intelligent, context-aware responses about your churn prediction system using Google's Generative AI (Gemini).

## Features

### Intelligent Responses
- Analyzes current prediction data to provide context-aware answers
- Explains churn probabilities and risk levels
- Describes model insights and SHAP explanations
- Suggests retention strategies for at-risk customers
- Helps formulate data queries

### Conversation Memory
- Maintains chat history within session
- Provides contextual follow-up responses
- Allows conversation reset

### Quick Actions
- Pre-configured buttons for common questions
- One-click access to high-risk customer analysis
- Instant model explanations
- Revenue-at-risk calculations

## Setup Instructions

### Option 1: Use Fallback Mode (No API Key Required)

The chatbot works out-of-the-box with intelligent rule-based responses. No configuration needed.

```python
# In app.py, the chatbot is initialized with use_gemini=False by default
chatbot = ChurnChatbot(project_id=PROJECT_ID, use_gemini=False)
```

### Option 2: Enable Google Gemini API (Recommended)

For enhanced AI-powered responses using Google's Gemini model:

#### Step 1: Get Google API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

#### Step 2: Configure API Key

**For Local Development:**

Set environment variable:

**Windows:**
```bash
set GOOGLE_API_KEY=your-api-key-here
```

**Linux/Mac:**
```bash
export GOOGLE_API_KEY=your-api-key-here
```

**For Streamlit Cloud Deployment:**

1. Go to your app settings in Streamlit Cloud
2. Navigate to "Secrets" section
3. Add:
```toml
GOOGLE_API_KEY = "your-api-key-here"
```

**For Local Streamlit Secrets:**

Create `.streamlit/secrets.toml`:
```toml
GOOGLE_API_KEY = "your-api-key-here"
```

#### Step 3: Enable Gemini in Code

Update the chatbot initialization in `app.py`:

```python
@st.cache_resource
def get_chatbot():
    """Initialize and cache the chatbot assistant."""
    return ChurnChatbot(project_id=PROJECT_ID, use_gemini=True)  # Changed to True
```

#### Step 4: Install Dependencies

```bash
pip install google-generativeai
```

Or use the provided requirements.txt:
```bash
pip install -r requirements.txt
```

## Usage

### Opening the Chat Interface

1. Click the "💬 AI Assistant Chat" button in the sidebar
2. The chat interface appears at the bottom of the page
3. Click again to hide the chat

### Asking Questions

**Type Your Question:**
```
Which customers are most likely to churn?
How does the model make predictions?
Show me revenue at risk
What actions should I take for high-risk customers?
```

**Use Quick Action Buttons:**
- "📊 Show high-risk customers"
- "🎯 Explain the model"
- "💰 Revenue at risk"

### Example Conversations

**Churn Analysis:**
```
User: Which customers have the highest churn risk?
Assistant: Based on current predictions, customer CUST_12345 has the highest 
churn risk with 87% probability. They are on the Pro plan with $850 MRR.

Recommended Actions:
1. Schedule immediate outreach from customer success team
2. Review their recent product usage and engagement
3. Consider personalized retention offer
```

**Model Explanation:**
```
User: How does the model work?
Assistant: The churn prediction system uses a RandomForest Classifier with 
85% accuracy. It analyzes 16 features including MRR, seats, tenure, and plan 
changes. Every prediction includes SHAP explanations showing which features 
increased or decreased churn risk.
```

**Revenue Impact:**
```
User: How much revenue is at risk?
Assistant: Current Revenue Analysis:
- Total MRR: $125,450
- At-risk MRR: $18,200 (14.5% of total)
- At-risk ARR: $218,400

Recommendation: Focus retention efforts on high-value at-risk customers.
```

## Chatbot Capabilities

### What the Chatbot Understands

1. **Churn Predictions**
   - Risk levels and probabilities
   - Customer identification
   - Segment analysis

2. **Model Insights**
   - Algorithm explanations
   - Feature importance
   - SHAP value interpretations

3. **Revenue Analysis**
   - MRR/ARR calculations
   - At-risk revenue quantification
   - ROI projections

4. **Data Queries**
   - Help formulating questions
   - Query suggestions
   - Result interpretations

5. **Action Recommendations**
   - Retention strategies
   - Intervention prioritization
   - Campaign suggestions

### Current Data Context

The chatbot automatically accesses:
- Total customer count
- Predicted churners
- Risk level distribution
- Plan tier breakdown
- At-risk revenue totals

This ensures all responses are grounded in your actual data.

## API Costs and Limits

### Google Gemini API (Free Tier)

- **Free Quota:** 60 requests per minute
- **Cost:** Free for first 60 requests/min, then $0.00025 per 1K characters
- **Context Window:** 30K tokens
- **Best For:** Production deployments with moderate usage

### Fallback Mode

- **Cost:** $0 (uses rule-based responses)
- **Limits:** None
- **Best For:** Development, testing, cost-sensitive deployments

## Troubleshooting

### Issue: "GOOGLE_API_KEY not found"

**Solution:** 
- Verify environment variable is set
- Check Streamlit secrets configuration
- Ensure no typos in variable name

### Issue: API rate limit exceeded

**Solution:**
- Wait 60 seconds for quota reset
- Reduce request frequency
- Consider upgrading API tier

### Issue: Generic responses instead of data-specific

**Solution:**
- Ensure predictions exist in BigQuery
- Check data_handler connection
- Verify PROJECT_ID configuration

### Issue: Chat history not persisting

**Solution:**
- Chat history is session-based (intentional)
- Refresh clears history
- Export important conversations manually

## Best Practices

### Effective Questions

**Good:**
- "Which customers are most likely to churn this month?"
- "What features drive churn predictions the most?"
- "How much MRR is at risk from Enterprise customers?"

**Less Effective:**
- "Tell me about customers" (too vague)
- "Fix the churn" (not a question)
- "Predict everything" (too broad)

### Privacy and Security

- Never share API keys in code or commits
- Use environment variables or secrets management
- Rotate API keys regularly
- Monitor API usage for anomalies

### Performance Optimization

- Chatbot is cached (@st.cache_resource) for speed
- Responses typically take 1-3 seconds with Gemini
- Fallback mode responds instantly
- Clear chat history periodically to reduce token usage

## Advanced Configuration

### Customizing System Context

Edit `chatbot_assistant.py` to modify the system context:

```python
self.system_context = """
Your custom system instructions here...
"""
```

### Adding Custom Response Patterns

Add patterns to `_generate_fallback_response()`:

```python
if 'your_keyword' in message_lower:
    return "Your custom response"
```

### Adjusting Gemini Model

Change model in `chatbot_assistant.py`:

```python
self.model = genai.GenerativeModel('gemini-1.5-pro')  # For advanced model
```

Available models:
- `gemini-pro`: Standard (recommended)
- `gemini-1.5-pro`: Enhanced capabilities
- `gemini-pro-vision`: Image support

## Integration with Other Features

### Analytics RAG

The chatbot complements the Analytics RAG system:
- Chatbot: Conversational, explanatory responses
- Analytics RAG: Structured queries, visualizations

Use both together for comprehensive insights.

### NL-to-SQL

The chatbot can help formulate SQL queries:
```
User: How do I find customers spending over $1000?
Assistant: Use the NL-to-SQL interface and ask: "Show customers with MRR over 1000"
```

### Prediction System

Chatbot explains prediction results:
```
User: What does 78% churn probability mean?
Assistant: 78% probability indicates high risk. The model is fairly confident 
this customer will churn. SHAP values show which features contributed most.
```

## Future Enhancements

Planned features:
- Multi-turn conversations with memory across sessions
- Export chat transcripts
- Voice input/output
- Proactive alerts ("3 new high-risk customers detected")
- Integration with CRM for action execution
- Custom training on company-specific data

## Support

For issues or questions:
- Check this guide first
- Review chatbot_assistant.py code
- Test with fallback mode to isolate API issues
- Check Streamlit logs for errors

## Summary

The AI Chatbot Assistant makes your churn prediction system more accessible by:
- Answering questions in natural language
- Providing context-aware insights
- Explaining complex ML concepts simply
- Suggesting actionable retention strategies

Start with fallback mode for development, then enable Gemini for production deployment.
