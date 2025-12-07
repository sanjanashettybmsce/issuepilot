"""Context Enrichment Engine for gathering repository context."""
from typing import Dict, List, Any, Optional
from backend.github_client import GitHubClient
import re


class ContextEnricher:
    """Enriches issue context with related information from repository."""
    
    def __init__(self):
        """Initialize context enricher with GitHub client."""
        self.github = GitHubClient()
    
    def enrich_issue_context(self, repo: str, issue_number: int) -> Dict[str, Any]:
        """Gather comprehensive context around an issue.
        
        Args:
            repo: Repository in format "owner/repo"
            issue_number: Issue number
            
        Returns:
            Dictionary with enriched context
        """
        # Fetch basic issue information
        issue_data = self.github.get_issue(repo, issue_number)
        issue = issue_data["issue"]
        comments = issue_data["comments"]
        
        context = {
            "issue_title": issue.get("title", ""),
            "issue_body": issue.get("body", ""),
            "issue_state": issue.get("state", ""),
            "issue_labels": [label.get("name") for label in issue.get("labels", [])],
            "comments_summary": self._summarize_comments(comments),
            "linked_items": self.github.get_linked_issues_and_prs(repo, issue_number),
            "repository_info": self.github.get_repository_info(repo)
        }
        
        # Gather files and commits from linked PRs
        linked_files = self._gather_files_from_linked_prs(
            repo,
            context["linked_items"].get("linked_prs", [])
        )
        context["relevant_files"] = linked_files
        
        # Extract stack traces and error messages
        stack_traces = self._extract_stack_traces(
            issue.get("body", "") + "\n" + "\n".join([c.get("body", "") for c in comments])
        )
        context["stack_traces"] = stack_traces
        
        # Get recent commits for affected files
        context["recent_commits"] = self._gather_recent_commits(repo, linked_files)
        
        return context
    
    def _summarize_comments(self, comments: List[Dict[str, Any]]) -> str:
        """Create a summary of issue comments.
        
        Args:
            comments: List of comment objects
            
        Returns:
            Concatenated comment bodies
        """
        if not comments:
            return ""
        
        # Limit to last 5 comments for context efficiency
        relevant_comments = comments[-5:]
        return "\n---\n".join([c.get("body", "") for c in relevant_comments])
    
    def _gather_files_from_linked_prs(self, repo: str, linked_prs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Gather files changed in linked pull requests.
        
        Args:
            repo: Repository in format "owner/repo"
            linked_prs: List of linked PR objects
            
        Returns:
            List of file information with content snippets
        """
        files_info = []
        
        for pr in linked_prs:
            if not pr.get("number"):
                continue
            
            try:
                files = self.github.get_files_from_pr(repo, pr["number"])
                
                for file_obj in files[:10]:  # Limit to first 10 files
                    file_info = {
                        "filename": file_obj.get("filename", ""),
                        "status": file_obj.get("status", ""),
                        "additions": file_obj.get("additions", 0),
                        "deletions": file_obj.get("deletions", 0),
                        "patch": file_obj.get("patch", "")[:500]  # First 500 chars of patch
                    }
                    files_info.append(file_info)
            except Exception as e:
                # Continue if PR fetch fails
                continue
        
        return files_info
    
    def _extract_stack_traces(self, text: str) -> List[str]:
        """Extract stack traces and error patterns from text.
        
        Args:
            text: Text to search for stack traces
            
        Returns:
            List of extracted stack traces
        """
        stack_traces = []
        
        # Common stack trace patterns
        patterns = [
            r'(Traceback.*?(?:\n  .*?)*)',  # Python traceback
            r'(Error:.*?(?:\n.*?)*)',  # Generic error
            r'(at .*?\n.*?)',  # Java-like stack trace
            r'(File ".*?", line \d+.*?)',  # File references
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.MULTILINE | re.DOTALL)
            stack_traces.extend(matches)
        
        # Limit to first 3 stack traces and 500 chars each
        return [st[:500] for st in stack_traces[:3]]
    
    def _gather_recent_commits(self, repo: str, files_info: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent commits touching affected files.
        
        Args:
            repo: Repository in format "owner/repo"
            files_info: List of file information
            limit: Maximum number of commits to return
            
        Returns:
            List of recent commit information
        """
        commits_info = []
        
        # Get commits for each file
        for file_obj in files_info[:5]:  # Limit to first 5 files
            filename = file_obj.get("filename", "")
            if not filename:
                continue
            
            try:
                commits = self.github.get_recent_commits(repo, path=filename, since_days=90)
                
                for commit in commits[:limit]:
                    commit_info = {
                        "message": commit.get("commit", {}).get("message", ""),
                        "author": commit.get("commit", {}).get("author", {}).get("name", ""),
                        "date": commit.get("commit", {}).get("author", {}).get("date", ""),
                        "sha": commit.get("sha", "")[:7],  # Short SHA
                        "file": filename
                    }
                    commits_info.append(commit_info)
            except Exception as e:
                # Continue if commit fetch fails
                continue
        
        return commits_info[:limit]
