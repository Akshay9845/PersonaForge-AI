#!/usr/bin/env python3

import os
from dotenv import load_dotenv

load_dotenv()

def test_groq():
    try:
        from groq import Groq
        print("✅ Groq import successful")
        
        api_key = os.getenv('GROQ_API_KEY', 'your_groq_api_key_here')
        print(f"🔑 API Key: {api_key[:10]}...")
        
        client = Groq(api_key=api_key)
        print("✅ Groq client created successfully")
        
        # Test a simple API call
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": "Say hello"}],
            model="llama3-70b-8192",
            temperature=0.5,
            max_tokens=10
        )
        
        print("✅ Groq API call successful!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ Groq test failed: {e}")
        return False

def test_gemini():
    try:
        import google.generativeai as genai
        print("✅ Gemini import successful")
        
        api_key = os.getenv('GEMINI_API_KEY', 'your_gemini_api_key_here')
        print(f"🔑 API Key: {api_key[:10]}...")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-pro')
        print("✅ Gemini client created successfully")
        
        # Test a simple API call
        response = model.generate_content("Say hello")
        print("✅ Gemini API call successful!")
        print(f"Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LLM APIs...")
    print("=" * 50)
    
    groq_working = test_groq()
    print()
    gemini_working = test_gemini()
    
    print("=" * 50)
    if groq_working:
        print("🎉 Groq is working!")
    else:
        print("❌ Groq is not working")
        
    if gemini_working:
        print("🎉 Gemini is working!")
    else:
        print("❌ Gemini is not working") 