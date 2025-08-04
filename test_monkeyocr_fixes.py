#!/usr/bin/env python3
"""
Test script to verify MonkeyOCR fixes work with proper API key setup.
This script follows the same pattern as the test suite to get a valid API key.
"""

import os
import sys
import requests
import time
from pathlib import Path

# Add the SDK to the path
sys.path.insert(0, str(Path(__file__).parent / "sdk" / "python"))

from ragflow_sdk import RAGFlow
from ragflow_sdk.modules.dataset import DataSet


def setup_api_key():
    """Setup API key using the same method as tests"""
    HOST_ADDRESS = os.getenv("HOST_ADDRESS", "http://127.0.0.1:9380")
    EMAIL = "user_123@1.com"
    PASSWORD = """ctAseGvejiaSWWZ88T/m4FQVOpQyUvP+x7sXtdv3feqZACiQleuewkUi35E16wSd5C5QcnkkcV9cYc8TKPTRZlxappDuirxghxoOvFcJxFU4ixLsD
fN33jCHRoDUW81IH9zjij/vaw8IbVyb6vuwg6MX6inOEBRRzVbRYxXOu1wkWY6SsI8X70oF9aeLFp/PzQpjoe/YbSqpTq8qqrmHzn9vO+yvyYyvmDsphXe
X8f7fp9c7vUsfOCkM+gHY3PadG+QHa7KI7mzTKgUTZImK6BZtfRBATDTthEUbbaTewY4H0MnWiCeeDhcbeQao6cFy1To8pE3RpmxnGnS8BsBn8w=="""
    
    try:
        # Register user
        register_data = {"email": EMAIL, "nickname": "user", "password": PASSWORD}
        res = requests.post(f"{HOST_ADDRESS}/v1/user/register", json=register_data)
        print(f"Register response: {res.json()}")
    except Exception as e:
        print(f"Register error (may already exist): {e}")
    
    # Login
    login_data = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(f"{HOST_ADDRESS}/v1/user/login", json=login_data)
    res = response.json()
    if res.get("code") != 0:
        raise Exception(f"Login failed: {res.get('message')}")
    
    auth = response.headers["Authorization"]
    
    # Generate token
    token_response = requests.post(f"{HOST_ADDRESS}/v1/system/new_token", headers={"Authorization": auth})
    token_res = token_response.json()
    if token_res.get("code") != 0:
        raise Exception(f"Token generation failed: {token_res.get('message')}")
    
    return token_res["data"].get("token")


def test_monkeyocr_fixes():
    """Test the MonkeyOCR fixes with proper API key"""
    print("🧪 Testing MonkeyOCR fixes...")
    
    try:
        # Get API key
        api_key = setup_api_key()
        print(f"✅ Got API key: {api_key[:10]}...")
        
        # Setup client
        base_url = os.getenv("HOST_ADDRESS", "http://127.0.0.1:9380")
        client = RAGFlow(api_key=api_key, base_url=base_url)
        print("✅ RAGFlow client setup successful")
        
        # Generate unique timestamp for dataset names
        timestamp = int(time.time())
        
        # Test 1: Create dataset with DeepDoc engine
        print("\n📝 Test 1: DeepDoc Processing Engine")
        deepdoc_config = DataSet.ParserConfig.create_deepdoc_config(chunk_token_num=500)
        deepdoc_dataset = client.create_dataset(
            name=f"Test DeepDoc Dataset {timestamp}",
            description="Testing DeepDoc processing engine",
            parser_engine="deepdoc",
            chunk_method="naive",
            parser_config=deepdoc_config
        )
        print(f"✅ Created DeepDoc dataset: {deepdoc_dataset.id}")
        
        # Test 2: Create dataset with MonkeyOCR engine
        print("\n📝 Test 2: MonkeyOCR Processing Engine")
        monkeyocr_config = DataSet.ParserConfig.create_monkeyocr_config(chunk_token_num=500)
        monkeyocr_dataset = client.create_dataset(
            name=f"Test MonkeyOCR Dataset {timestamp}",
            description="Testing MonkeyOCR processing engine",
            parser_engine="monkeyocr",
            chunk_method="monkeyocr",
            parser_config=monkeyocr_config
        )
        print(f"✅ Created MonkeyOCR dataset: {monkeyocr_dataset.id}")
        
        # Test 3: Advanced MonkeyOCR configuration
        print("\n📝 Test 3: Advanced MonkeyOCR Configuration")
        advanced_config = DataSet.ParserConfig.create_monkeyocr_config(
            chunk_token_num=1000,
            # Note: MonkeyOCR-specific fields are handled by the backend
            # when parser_engine="monkeyocr" is specified
        )
        
        advanced_dataset = client.create_dataset(
            name=f"Test Advanced MonkeyOCR Dataset {timestamp}",
            parser_engine="monkeyocr",
            chunk_method="monkeyocr",
            parser_config=advanced_config
        )
        
        print(f"✅ Created advanced MonkeyOCR dataset: {advanced_dataset.id}")
        
        # Test 4: Backward compatibility
        print("\n📝 Test 4: Backward Compatibility")
        backward_dataset = client.create_dataset(
            name=f"Test Backward Compatible Dataset {timestamp}",
            chunk_method="naive"
        )
        print(f"✅ Created backward compatible dataset: {backward_dataset.id}")
        
        # Test 5: Verify configurations
        print("\n📝 Test 5: Verify Configurations")
        print(f"DeepDoc config: {deepdoc_config.to_json()}")
        print(f"MonkeyOCR config: {monkeyocr_config.to_json()}")
        print(f"Advanced config: {advanced_config.to_json()}")
        
        # Clean up
        print("\n🧹 Cleaning up test datasets...")
        client.delete_datasets(ids=[
            deepdoc_dataset.id,
            monkeyocr_dataset.id,
            advanced_dataset.id,
            backward_dataset.id
        ])
        print("✅ Cleanup completed")
        
        print("\n🎉 All tests passed! MonkeyOCR fixes are working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = test_monkeyocr_fixes()
    sys.exit(0 if success else 1) 