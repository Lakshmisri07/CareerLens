"""
List all available Gemini models for your API key
"""

from dotenv import load_dotenv
import os
import google.generativeai as genai

load_dotenv()
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ API key not found in .env")
    exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("Available Gemini Models")
print("=" * 60)

try:
    models = genai.list_models()
    
    generation_models = []
    for model in models:
        # Check if model supports generateContent
        if 'generateContent' in model.supported_generation_methods:
            generation_models.append(model.name)
            print(f"✅ {model.name}")
            print(f"   Description: {model.description[:80]}...")
            print(f"   Methods: {', '.join(model.supported_generation_methods)}")
            print()
    
    if generation_models:
        print("=" * 60)
        print(f"✅ Found {len(generation_models)} models for text generation")
        print("=" * 60)
        print("\nRecommended model to use:")
        print(f"👉 {generation_models[0]}")
    else:
        print("❌ No models found that support generateContent")
        
except Exception as e:
    print(f"❌ Error: {e}")