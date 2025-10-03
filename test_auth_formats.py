#!/usr/bin/env python3
"""Test different LandingAI API authentication formats."""

import requests
import json
import os

def test_auth_formats():
    """Test different authentication formats."""
    api_key = "am43cmYzaGF3M2hhOXhiMWQ0a3B4OkZPcENsWE81WU9zUkdldU5pU0NDdDZGUm14MXE2MUFh"
    
    # Test different auth formats
    auth_formats = [
        f"Bearer {api_key}",
        f"API-Key {api_key}",
        f"X-API-Key {api_key}",
        api_key,
        f"landingai {api_key}",
        f"Token {api_key}"
    ]
    
    endpoint = "https://api.landing.ai/v1/ade/extract"
    test_file = "demo_data/inbox/fe1cde3a_claim_auto_001.pdf"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    for auth_format in auth_formats:
        print(f"\n🔍 Testing auth format: {auth_format[:20]}...")
        
        try:
            with open(test_file, 'rb') as f:
                files = {'file': f}
                headers = {
                    "Authorization": auth_format,
                }
                
                response = requests.post(endpoint, headers=headers, files=files, timeout=30)
                
                print(f"Status: {response.status_code}")
                if response.status_code != 401:
                    print(f"Response: {response.text[:200]}...")
                    if response.status_code == 200:
                        print("✅ SUCCESS! This auth format works!")
                        return auth_format
                else:
                    print("❌ Still unauthorized")
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    working_auth = test_auth_formats()
    if working_auth:
        print(f"\n🎉 Working auth format found: {working_auth}")
    else:
        print("\n❌ No working auth format found")
