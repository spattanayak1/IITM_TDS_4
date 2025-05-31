#!/usr/bin/env python3
"""
Interactive Test Script for TDS Virtual TA
Ask any question to test the API
"""

import requests
import json
import base64
from pathlib import Path

API_URL = "http://localhost:8000/api/"

def encode_image(image_path):
    """Encode image to base64"""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None

def test_question(question, image_path=None):
    """Test a single question"""
    payload = {"question": question}
    
    if image_path and Path(image_path).exists():
        image_base64 = encode_image(image_path)
        if image_base64:
            payload["image"] = image_base64
            print(f"📷 Image attached: {image_path}")
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Response received!")
            print(f"📝 Answer: {result['answer']}")
            print(f"🔗 Links: {len(result['links'])} provided")
            for i, link in enumerate(result['links'], 1):
                print(f"  {i}. {link['title']}: {link['url']}")
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error. Make sure the API is running:")
        print("   Run: python app.py")
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    print("🤖 TDS Virtual TA - Interactive Test")
    print("=" * 50)
    print("Ask any question about TDS course!")
    print("Type 'quit' or 'exit' to stop")
    print("Type 'image <path>' to add an image to your next question")
    print("=" * 50)
    
    image_path = None
    
    while True:
        print("\n" + "─" * 30)
        user_input = input("❓ Your question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
            
        if user_input.lower().startswith('image '):
            image_path = user_input[6:].strip()
            if Path(image_path).exists():
                print(f"📷 Image set: {image_path}")
            else:
                print(f"❌ Image not found: {image_path}")
                image_path = None
            continue
            
        if not user_input:
            print("⚠️  Please enter a question")
            continue
            
        print(f"🔄 Asking: {user_input}")
        test_question(user_input, image_path)
        
        # Reset image after use
        if image_path:
            image_path = None

if __name__ == "__main__":
    main()