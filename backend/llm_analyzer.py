"""LLM integration for analyzing enriched issue context."""
from typing import Dict, Any
import json
import requests
from backend.config import config


class LLMAnalyzer:
    """Analyzes enriched issue context using Google Gemini API."""
    
    def __init__(self):
        """Initialize LLM analyzer with Google Gemini API."""
        self.api_key = config.GEMINI_API_KEY
        self.model = config.GEMINI_MODEL
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    def analyze_issue(self, enriched_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze enriched issue context and generate structured analysis.
        
        Args:
            enriched_context: Dictionary with enriched issue context
            
        Returns:
            Structured analysis as dictionary
        """
        # Build comprehensive prompt
        prompt = self._build_analysis_prompt(enriched_context)
        
        # Prepare request to Gemini API
        url = self.api_url.format(model=self.model)
        headers = {
            "Content-Type": "application/json"
        }
        
        payload = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {"text": self._get_system_prompt() + "\n\n" + prompt}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "response_mime_type": "application/json"
            }
        }
        
        # Call Gemini API
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                params={"key": self.api_key},
                timeout=60
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini API request failed: {str(e)}")
        
        # Parse response
        try:
            response_data = response.json()
            response_text = response_data["candidates"][0]["content"]["parts"][0]["text"]
            analysis = json.loads(response_text)
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            raise Exception(f"Failed to parse Gemini API response: {str(e)}")
        
        return self._validate_analysis(analysis)
    
    def _build_analysis_prompt(self, context: Dict[str, Any]) -> str:
        """Build comprehensive analysis prompt from enriched context.
        
        Args:
            context: Enriched context dictionary
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""Analyze the following GitHub issue and provide structured insights:

**Issue Title:** {context.get('issue_title', 'N/A')}

**Issue Body:**
{context.get('issue_body', 'N/A')[:1000]}

**Issue State:** {context.get('issue_state', 'N/A')}

**Current Labels:** {', '.join(context.get('issue_labels', []))}

**Recent Comments Summary:**
{context.get('comments_summary', 'No comments')[:500]}

**Linked Items:**
- Linked Issues: {len(context.get('linked_items', {}).get('linked_issues', []))} found
- Linked PRs: {len(context.get('linked_items', {}).get('linked_prs', []))} found

**Relevant Files Changed (from linked PRs):**
{self._format_files(context.get('relevant_files', [])[:5])}

**Stack Traces/Errors:**
{self._format_stack_traces(context.get('stack_traces', []))}

**Recent Commits:**
{self._format_commits(context.get('recent_commits', [])[:3])}

**Repository Context:**
- Stars: {context.get('repository_info', {}).get('stargazers_count', 'N/A')}
- Language: {context.get('repository_info', {}).get('language', 'N/A')}
- Open Issues: {context.get('repository_info', {}).get('open_issues_count', 'N/A')}

Based on this comprehensive context, provide analysis in the exact JSON format specified.
"""
        return prompt
    
    def _format_files(self, files: list) -> str:
        """Format file information for prompt."""
        if not files:
            return "No relevant files found"
        
        formatted = []
        for f in files:
            formatted.append(
                f"- {f.get('filename')}: {f.get('status')} "
                f"(+{f.get('additions', 0)}/-{f.get('deletions', 0)})"
            )
        return "\n".join(formatted)
    
    def _format_stack_traces(self, traces: list) -> str:
        """Format stack traces for prompt."""
        if not traces:
            return "No stack traces found"
        
        formatted = []
        for i, trace in enumerate(traces, 1):
            formatted.append(f"**Trace {i}:**\n{trace}")
        return "\n".join(formatted)
    
    def _format_commits(self, commits: list) -> str:
        """Format commit information for prompt."""
        if not commits:
            return "No recent commits found"
        
        formatted = []
        for commit in commits:
            formatted.append(
                f"- [{commit.get('sha')}] {commit.get('message', 'N/A')[:50]} "
                f"by {commit.get('author', 'N/A')} on {commit.get('date', 'N/A')}"
            )
        return "\n".join(formatted)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for LLM."""
        return """You are an expert GitHub issue analyst. Your task is to analyze issues with enriched context 
(linked PRs, files, commits, stack traces) and provide structured insights.

Return ONLY valid JSON in this exact format:
{
  "summary": "A one-sentence summary of the issue/problem",
  "type": "bug|feature_request|documentation|question|other",
  "priority_score": {
    "score": <1-5>,
    "justification": "Why this priority level"
  },
  "suggested_labels": ["label1", "label2", "label3"],
  "potential_impact": "Brief description of user impact if this is a bug"
}

Be precise, actionable, and data-driven in your analysis."""
    
    def _validate_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize analysis output.
        
        Args:
            analysis: Analysis dictionary from LLM
            
        Returns:
            Validated analysis with defaults for missing fields
        """
        # Set defaults for required fields
        validated = {
            "summary": analysis.get("summary", "Issue analysis unavailable"),
            "type": analysis.get("type", "other"),
            "priority_score": {
                "score": min(max(analysis.get("priority_score", {}).get("score", 3), 1), 5),
                "justification": analysis.get("priority_score", {}).get("justification", "Moderate priority")
            },
            "suggested_labels": analysis.get("suggested_labels", ["triage-needed"]),
            "potential_impact": analysis.get("potential_impact", "Potential impact pending review")
        }
        
        # Validate type
        valid_types = ["bug", "feature_request", "documentation", "question", "other"]
        if validated["type"] not in valid_types:
            validated["type"] = "other"
        
        # Ensure suggested_labels has 2-3 items
        if not isinstance(validated["suggested_labels"], list):
            validated["suggested_labels"] = ["triage-needed"]
        validated["suggested_labels"] = validated["suggested_labels"][:3]
        if len(validated["suggested_labels"]) < 2:
            validated["suggested_labels"].append("triage-needed")
        
        return validated
