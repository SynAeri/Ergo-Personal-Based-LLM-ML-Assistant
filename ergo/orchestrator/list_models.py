"""
List available Gemini models for the configured API key
"""

import sys
from pathlib import Path
import google.generativeai as genai

sys.path.insert(0, str(Path(__file__).parent))
from src.config import settings

if not settings.google_ai_api_key:
    print("ERROR: No Google AI API key configured in .env")
    sys.exit(1)

genai.configure(api_key=settings.google_ai_api_key)

print("Available Gemini models:\n")
for model in genai.list_models():
    if 'generateContent' in model.supported_generation_methods:
        print(f"  - {model.name}")
        print(f"    Display: {model.display_name}")
        print(f"    Description: {model.description[:80]}...")
        print()
