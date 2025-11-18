#!/usr/bin/env python3
"""Test USPTO TSDR API integration."""

import os
import sys
import requests
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

load_dotenv()


def test_api_key_present():
    """Test if API key is configured."""
    api_key = os.getenv('USPTO_API_KEY')

    if not api_key:
        print("❌ USPTO_API_KEY not found in .env")
        return False

    print(f"✅ API Key found: {api_key[:10]}...")
    return True


def test_tsdr_endpoint():
    """Test TSDR API with a known trademark."""
    api_key = os.getenv('USPTO_API_KEY')

    # Test with a known serial number (Apple Inc. - APPLE trademark)
    serial_number = "73222525"
    url = f"https://tsdrapi.uspto.gov/ts/cd/casestatus/sn{serial_number}/info.json"

    headers = {
        "USPTO-API-KEY": api_key
    }

    print(f"\n🔍 Testing TSDR API endpoint...")
    print(f"URL: {url}")
    print(f"Serial Number: {serial_number}")

    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"\n📊 Response Status: {response.status_code}")

        if response.status_code == 200:
            print("✅ TSDR API is working!")

            try:
                # Try to parse JSON
                data = response.json()
                print(f"\n📄 Response type: JSON")
                print(f"Sample keys: {list(data.keys())[:5]}")
            except:
                # Might be XML
                print(f"\n📄 Response type: XML/Other")
                print(f"First 200 chars: {response.text[:200]}")

            return True

        elif response.status_code == 401:
            print(f"❌ Authentication failed - API key may be invalid")
            return False

        elif response.status_code == 404:
            print(f"⚠️  Serial number not found (this is okay, API is working)")
            return True

        else:
            print(f"⚠️  Unexpected status code: {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False

    except requests.exceptions.Timeout:
        print(f"❌ Request timed out")
        return False

    except requests.exceptions.RequestException as e:
        print(f"❌ Request error: {e}")
        return False


def test_trademark_checker_integration():
    """Test Brand Agent trademark checker with API key."""
    from src.tools.trademark_checker import search_trademarks_uspto

    print(f"\n🔍 Testing Brand Agent trademark checker...")

    # Test with a sample brand name
    result = search_trademarks_uspto("TestBrand", category="009", limit=10)

    print(f"\n📊 Trademark Search Results:")
    print(f"   Brand Name: {result['brand_name']}")
    print(f"   Risk Level: {result['risk_level']}")
    print(f"   Conflicts: {result['conflicts_found']}")
    print(f"   Source: {result['source']}")

    # Check if TSDR API is being used
    if "TSDR" in result['source']:
        print(f"\n✅ TSDR API integration active!")
        return True
    else:
        print(f"\n⚠️  Using simulation mode (API key might not be detected)")
        return False


def main():
    """Run all TSDR API tests."""
    print("=" * 70)
    print("USPTO TSDR API INTEGRATION TEST")
    print("=" * 70)

    results = {
        "API Key Present": False,
        "TSDR Endpoint": False,
        "Brand Agent Integration": False
    }

    # Test 1: API key present
    print("\n" + "-" * 70)
    print("TEST 1: API Key Configuration")
    print("-" * 70)
    results["API Key Present"] = test_api_key_present()

    if not results["API Key Present"]:
        print("\n❌ Cannot proceed without API key")
        print("Please add USPTO_API_KEY to your .env file")
        sys.exit(1)

    # Test 2: TSDR endpoint
    print("\n" + "-" * 70)
    print("TEST 2: TSDR API Endpoint")
    print("-" * 70)
    results["TSDR Endpoint"] = test_tsdr_endpoint()

    # Test 3: Brand Agent integration
    print("\n" + "-" * 70)
    print("TEST 3: Brand Agent Integration")
    print("-" * 70)
    results["Brand Agent Integration"] = test_trademark_checker_integration()

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    for test, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test}")

    all_passed = all(results.values())

    if all_passed:
        print("\n🎉 All tests passed! Your TSDR API is fully integrated.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")

    print("\n" + "=" * 70)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
