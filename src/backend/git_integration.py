"""
Git integration module for fetching PR data from various Git platforms
"""

import git
import requests
import os
import tempfile
import shutil
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from models import PRData
import asyncio
import aiohttp

class GitService:
    def __init__(self):
        self.temp_dir = None
        
    async def fetch_pr_data(self, repository_url: str, pr_number: int) -> PRData:
        """
        Fetch pull request data from the repository
        """
        # Parse repository URL to determine platform (GitHub, GitLab, Bitbucket)
        parsed_url = urlparse(str(repository_url))
        
        if "github.com" in parsed_url.netloc:
            return await self._fetch_github_pr(repository_url, pr_number)
        elif "gitlab.com" in parsed_url.netloc:
            return await self._fetch_gitlab_pr(repository_url, pr_number)
        elif "bitbucket.org" in parsed_url.netloc:
            return await self._fetch_bitbucket_pr(repository_url, pr_number)
        else:
            raise ValueError("Unsupported Git platform")
    
    async def _fetch_github_pr(self, repository_url: str, pr_number: int) -> PRData:
        """
        Fetch PR data from GitHub API
        """
        # Extract owner and repo from URL
        parsed = urlparse(str(repository_url))
        path_parts = parsed.path.strip('/').split('/')
        owner, repo = path_parts[0], path_parts[1].replace('.git', '')
        
        api_url = f"https://api.github.com/repos/{owner}/{repo}/pulls/{pr_number}"
        
        async with aiohttp.ClientSession() as session:
            # Get PR metadata
            async with session.get(api_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch PR data: {response.status}")
                pr_data = await response.json()
            
            # Get PR files and diff
            files_url = f"{api_url}/files"
            async with session.get(files_url) as response:
                if response.status != 200:
                    raise Exception(f"Failed to fetch PR files: {response.status}")
                files_data = await response.json()
        
        # Clone repository and get diff
        diff_content = await self._get_pr_diff(repository_url, pr_data['head']['sha'], pr_data['base']['sha'])
        
        return PRData(
            files_changed=[f['filename'] for f in files_data],
            additions=pr_data['additions'],
            deletions=pr_data['deletions'],
            commits=pr_data['commits'],
            diff_content=diff_content,
            branch_name=pr_data['head']['ref'],
            base_branch=pr_data['base']['ref']
        )
    
    async def _fetch_gitlab_pr(self, repository_url: str, pr_number: int) -> PRData:
        """
        Fetch PR data from GitLab API (Merge Request)
        """
        # Implementation for GitLab
        # Similar to GitHub but using GitLab API endpoints
        raise NotImplementedError("GitLab integration coming soon")
    
    async def _fetch_bitbucket_pr(self, repository_url: str, pr_number: int) -> PRData:
        """
        Fetch PR data from Bitbucket API
        """
        # Implementation for Bitbucket
        raise NotImplementedError("Bitbucket integration coming soon")
    
    async def _get_pr_diff(self, repository_url: str, head_sha: str, base_sha: str) -> str:
        """
        Clone repository and get diff between commits
        """
        try:
            # Create temporary directory
            self.temp_dir = tempfile.mkdtemp()
            
            # Clone repository
            repo = git.Repo.clone_from(str(repository_url), self.temp_dir)
            
            # Get diff between commits
            diff = repo.git.diff(base_sha, head_sha)
            
            return diff
            
        except Exception as e:
            raise Exception(f"Failed to get diff: {str(e)}")
        finally:
            # Cleanup
            if self.temp_dir and os.path.exists(self.temp_dir):
                shutil.rmtree(self.temp_dir)
    
    def __del__(self):
        """Cleanup temporary directory"""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)