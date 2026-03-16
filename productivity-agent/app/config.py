"""Configuration management for the productivity agent."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    DISCORD_TOKEN: str = os.getenv("DISCORD_TOKEN", "")
    DISCORD_CHANNEL_ID: int = int(os.getenv("DISCORD_CHANNEL_ID", "0"))
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Database configuration
    DATABASE_URL: str = "sqlite:///data/agent.db"
    
    # FastAPI configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Scheduler configuration
    SCHEDULER_TIMEZONE: str = "UTC"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        required_vars = [
            ("DISCORD_TOKEN", cls.DISCORD_TOKEN),
            ("DISCORD_CHANNEL_ID", cls.DISCORD_CHANNEL_ID),
            ("OPENAI_API_KEY", cls.OPENAI_API_KEY),
        ]
        
        missing = [name for name, value in required_vars if not value]
        if missing:
            raise ValueError(f"Missing required environment variables: {missing}")
        
        return True
