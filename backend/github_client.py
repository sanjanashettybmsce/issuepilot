"""GitHub API client for fetching issue and repository data."""
import requests
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from backend.config import config


class GitHubClient:
    """Client for interacting with GitHub API."""
    
    def __init__(self):
        """Initialize GitHub client with authentication."""
        self.base_url = config.GITHUB_API_BASE_URL
        self.headers = {
            "Authorization": f"token {config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def get_issue(self, repo: str, issue_number: int) -> Dict[str, Any]:
        """Fetch a single issue with comments.
        
        Args:
            repo: Repository in format "owner/repo"
            issue_number: Issue number
            
        Returns:
            Dictionary containing issue details and comments
        """
        issue_url = f"{self.base_url}/repos/{repo}/issues/{issue_number}"
        
        # Fetch issue details
        issue_response = requests.get(issue_url, headers=self.headers)
        issue_response.raise_for_status()
        issue_data = issue_response.json()
        
        # Fetch comments
        comments_url = f"{issue_url}/comments"
        comments_response = requests.get(comments_url, headers=self.headers)
        comments_response.raise_for_status()
        comments_data = comments_response.json()
        
        return {
            "issue": issue_data,
            "comments": comments_data
        }
    
    def get_linked_issues_and_prs(self, repo: str, issue_number: int) -> Dict[str, List[Any]]:
        """Extract linked issues and PRs from issue body and comments.
        
        Args:
            repo: Repository in format "owner/repo"
            issue_number: Issue number
            
        Returns:
            Dictionary with linked issues and PRs
        """
        issue_data = self.get_issue(repo, issue_number)
        issue = issue_data["issue"]
        comments = issue_data["comments"]
        
        linked_issues = []
        linked_prs = []
        
        # Parse issue body and comments for links
        texts = [issue.get("body", "")] + [c.get("body", "") for c in comments]
        
        for text in texts:
            if text:
                # Simple extraction of #123 format references
                import re
                matches = re.findall(r'#(\d+)', text)
                for match in matches:
                    pr_number = int(match)
                    if pr_number != issue_number:  # Don't include self-reference
                        pr_data = self._fetch_related_item(repo, pr_number)
                        if pr_data.get("pull_request"):
                            linked_prs.append(pr_data)
                        else:
                            linked_issues.append(pr_data)
        
        return {
            "linked_issues": linked_issues,
            "linked_prs": linked_prs
        }
    
    def _fetch_related_item(self, repo: str, number: int) -> Dict[str, Any]:
        """Fetch a related issue or PR."""
        url = f"{self.base_url}/repos/{repo}/issues/{number}"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return {}
    
    def get_files_from_pr(self, repo: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get list of files changed in a PR.
        
        Args:
            repo: Repository in format "owner/repo"
            pr_number: Pull request number
            
        Returns:
            List of file change objects
        """
        url = f"{self.base_url}/repos/{repo}/pulls/{pr_number}/files"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def get_file_content(self, repo: str, path: str, ref: str = "main") -> str:
        """Get content of a file from repository.
        
        Args:
            repo: Repository in format "owner/repo"
            path: File path in repository
            ref: Git reference (branch/tag/commit)
            
        Returns:
            File content as string
        """
        url = f"{self.base_url}/repos/{repo}/contents/{path}"
        params = {"ref": ref}
        response = requests.get(url, headers=self.headers, params=params)
        
        if response.status_code == 200:
            import base64
            data = response.json()
            if "content" in data:
                return base64.b64decode(data["content"]).decode("utf-8")
        return ""
    
    def get_recent_commits(self, repo: str, path: Optional[str] = None, since_days: int = 30) -> List[Dict[str, Any]]:
        """Get recent commits touching a file or repository.
        
        Args:
            repo: Repository in format "owner/repo"
            path: Optional file path to filter commits
            since_days: Number of days back to search
            
        Returns:
            List of commit objects
        """
        url = f"{self.base_url}/repos/{repo}/commits"
        
        since_date = (datetime.utcnow() - timedelta(days=since_days)).isoformat()
        params = {
            "since": since_date,
            "per_page": 100
        }
        
        if path:
            params["path"] = path
        
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def get_repository_info(self, repo: str) -> Dict[str, Any]:
        """Get basic repository information.
        
        Args:
            repo: Repository in format "owner/repo"
            
        Returns:
            Repository metadata
        """
        url = f"{self.base_url}/repos/{repo}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
