"""Configuration management for IssueSense AI."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
# Use absolute path to ensure we load from the correct location
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path, override=True)


class Config:
    """Application configuration."""
    
    # GitHub API Configuration
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
    GITHUB_API_BASE_URL = os.getenv("GITHUB_API_BASE_URL", "https://api.github.com")
    
    # Google Gemini Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-pro")
    
    # Server Configuration
    BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))
    
    # Validation
    @classmethod
    def validate(cls):
        """Validate that required environment variables are set."""
        if not cls.GITHUB_TOKEN:
            raise ValueError("GITHUB_TOKEN environment variable is not set")
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY environment variable is not set")


# Create config instance
config = Config()
