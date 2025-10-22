"""
Quick test script to verify Gemini API key works
Run this after setting up your .env file
"""

from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv('GEMINI_API_KEY')

print("=" * 50)
print("Testing Gemini API Setup")
print("=" * 50)

# Check if key exists
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file")
    print("\nPlease add this line to your .env file:")
    print("GEMINI_API_KEY=your_actual_key_here")
    exit(1)

print(f"✅ API Key found: {api_key[:20]}...")

# Try to import and configure
try:
    import google.generativeai as genai
    print("✅ google-generativeai package installed")
    
    # Configure with key
    genai.configure(api_key=api_key)
    print("✅ API key configured successfully")
    
    # Test generation - try different model names
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ Model loaded: gemini-1.5-flash")
    except:
        try:
            model = genai.GenerativeModel('gemini-1.5-pro')
            print("✅ Model loaded: gemini-1.5-pro")
        except:
            model = genai.GenerativeModel('gemini-pro')
            print("✅ Model loaded: gemini-pro")
    
    print("\n🔄 Testing AI generation...")
    response = model.generate_content("Say hello in one word")
    print(f"✅ AI Response: {response.text}")
    
    print("\n" + "=" * 50)
    print("🎉 SUCCESS! Gemini AI is working perfectly!")
    print("=" * 50)
    print("\nYou can now integrate AI into your quiz app.")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nTroubleshooting:")
    print("1. Check if your API key is correct")
    print("2. Ensure you have internet connection")
    print("3. Run: pip install google-generativeai python-dotenv")