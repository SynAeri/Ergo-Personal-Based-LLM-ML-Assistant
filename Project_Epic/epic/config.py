"""
Configuration loading with .env support
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"

if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ Loaded configuration from {env_file}")

# API Keys
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_AI_API_KEY = os.getenv("GOOGLE_AI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Server configuration
EPIC_HOST = os.getenv("EPIC_HOST", "127.0.0.1")
EPIC_PORT = int(os.getenv("EPIC_PORT", "8766"))

def check_api_keys():
    """Check if required API keys are set"""
    warnings = []

    if not ANTHROPIC_API_KEY:
        warnings.append("⚠️  ANTHROPIC_API_KEY not set (required for Claude agents)")

    if not GOOGLE_AI_API_KEY:
        warnings.append("⚠️  GOOGLE_AI_API_KEY not set (optional, for Gemini agents)")

    return warnings
