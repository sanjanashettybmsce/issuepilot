# IssuePilot

A production-style web application that analyzes GitHub issues using AI-powered context enrichment and LLM analysis.

## Features

- **GitHub Issue Analysis**: Fetches issue details and comments from GitHub API
- **Context Enrichment Engine**: Gathers linked issues, PRs, relevant files, and recent commits
- **AI-Powered Insights**: Uses Google Gemini API's Chat Completions API to analyze enriched context
- **Structured Output**: Returns analysis in a standardized JSON format
- **User-Friendly UI**: Clean Streamlit interface for input and visualization

## Screenshot

<img width="2776" height="1354" alt="image" src="https://github.com/user-attachments/assets/d3b17158-b3df-4f2e-91c0-d032041b742e" />

<img width="2814" height="1450" alt="image" src="https://github.com/user-attachments/assets/be89037d-7250-45bc-8865-eff0160ba433" />


## Project Structure

```
IssuePilot/
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── github_client.py      # GitHub API client
│   ├── context_enricher.py   # Context enrichment logic
│   ├── llm_analyzer.py       # LLM integration
│   └── models.py            # Pydantic models
└── frontend/
  ├── app.py               # Streamlit application
  └── styles.py            # UI styling
```

## Setup

1. Clone or navigate to the project directory
2. Create a `.env` file based on `.env.example`
3. Install dependencies: `pip install -r requirements.txt`
4. Run the backend: `python -m uvicorn backend.main:app --reload`
5. Run the frontend: `streamlit run frontend/app.py`

## Environment Variables

- `GITHUB_TOKEN`: Personal GitHub access token (get from https://github.com/settings/tokens)
- `GEMINI_API_KEY`: Google Gemini API key (get from https://aistudio.google.com/app/apikey)
- `GITHUB_API_BASE_URL`: GitHub API base URL (default: https://api.github.com)
- `GEMINI_MODEL`: LLM model to use (default: gemini-2.5-flash)

## API Endpoints

- `POST /analyze`: Analyze a GitHub issue
  - Request body: `{"repo_url": "owner/repo", "issue_number": 123}`
  - Response: Structured JSON analysis

## Output Format

```json
{
  "summary": "A one-sentence summary of the issue.",
  "type": "bug|feature_request|documentation|question|other",
  "priority_score": "1-5 with justification",
  "suggested_labels": ["label1", "label2", "label3"],
  "potential_impact": "Impact description"
}
```

## Author

Created by **Sanjana Shetty** as part of production-style AI project development.
