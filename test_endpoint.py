"""
Test Script for TDS Quiz Solver Endpoint
Tests the /solve webhook endpoint with valid and invalid requests
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

EMAIL = os.getenv("EMAIL")
SECRET = os.getenv("SECRET")

# Base URL for local testing
BASE_URL = "http://localhost:8000"


def test_health_check():
    """
    Test the health check endpoint
    """
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Health check passed")
            return True
        else:
            print("❌ Health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_valid_request():
    """
    Test with valid email, secret, and URL
    """
    print("\n" + "="*70)
    print("TEST 2: Valid Request")
    print("="*70)
    
    if not EMAIL or not SECRET:
        print("❌ EMAIL or SECRET not set in .env file")
        return False
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": "https://tds-llm-analysis.s-anand.net/demo"
    }
    
    print(f"Sending request with payload:")
    print(json.dumps(payload, indent=2))
    
    try:
        response = requests.post(
            f"{BASE_URL}/solve",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Valid request accepted")
            return True
        else:
            print("❌ Valid request failed")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_invalid_secret():
    """
    Test with invalid secret (should return 403)
    """
    print("\n" + "="*70)
    print("TEST 3: Invalid Secret")
    print("="*70)
    
    if not EMAIL:
        print("❌ EMAIL not set in .env file")
        return False
    
    payload = {
        "email": EMAIL,
        "secret": "wrong_secret_12345",
        "url": "https://tds-llm-analysis.s-anand.net/demo"
    }
    
    print(f"Sending request with invalid secret")
    
    try:
        response = requests.post(
            f"{BASE_URL}/solve",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 403:
            print("✅ Invalid secret correctly rejected")
            return True
        else:
            print("❌ Expected 403 status code")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_invalid_json():
    """
    Test with invalid JSON payload (should return 422)
    """
    print("\n" + "="*70)
    print("TEST 4: Invalid JSON Payload")
    print("="*70)
    
    payload = {
        "email": EMAIL,
        # Missing 'secret' and 'url' fields
    }
    
    print(f"Sending incomplete payload")
    
    try:
        response = requests.post(
            f"{BASE_URL}/solve",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 422:
            print("✅ Invalid payload correctly rejected")
            return True
        else:
            print("❌ Expected 422 status code")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_custom_url():
    """
    Test with a custom URL
    """
    print("\n" + "="*70)
    print("TEST 5: Custom URL (Optional)")
    print("="*70)
    
    custom_url = input("Enter custom quiz URL (or press Enter to skip): ").strip()
    
    if not custom_url:
        print("⏭️  Skipped")
        return True
    
    if not EMAIL or not SECRET:
        print("❌ EMAIL or SECRET not set in .env file")
        return False
    
    payload = {
        "email": EMAIL,
        "secret": SECRET,
        "url": custom_url
    }
    
    print(f"Sending request with custom URL: {custom_url}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/solve",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ Custom URL request accepted")
            return True
        else:
            print("⚠️  Request completed with status:", response.status_code)
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """
    Run all tests
    """
    print("\n" + "="*70)
    print("TDS QUIZ SOLVER - ENDPOINT TESTING")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Email: {EMAIL}")
    print("="*70)
    
    if not EMAIL or not SECRET:
        print("\n❌ ERROR: Please create a .env file with EMAIL and SECRET variables")
        print("\nExample .env file:")
        print("EMAIL=your.email@example.com")
        print("SECRET=your_secret_key")
        return
    
    # Run tests
    results = []
    
    results.append(("Health Check", test_health_check()))
    results.append(("Valid Request", test_valid_request()))
    results.append(("Invalid Secret", test_invalid_secret()))
    results.append(("Invalid JSON", test_invalid_json()))
    results.append(("Custom URL", test_custom_url()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("="*70)
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")


if __name__ == "__main__":
    main()
