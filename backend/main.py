"""FastAPI backend for IssueSense AI."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import logging
from backend.models import IssueAnalysisRequest, IssueAnalysisResponse, PriorityScore, ErrorResponse
from backend.config import config
from backend.context_enricher import ContextEnricher
from backend.llm_analyzer import LLMAnalyzer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration at startup
try:
    config.validate()
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="IssuePilot",
    description="AI-powered GitHub issue analysis with context enrichment using Google Gemini",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
enricher = ContextEnricher()
analyzer = LLMAnalyzer()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "IssueSense AI",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=IssueAnalysisResponse)
async def analyze_issue(request: IssueAnalysisRequest):
    """Analyze a GitHub issue with context enrichment.
    
    Args:
        request: Issue analysis request with repo URL and issue number
        
    Returns:
        Structured issue analysis
    """
    try:
        logger.info(f"Analyzing issue: {request.repo_url}#{request.issue_number}")
        
        # Validate repository format
        if "/" not in request.repo_url or request.repo_url.count("/") > 1:
            raise ValueError("Invalid repository format. Use 'owner/repo'")
        
        # Step 1: Enrich context
        logger.info("Enriching issue context...")
        enriched_context = enricher.enrich_issue_context(
            request.repo_url,
            request.issue_number
        )
        
        # Step 2: Analyze with LLM
        logger.info("Analyzing with LLM...")
        analysis = analyzer.analyze_issue(enriched_context)
        
        # Step 3: Format response
        response = IssueAnalysisResponse(
            summary=analysis["summary"],
            type=analysis["type"],
            priority_score=PriorityScore(
                score=analysis["priority_score"]["score"],
                justification=analysis["priority_score"]["justification"]
            ),
            suggested_labels=analysis["suggested_labels"],
            potential_impact=analysis["potential_impact"]
        )
        
        logger.info(f"Analysis complete for {request.repo_url}#{request.issue_number}")
        return response
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.error(f"Error analyzing issue: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error analyzing issue. Please check the repository and issue number."
        )


@app.post("/batch-analyze")
async def batch_analyze(requests_list: list[IssueAnalysisRequest]):
    """Analyze multiple GitHub issues in batch.
    
    Args:
        requests_list: List of analysis requests
        
    Returns:
        List of analysis results
    """
    results = []
    for request in requests_list:
        try:
            result = await analyze_issue(request)
            results.append({
                "repo": request.repo_url,
                "issue": request.issue_number,
                "analysis": result,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "repo": request.repo_url,
                "issue": request.issue_number,
                "error": str(e),
                "status": "failed"
            })
    
    return results


@app.get("/")
def root():
    """Root endpoint with API documentation."""
    return {
        "service": "IssueSense AI",
        "description": "AI-powered GitHub issue analysis with context enrichment",
        "endpoints": {
            "health": "/health",
            "analyze": "POST /analyze",
            "batch_analyze": "POST /batch-analyze",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT
    )
