from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class AnalyzeRequest(BaseModel):
    github_url: str

class Summary(BaseModel):
    overall_grade: str
    security_score: int
    code_quality_score: int
    maintainability_score: int
    total_files_reviewed: int

class Issue(BaseModel):
    file: str
    line: int
    message: str
    rule_id: str

class Issues(BaseModel):
    critical: List[Issue]
    major: List[Issue]
    minor: List[Issue]

class Metrics(BaseModel):
    cyclomatic_complexity: Dict[str, Any]
    line_counts: Dict[str, int]
    function_counts: Dict[str, int]

class CrossFileAnalysis(BaseModel):
    circular_imports: List[str]
    shared_globals: List[str]
    duplicate_classes: List[str]

class AIFixSuggestion(BaseModel):
    fix_id: str
    file: str
    line: int
    issue_type: str
    risk_explanation: str
    recommended_fix_explanation: str
    secure_code_example: str

class AnalyzeResponse(BaseModel):
    summary: Summary
    issues: Issues
    metrics: Metrics
    cross_file_analysis: CrossFileAnalysis
    recommendations: List[str]
    ai_status: str
    ai_fix_suggestions: List[AIFixSuggestion]

class ApplyFixRequest(BaseModel):
    fix_id: str
    file: str
    line: int
    secure_code_example: str

class RejectFixRequest(BaseModel):
    fix_id: str

class ActionResponse(BaseModel):
    status: str
    message: Optional[str] = None
    applied_fixes: Optional[int] = None
