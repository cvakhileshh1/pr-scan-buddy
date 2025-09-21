"""
PR Review Agent Backend - FastAPI Application
Professional code review automation system.
Copy this to a separate Python project to run the backend.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from typing import List, Optional
import asyncio

# Import custom modules (create these files separately)
from git_integration import GitService
from code_analyzer import CodeAnalyzer
from models import PRAnalysisRequest, PRAnalysisResponse, CodeFeedback

app = FastAPI(
    title="PR Review Agent API",
    description="AI-powered Pull Request Review System",
    version="1.0.0"
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
git_service = GitService()
code_analyzer = CodeAnalyzer()

@app.get("/")
async def root():
    return {"message": "PR Review Agent API is running"}

@app.post("/api/analyze-pr", response_model=PRAnalysisResponse)
async def analyze_pull_request(request: PRAnalysisRequest):
    """
    Analyze a pull request and return code review feedback
    """
    try:
        # Fetch PR data from Git repository
        pr_data = await git_service.fetch_pr_data(
            repository_url=request.repository_url,
            pr_number=request.pr_number
        )
        
        # Analyze the code changes
        analysis_result = await code_analyzer.analyze_changes(pr_data)
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "PR Review Agent"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )