#!/usr/bin/env python3
"""
Comprehensive test suite for TDS Virtual TA API
"""
import requests
import json
import time
import base64
import os
from typing import Dict, Any


class TDSVirtualTATests:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/"
        self.health_url = f"{base_url}/health"
        self.stats_url = f"{base_url}/api/stats"
        
    def test_health_check(self) -> bool:
        """Test if the API is running"""
        try:
            response = requests.get(self.health_url, timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def test_api_endpoint(self, question: str, image_b64: str = None) -> Dict[str, Any]:
        """Test the main API endpoint"""
        payload = {"question": question}
        if image_b64:
            payload["image"] = image_b64
            
        try:
            response = requests.post(self.api_url, json=payload, timeout=10)
            return {
                "status_code": response.status_code,
                "response": response.json() if response.status_code == 200 else response.text,
                "success": response.status_code == 200
            }
        except Exception as e:
            return {
                "status_code": 0,
                "response": str(e),
                "success": False
            }
    
    def validate_response_format(self, response: Dict[str, Any]) -> bool:
        """Validate that the response has the correct format"""
        if not isinstance(response, dict):
            return False
        
        if "answer" not in response or "links" not in response:
            return False
            
        if not isinstance(response["answer"], str):
            return False
            
        if not isinstance(response["links"], list):
            return False
            
        for link in response["links"]:
            if not isinstance(link, dict):
                return False
            if "url" not in link or "text" not in link:
                return False
            if not isinstance(link["url"], str) or not isinstance(link["text"], str):
                return False
                
        return True
    
    def run_evaluation_tests(self):
        """Run the same tests as the promptfoo evaluation"""
        print("🧪 Running TDS Virtual TA Evaluation Tests")
        print("=" * 60)
        
        tests = [
            {
                "name": "GPT Model Usage Question",
                "question": "The question asks to use gpt-3.5-turbo-0125 model but the ai-proxy provided by Anand sir only supports gpt-4o-mini. So should we just use gpt-4o-mini or use the OpenAI API for gpt3.5 turbo?",
                "expected_keywords": ["gpt-3.5-turbo-0125", "OpenAI API"],
                "expected_links": ["discourse.onlinedegree.iitm.ac.in"]
            },
            {
                "name": "Dashboard Scoring Question", 
                "question": "If a student scores 10/10 on GA4 as well as a bonus, how would it appear on the dashboard?",
                "expected_keywords": ["110", "dashboard"],
                "expected_links": ["discourse.onlinedegree.iitm.ac.in", "ga4"]
            },
            {
                "name": "Docker vs Podman Question",
                "question": "I know Docker but have not used Podman before. Should I use Docker for this course?",
                "expected_keywords": ["Podman", "Docker", "acceptable"],
                "expected_links": ["tds.s-anand.net", "docker"]
            },
            {
                "name": "Future Schedule Question",
                "question": "When is the TDS Sep 2025 end-term exam?",
                "expected_keywords": ["don't know", "not available"],
                "expected_links": []
            }
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for i, test in enumerate(tests, 1):
            print(f"\n📝 Test {i}/{total_tests}: {test['name']}")
            print("-" * 40)
            
            result = self.test_api_endpoint(test["question"])
            
            if not result["success"]:
                print(f"❌ API call failed: {result['response']}")
                continue
                
            response = result["response"]
            
            # Validate response format
            if not self.validate_response_format(response):
                print("❌ Invalid response format")
                continue
                
            print(f"✅ Valid JSON response format")
            
            # Check answer content
            answer = response["answer"].lower()
            answer_score = 0
            
            for keyword in test["expected_keywords"]:
                if keyword.lower() in answer:
                    answer_score += 1
                    print(f"✅ Found expected keyword: '{keyword}'")
                else:
                    print(f"⚠️  Missing keyword: '{keyword}'")
            
            # Check links
            links = response["links"]
            link_score = 0
            
            for expected_link in test["expected_links"]:
                found = any(expected_link.lower() in link["url"].lower() for link in links)
                if found:
                    link_score += 1
                    print(f"✅ Found expected link pattern: '{expected_link}'")
                else:
                    print(f"⚠️  Missing link pattern: '{expected_link}'")
            
            # Overall test scoring
            if answer_score >= len(test["expected_keywords"]) // 2 and link_score >= len(test["expected_links"]) // 2:
                passed_tests += 1
                print(f"✅ Test PASSED")
            else:
                print(f"❌ Test FAILED")
                
            print(f"Answer: {response['answer'][:100]}...")
            print(f"Links provided: {len(links)}")
        
        print("\n" + "=" * 60)
        print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! API is working correctly.")
        elif passed_tests >= total_tests * 0.75:
            print("✅ Most tests passed. API is functioning well.")
        else:
            print("⚠️  Several tests failed. API needs improvement.")
            
        return passed_tests / total_tests
    
    def test_with_image(self):
        """Test API with image attachment"""
        print("\n🖼️  Testing with image attachment...")
        
        # Try to load an image file
        image_files = ["image.png", "image.webp", "project-tds-virtual-ta-q1.webp"]
        image_b64 = None
        
        for img_file in image_files:
            if os.path.exists(img_file):
                try:
                    with open(img_file, "rb") as f:
                        image_b64 = base64.b64encode(f.read()).decode('utf-8')
                    print(f"✅ Loaded image: {img_file}")
                    break
                except Exception as e:
                    print(f"⚠️  Failed to load {img_file}: {e}")
        
        if image_b64:
            result = self.test_api_endpoint(
                "Should I use gpt-4o-mini which AI proxy supports, or gpt3.5 turbo?",
                image_b64
            )
            
            if result["success"]:
                print("✅ API handled image attachment successfully")
                return True
            else:
                print(f"❌ API failed with image: {result['response']}")
                return False
        else:
            print("⚠️  No image files found to test with")
            return None


def main():
    print("🚀 Starting TDS Virtual TA Comprehensive Tests")
    
    tester = TDSVirtualTATests()
    
    # Check if API is running
    if not tester.test_health_check():
        print("❌ API is not running. Please start it with: python app.py")
        return False
    
    print("✅ API is running and healthy")
    
    # Run evaluation tests
    score = tester.run_evaluation_tests()
    
    # Test image functionality
    tester.test_with_image()
    
    # Get API stats
    try:
        response = requests.get(tester.stats_url, timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print(f"\n📈 API Statistics:")
            print(f"   Discourse topics: {stats.get('discourse_topics', 0)}")
            print(f"   Course content sections: {stats.get('course_content_sections', 0)}")
            print(f"   Predefined answer categories: {stats.get('predefined_answer_categories', 0)}")
    except:
        print("⚠️  Could not retrieve API statistics")
    
    print(f"\n🏆 Overall Score: {score:.1%}")
    return score >= 0.75


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)