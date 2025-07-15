#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()

def test_simple_groq():
    try:
        from groq import Groq
        print("✅ Groq import successful")
        
        api_key = os.getenv('GROQ_API_KEY', 'your-groq-api-key-here')
        print(f"🔑 API Key: {api_key[:10]}...")
        
        # Try different initialization methods
        print("Testing Groq client initialization...")
        
        # Method 1: Basic initialization
        try:
            client1 = Groq(api_key=api_key)
            print("✅ Method 1 (api_key=) successful")
        except Exception as e:
            print(f"❌ Method 1 failed: {e}")
        
        # Method 2: Direct initialization
        try:
            client2 = Groq(api_key)
            print("✅ Method 2 (direct) successful")
        except Exception as e:
            print(f"❌ Method 2 failed: {e}")
        
        # Method 3: With environment variable
        try:
            os.environ['GROQ_API_KEY'] = api_key
            client3 = Groq()
            print("✅ Method 3 (env var) successful")
        except Exception as e:
            print(f"❌ Method 3 failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Groq client initialization...")
    print("=" * 50)
    test_simple_groq() 