#!/usr/bin/env python3
"""
Environment Validation Script (Groq Primary, Gemini Fallback)
Checks Groq and Gemini API keys, dependencies, and system health for PersonaForge AI.
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class EnvironmentValidator:
    """Validates environment setup and API keys."""
    
    def __init__(self):
        self.issues = []
        self.warnings = []
        self.successes = []
    
    def validate_env_file(self):
        """Check if .env file exists and has required variables."""
        env_file = Path('.env')
        if not env_file.exists():
            self.issues.append("❌ .env file not found")
            return False
        self.successes.append("✅ .env file found")
        # Check for required variables
        required_vars = ['GROQ_API_KEY']
        optional_vars = ['GEMINI_API_KEY', 'REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT']
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                self.issues.append(f"❌ {var} not set in .env file")
            elif value.strip() == '':
                self.issues.append(f"❌ {var} is empty in .env file")
            else:
                self.successes.append(f"✅ {var} is set")
        for var in optional_vars:
            value = os.getenv(var)
            if not value:
                self.warnings.append(f"⚠️ {var} not set (optional)")
            else:
                self.successes.append(f"✅ {var} is set")
        return len([i for i in self.issues if var in i for var in required_vars]) == 0

    async def test_gemini_api(self):
        """Test Gemini API key."""
        gemini_key = os.getenv('GEMINI_API_KEY')
        if not gemini_key:
            self.issues.append("❌ Cannot test Gemini API - no key provided")
            return False
        try:
            import google.generativeai as genai
            genai.configure(api_key=gemini_key)
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = await asyncio.to_thread(
                model.generate_content,
                "Say 'Hello'"
            )
            if response.text:
                self.successes.append("✅ Gemini API key is valid and working")
                return True
            else:
                self.issues.append("❌ Gemini API returned empty response")
                return False
        except Exception as e:
            error_msg = str(e)
            if "invalid" in error_msg.lower() or "401" in error_msg:
                self.issues.append("❌ Gemini API key is invalid")
            elif "rate" in error_msg.lower() or "429" in error_msg or "quota" in error_msg.lower():
                self.warnings.append("⚠️ Gemini API rate limited/quota exceeded (key may be valid)")
            else:
                self.issues.append(f"❌ Gemini API test failed: {error_msg}")
            return False

    def print_summary(self):
        print("\nValidation Summary:")
        for msg in self.successes:
            print(msg)
        for msg in self.warnings:
            print(msg)
        for msg in self.issues:
            print(msg)

async def main():
    validator = EnvironmentValidator()
    validator.validate_env_file()
    await validator.test_gemini_api()
    validator.print_summary()

if __name__ == "__main__":
    asyncio.run(main()) 