#!/usr/bin/env python3

import asyncio
import json
from web_dashboard import app
from fastapi.testclient import TestClient

client = TestClient(app=app)

def test_analyze_endpoint():
    """Test the analyze endpoint directly."""
    try:
        response = client.post(
            "/api/analyze",
            json={
                "username": "testuser",
                "max_posts": 5,
                "max_comments": 10
            }
        )
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response
    except Exception as e:
        print(f"Error: {e}")
        return None

if __name__ == "__main__":
    test_analyze_endpoint() 