"""Pydantic models for request/response data."""
try:
    from pydantic import BaseModel
except ImportError:
    # Fallback: use typing for models if pydantic not available
    class BaseModel:
        pass

from typing import Optional, List


class IssueAnalysisRequest(BaseModel):
    """Request model for issue analysis."""
    repo_url: str  # Format: "owner/repo"
    issue_number: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "repo_url": "torvalds/linux",
                "issue_number": 12345
            }
        }


class PriorityScore(BaseModel):
    """Priority score with justification."""
    score: int  # 1-5
    justification: str


class IssueAnalysisResponse(BaseModel):
    """Response model for issue analysis."""
    summary: str
    type: str  # bug, feature_request, documentation, question, other
    priority_score: PriorityScore
    suggested_labels: List[str]
    potential_impact: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary": "User reports that login fails with incorrect password error message.",
                "type": "bug",
                "priority_score": {
                    "score": 4,
                    "justification": "Affects user authentication, blocking access for many users."
                },
                "suggested_labels": ["bug", "login-flow", "authentication"],
                "potential_impact": "Users unable to access the application, leading to service disruption."
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    details: Optional[str] = None
