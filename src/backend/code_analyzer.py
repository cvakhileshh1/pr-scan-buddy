"""
Code analysis module for reviewing code quality, security, and best practices
"""

import ast
import re
import asyncio
from typing import List, Dict, Any
from models import PRData, PRAnalysisResponse, CodeFeedback, FeedbackType
import subprocess
import tempfile
import os

class CodeAnalyzer:
    def __init__(self):
        self.security_patterns = [
            (r'eval\s*\(', "Avoid using eval() as it can execute arbitrary code"),
            (r'exec\s*\(', "Avoid using exec() as it can execute arbitrary code"),
            (r'subprocess\.call\s*\(.*shell\s*=\s*True', "Avoid shell=True in subprocess calls"),
            (r'sql.*\+.*', "Potential SQL injection - use parameterized queries"),
            (r'password\s*=\s*["\'][^"\']*["\']', "Hardcoded password detected"),
            (r'api_key\s*=\s*["\'][^"\']*["\']', "Hardcoded API key detected"),
        ]
        
        self.quality_patterns = [
            (r'def\s+\w+\([^)]*\):\s*$', "Function missing docstring"),
            (r'class\s+\w+.*:\s*$', "Class missing docstring"),
            (r'print\s*\(', "Consider using logging instead of print statements"),
            (r'TODO|FIXME|HACK', "TODO/FIXME comment found - consider addressing"),
        ]
    
    async def analyze_changes(self, pr_data: PRData) -> PRAnalysisResponse:
        """
        Analyze the PR changes and generate feedback
        """
        feedback = []
        
        # Parse diff and analyze each file
        diff_sections = self._parse_diff(pr_data.diff_content)
        
        for file_path, changes in diff_sections.items():
            if self._is_code_file(file_path):
                file_feedback = await self._analyze_file_changes(file_path, changes)
                feedback.extend(file_feedback)
        
        # Calculate overall score
        score = self._calculate_score(feedback)
        
        # Generate summary
        summary = self._generate_summary(pr_data, feedback, score)
        
        return PRAnalysisResponse(
            score=score,
            feedback=feedback,
            summary=summary,
            files_changed=len(pr_data.files_changed),
            lines_added=pr_data.additions,
            lines_removed=pr_data.deletions,
            recommendations=self._generate_recommendations(feedback)
        )
    
    def _parse_diff(self, diff_content: str) -> Dict[str, List[str]]:
        """
        Parse git diff content and extract changes per file
        """
        files = {}
        current_file = None
        current_changes = []
        
        for line in diff_content.split('\n'):
            if line.startswith('diff --git'):
                if current_file:
                    files[current_file] = current_changes
                # Extract filename
                parts = line.split(' ')
                current_file = parts[-1][2:]  # Remove 'b/' prefix
                current_changes = []
            elif line.startswith('+') and not line.startswith('+++'):
                current_changes.append(line[1:])  # Remove '+' prefix
        
        if current_file:
            files[current_file] = current_changes
            
        return files
    
    def _is_code_file(self, file_path: str) -> bool:
        """
        Check if the file is a code file that should be analyzed
        """
        code_extensions = ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.cs', '.php', '.rb', '.go']
        return any(file_path.endswith(ext) for ext in code_extensions)
    
    async def _analyze_file_changes(self, file_path: str, changes: List[str]) -> List[CodeFeedback]:
        """
        Analyze changes in a specific file
        """
        feedback = []
        
        for line_num, line_content in enumerate(changes, 1):
            # Security analysis
            security_issues = self._check_security_patterns(line_content)
            for issue in security_issues:
                feedback.append(CodeFeedback(
                    file=file_path,
                    line=line_num,
                    type=FeedbackType.ERROR,
                    message=issue,
                    severity=5
                ))
            
            # Code quality analysis
            quality_issues = self._check_quality_patterns(line_content)
            for issue in quality_issues:
                feedback.append(CodeFeedback(
                    file=file_path,
                    line=line_num,
                    type=FeedbackType.WARNING,
                    message=issue,
                    severity=3
                ))
            
            # Python-specific analysis
            if file_path.endswith('.py'):
                python_issues = await self._analyze_python_line(line_content)
                for issue in python_issues:
                    feedback.append(CodeFeedback(
                        file=file_path,
                        line=line_num,
                        type=issue['type'],
                        message=issue['message'],
                        severity=issue['severity']
                    ))
        
        return feedback
    
    def _check_security_patterns(self, line: str) -> List[str]:
        """
        Check line against security patterns
        """
        issues = []
        for pattern, message in self.security_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(message)
        return issues
    
    def _check_quality_patterns(self, line: str) -> List[str]:
        """
        Check line against code quality patterns
        """
        issues = []
        for pattern, message in self.quality_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                issues.append(message)
        return issues
    
    async def _analyze_python_line(self, line: str) -> List[Dict]:
        """
        Python-specific code analysis
        """
        issues = []
        
        # Check for missing type hints
        if re.match(r'def\s+\w+\([^)]*\):', line) and '->' not in line:
            issues.append({
                'type': FeedbackType.SUGGESTION,
                'message': 'Consider adding type hints for better code clarity',
                'severity': 2
            })
        
        # Check for long lines
        if len(line.strip()) > 88:
            issues.append({
                'type': FeedbackType.WARNING,
                'message': 'Line exceeds recommended length (88 characters)',
                'severity': 2
            })
        
        # Check for unused imports (basic check)
        if line.strip().startswith('import ') and '#' not in line:
            issues.append({
                'type': FeedbackType.INFO,
                'message': 'Verify that this import is actually used',
                'severity': 1
            })
        
        return issues
    
    def _calculate_score(self, feedback: List[CodeFeedback]) -> int:
        """
        Calculate overall code quality score based on feedback
        """
        if not feedback:
            return 100
        
        total_penalty = 0
        for item in feedback:
            if item.type == FeedbackType.ERROR:
                total_penalty += item.severity * 3
            elif item.type == FeedbackType.WARNING:
                total_penalty += item.severity * 2
            elif item.type == FeedbackType.SUGGESTION:
                total_penalty += item.severity * 1
            else:  # INFO
                total_penalty += item.severity * 0.5
        
        # Calculate score (max penalty of 100)
        score = max(0, 100 - min(100, total_penalty))
        return int(score)
    
    def _generate_summary(self, pr_data: PRData, feedback: List[CodeFeedback], score: int) -> str:
        """
        Generate a summary of the analysis
        """
        error_count = len([f for f in feedback if f.type == FeedbackType.ERROR])
        warning_count = len([f for f in feedback if f.type == FeedbackType.WARNING])
        
        summary = f"Analysis of PR with {pr_data.files_changed} files changed "
        summary += f"({pr_data.additions} additions, {pr_data.deletions} deletions). "
        
        if score >= 90:
            summary += "Excellent code quality with minimal issues. "
        elif score >= 70:
            summary += "Good code quality with some areas for improvement. "
        else:
            summary += "Code quality needs attention with several issues to address. "
        
        if error_count > 0:
            summary += f"Found {error_count} critical issues that should be fixed. "
        if warning_count > 0:
            summary += f"Found {warning_count} warnings to consider. "
        
        return summary
    
    def _generate_recommendations(self, feedback: List[CodeFeedback]) -> List[str]:
        """
        Generate actionable recommendations based on feedback
        """
        recommendations = []
        
        error_count = len([f for f in feedback if f.type == FeedbackType.ERROR])
        if error_count > 0:
            recommendations.append("Address all critical security and error issues before merging")
        
        security_issues = len([f for f in feedback if 'security' in f.message.lower() or 'injection' in f.message.lower()])
        if security_issues > 0:
            recommendations.append("Review and fix security vulnerabilities")
        
        doc_issues = len([f for f in feedback if 'docstring' in f.message.lower()])
        if doc_issues > 0:
            recommendations.append("Add documentation to improve code maintainability")
        
        if not recommendations:
            recommendations.append("Great work! Code looks good to merge.")
        
        return recommendations