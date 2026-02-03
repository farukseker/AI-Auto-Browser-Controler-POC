"""
Configuration settings for AI Selenium automation
"""
import os
from dataclasses import dataclass


@dataclass
class Config:
    """Central configuration"""
    
    # OpenRouter settings
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4-turbo")
    
    # Selenium settings
    HEADLESS: bool = os.getenv("SELENIUM_HEADLESS", "false").lower() == "true"
    TIMEOUT: int = int(os.getenv("SELENIUM_TIMEOUT", "10"))
    SCREENSHOT_DIR: str = os.getenv("SCREENSHOT_DIR", "./screenshots")
    
    # Retry settings
    AUTO_RETRY: bool = os.getenv("AUTO_RETRY", "true").lower() == "true"
    MAX_RETRIES: int = int(os.getenv("MAX_RETRIES", "2"))
    
    # Logging
    LOG_DIR: str = os.getenv("LOG_DIR", "./logs")
    SAVE_LOGS: bool = os.getenv("SAVE_LOGS", "true").lower() == "true"
    
    # Browser settings
    WINDOW_WIDTH: int = int(os.getenv("WINDOW_WIDTH", "1920"))
    WINDOW_HEIGHT: int = int(os.getenv("WINDOW_HEIGHT", "1080"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required settings"""
        config = cls()
        
        if not config.OPENROUTER_API_KEY:
            print("ERROR: OPENROUTER_API_KEY not set")
            print("Set it via environment variable or in code")
            return False
            
        return True
        
    @classmethod
    def print_config(cls):
        """Print current configuration"""
        config = cls()
        
        print("\nCurrent Configuration:")
        print("-" * 60)
        print(f"Model:          {config.OPENROUTER_MODEL}")
        print(f"Headless:       {config.HEADLESS}")
        print(f"Timeout:        {config.TIMEOUT}s")
        print(f"Auto Retry:     {config.AUTO_RETRY}")
        print(f"Max Retries:    {config.MAX_RETRIES}")
        print(f"Screenshot Dir: {config.SCREENSHOT_DIR}")
        print(f"Log Dir:        {config.LOG_DIR}")
        print("-" * 60 + "\n")
