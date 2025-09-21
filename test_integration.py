#!/usr/bin/env python3
"""
Test script to verify SmartGuard AI integration is working properly.
"""

import os
import sys
from dotenv import load_dotenv

# Load environment
load_dotenv()

def test_gemini_client():
    """Test GeminiClient functionality"""
    print("🧪 Testing GeminiClient...")
    try:
        from gemini_client import GeminiClient
        
        # Check if API key is available
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_gemini_api_key_here":
            print("⚠️ GEMINI_API_KEY not configured - skipping AI tests")
            return False
        
        # Test client initialization
        client = GeminiClient()
        print("✅ GeminiClient initialized successfully")
        
        # Test log summarization
        test_log = "Error: Database connection failed at 2024-01-15 10:30:00"
        summary = client.summarize_log(test_log)
        print(f"✅ Log summarization test: {summary[:100]}...")
        
        # Test chat response
        chat_response = client.chat_response("What's the system status?")
        print(f"✅ Chat response test: {chat_response[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ GeminiClient test failed: {e}")
        return False

def test_smartguard_integration():
    """Test SmartGuard integration"""
    print("\n🧪 Testing SmartGuard Integration...")
    try:
        from smartguard_integration import smartguard_integration
        
        print(f"✅ SmartGuard integration available: {smartguard_integration.available}")
        
        # Test enhanced sample logs
        logs = smartguard_integration.get_enhanced_sample_logs(5)
        print(f"✅ Generated {len(logs)} enhanced sample logs")
        
        # Test log analysis
        if smartguard_integration.available:
            analysis = smartguard_integration.analyze_with_ai(logs)
            print(f"✅ AI analysis test: {analysis[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ SmartGuard integration test failed: {e}")
        return False

def test_api_imports():
    """Test API imports"""
    print("\n🧪 Testing API imports...")
    try:
        from api import app, AI_AVAILABLE, smartguard_integration
        print(f"✅ API imports successful")
        print(f"✅ AI available: {AI_AVAILABLE}")
        print(f"✅ SmartGuard integration available: {smartguard_integration.available}")
        return True
        
    except Exception as e:
        print(f"❌ API import test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🛡️ SmartGuard AI Integration Test Suite")
    print("=" * 50)
    
    tests = [
        test_api_imports,
        test_smartguard_integration,
        test_gemini_client,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! SmartGuard AI integration is working properly.")
        return 0
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
