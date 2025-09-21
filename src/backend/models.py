"""
Data models for the PR Review Agent
"""

from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal
from enum import Enum

class FeedbackType(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    SUGGESTION = "suggestion"
    INFO = "info"

class PRAnalysisRequest(BaseModel):
    repository_url: HttpUrl
    pr_number: int
    
class CodeFeedback(BaseModel):
    file: str
    line: int
    type: FeedbackType
    message: str
    severity: int  # 1-5 scale
    suggestion: Optional[str] = None

class PRData(BaseModel):
    files_changed: List[str]
    additions: int
    deletions: int
    commits: int
    diff_content: str
    branch_name: str
    base_branch: str

class PRAnalysisResponse(BaseModel):
    score: int  # 0-100
    feedback: List[CodeFeedback]
    summary: str
    files_changed: int
    lines_added: int
    lines_removed: int
    recommendations: Optional[List[str]] = None