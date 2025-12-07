# IssueSense AI - Installation & Setup Guide

## Prerequisites

- Python 3.9 or higher
- GitHub Personal Access Token
- OpenAI API Key

## Step 1: Clone or Navigate to Project

```bash
cd /Users/sanjana/Desktop/IssuePilot
```

## Step 2: Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Set Up Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your credentials:
   ```
   GITHUB_TOKEN=your_github_token_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Getting Credentials

#### GitHub Token
1. Go to https://github.com/settings/tokens
2. Click "Generate new token"
3. Select scopes: `repo`, `read:user`
4. Copy the token to `.env`

#### OpenAI API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy the key to `.env`

## Step 5: Run the Application

### Option A: Run Both Services (Recommended)

Terminal 1 - Backend:
```bash
python -m uvicorn backend.main:app --reload --host localhost --port 8000
```

Terminal 2 - Frontend:
```bash
streamlit run frontend/app.py
```

The Streamlit app will open at `http://localhost:8501`

### Option B: Run Individually

**Backend only:**
```bash
python -m uvicorn backend.main:app --reload
```

**Frontend only:**
```bash
streamlit run frontend/app.py -- --backend-url http://localhost:8000
```

## API Documentation

Once the backend is running, visit:
- **Interactive Docs:** http://localhost:8000/docs
- **Alternative Docs:** http://localhost:8000/redoc

## Usage

### Through Streamlit UI
1. Enter repository URL (format: `owner/repo`)
2. Enter issue number
3. Click "Analyze Issue"
4. View comprehensive analysis including:
   - Issue summary
   - Type classification
   - Priority score with justification
   - Suggested labels
   - Potential impact

### Through API Directly

```bash
curl -X POST "http://localhost:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "torvalds/linux",
    "issue_number": 12345
  }'
```

### Batch Analysis

```bash
curl -X POST "http://localhost:8000/batch-analyze" \
  -H "Content-Type: application/json" \
  -d '[
    {"repo_url": "owner/repo1", "issue_number": 1},
    {"repo_url": "owner/repo2", "issue_number": 2}
  ]'
```

## Project Structure

```
IssuePilot/
├── backend/
│   ├── __init__.py
│   ├── config.py              # Environment configuration
│   ├── github_client.py        # GitHub API wrapper
│   ├── context_enricher.py     # Context enrichment logic
│   ├── llm_analyzer.py         # OpenAI integration
│   ├── models.py               # Pydantic models
│   └── main.py                 # FastAPI application
├── frontend/
│   ├── __init__.py
│   ├── app.py                  # Streamlit UI
│   └── styles.py               # UI styling utilities
├── requirements.txt            # Dependencies
├── .env.example               # Environment template
├── .gitignore                 # Git ignore patterns
└── README.md                  # Project overview
```

## How It Works

### 1. Issue Fetching
- Retrieves GitHub issue details via GitHub API
- Gathers all comments and metadata

### 2. Context Enrichment
- Identifies linked issues and pull requests
- Extracts files changed in linked PRs
- Gathers recent commits touching affected files
- Extracts stack traces and error messages

### 3. LLM Analysis
- Builds comprehensive prompt with all context
- Sends to OpenAI's Chat Completions API
- Requests structured JSON output
- Validates and sanitizes response

### 4. Result Formatting
- Returns structured analysis with:
  - One-sentence summary
  - Issue type (bug, feature, documentation, question, other)
  - Priority score (1-5) with justification
  - Suggested labels (2-3 relevant ones)
  - Potential impact description

## Troubleshooting

### "Cannot connect to backend"
- Ensure backend is running: `python -m uvicorn backend.main:app --reload`
- Check backend host/port in Streamlit sidebar

### "GITHUB_TOKEN environment variable is not set"
- Create `.env` file from `.env.example`
- Add valid GitHub token to `.env`

### "OPENAI_API_KEY environment variable is not set"
- Add valid OpenAI API key to `.env`

### Rate Limiting Issues
- GitHub API: Implement exponential backoff or increase rate limits
- OpenAI API: Monitor usage in https://platform.openai.com/usage

### Stack Trace Not Extracted
- Not all issues contain stack traces
- Common in feature requests and questions

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| GITHUB_TOKEN | ✅ | - | GitHub Personal Access Token |
| GEMINI_API_KEY | ✅ | - | Gemini API Key |
| GITHUB_API_BASE_URL | ❌ | https://api.github.com | GitHub API endpoint |
| OPENAI_MODEL | ❌ | gpt-4-turbo-preview | LLM model to use |
| BACKEND_HOST | ❌ | localhost | Backend server host |
| BACKEND_PORT | ❌ | 8000 | Backend server port |

## Performance Considerations

- **Context Enrichment:** Fetches multiple API calls, may take 30-60 seconds
- **LLM Analysis:** OpenAI response time depends on model and prompt size
- **Total Time:** Typically 1-3 minutes per issue

## API Response Format

```json
{
  "summary": "User reports login fails with incorrect error message",
  "type": "bug",
  "priority_score": {
    "score": 4,
    "justification": "Blocks user authentication, affecting many users"
  },
  "suggested_labels": ["bug", "authentication", "high-priority"],
  "potential_impact": "Users unable to access the application"
}
```

## Next Steps

1. Configure your `.env` with credentials
2. Run the backend and frontend
3. Analyze your first GitHub issue!

## Support

For issues or questions:
- Check the README.md
- Review API docs at `/docs`
- Check backend logs for detailed error messages

---

**Happy issue analyzing! 🚀**
