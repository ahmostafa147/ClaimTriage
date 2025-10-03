#!/usr/bin/env python3
"""Test LandingAI ADE API directly to understand the correct format."""

import requests
import json
import os

def test_landingai_api():
    """Test the LandingAI API directly."""
    api_key = "am43cmYzaGF3M2hhOXhiMWQ0a3B4OkZPcENsWE81WU9zUkdldU5pU0NDdDZGUm14MXE2MUFh"
    
    # Test different API endpoints
    endpoints = [
        "https://api.landing.ai/v1/ade/extract",
        "https://api.landing.ai/v1/document-extraction/extract", 
        "https://api.landing.ai/v1/extract",
        "https://api.landing.ai/ade/extract"
    ]
    
    for endpoint in endpoints:
        print(f"\n🔍 Testing endpoint: {endpoint}")
        
        # Test with a simple PDF file
        test_file = "demo_data/inbox/fe1cde3a_claim_auto_001.pdf"
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            continue
            
        try:
            with open(test_file, 'rb') as f:
                files = {'file': f}
                headers = {
                    "Authorization": f"Bearer {api_key}",
                }
                
                response = requests.post(endpoint, headers=headers, files=files, timeout=30)
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                
                if response.status_code == 200:
                    print("✅ SUCCESS! This endpoint works!")
                    return endpoint
                    
        except Exception as e:
            print(f"❌ Error: {e}")
    
    return None

if __name__ == "__main__":
    working_endpoint = test_landingai_api()
    if working_endpoint:
        print(f"\n🎉 Working endpoint found: {working_endpoint}")
    else:
        print("\n❌ No working endpoint found")
