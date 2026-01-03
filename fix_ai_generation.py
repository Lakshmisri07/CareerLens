#!/usr/bin/env python3
"""
Diagnose and Fix AI Question Generation
This will identify why real questions aren't being generated
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("="*80)
print("🔍 DIAGNOSING AI QUESTION GENERATION")
print("="*80)

# Step 1: Check API Key
print("\n[Step 1] Checking Gemini API Key...")
api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file!")
    print("\n🔧 FIX:")
    print("1. Open your .env file")
    print("2. Add this line:")
    print("   GEMINI_API_KEY=your_actual_key_here")
    print("3. Get key from: https://aistudio.google.com/app/apikey")
    exit(1)

print(f"✅ API Key found: {api_key[:20]}...")

# Check if key looks valid
if not api_key.startswith('AIzaSy'):
    print("⚠️  WARNING: API key doesn't start with 'AIzaSy'")
    print("   This might not be a valid Gemini API key")
    print("   Get correct key from: https://aistudio.google.com/app/apikey")

# Step 2: Test API Connection
print("\n[Step 2] Testing Gemini API Connection...")

try:
    import google.generativeai as genai
    print("✅ google-generativeai package imported")
    
    genai.configure(api_key=api_key)
    print("✅ API configured")
    
    # Try to create model and generate test content
    print("\nTrying different models...")
    
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-pro', 
        'gemini-pro'
    ]
    
    working_model = None
    
    for model_name in models_to_try:
        try:
            print(f"\n  Testing {model_name}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say hello in one word")
            print(f"  ✅ {model_name} WORKS!")
            print(f"  Response: {response.text}")
            working_model = model_name
            break
        except Exception as e:
            print(f"  ❌ {model_name} failed: {str(e)[:80]}")
            continue
    
    if not working_model:
        print("\n❌ NO WORKING MODEL FOUND!")
        print("\n🔧 POSSIBLE ISSUES:")
        print("1. Invalid API key - get new one from https://aistudio.google.com/app/apikey")
        print("2. API quota exceeded - wait or create new key")
        print("3. Network/firewall blocking access")
        print("4. API key not activated yet - wait 1-2 minutes after creation")
        exit(1)
    
    print(f"\n✅ Working model found: {working_model}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\n🔧 FIXES:")
    print("1. Check internet connection")
    print("2. Verify API key is correct")
    print("3. Install package: pip install google-generativeai")
    exit(1)

# Step 3: Test Actual Question Generation
print("\n[Step 3] Testing Question Generation...")

try:
    # Import the actual function
    from ai_question_generator import generate_quiz_questions
    
    print("Generating 2 test questions for C - Arrays (beginner)...")
    questions = generate_quiz_questions('C', 'Arrays', 'beginner', 2)
    
    print(f"\n✅ Generated {len(questions)} questions")
    
    # Check if questions are real or fallback
    is_fallback = False
    
    for i, q in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"QUESTION {i}:")
        print(f"{'='*80}")
        print(f"Q: {q['q']}")
        print(f"\nOptions:")
        for j, opt in enumerate(q['options'], 1):
            marker = " ← CORRECT" if opt == q['answer'] else ""
            print(f"  {j}. {opt}{marker}")
        print(f"\nCorrect Answer: '{q['answer']}'")
        
        # Check if this is a fallback question
        if 'Sample' in q['q'] or 'Question' in q['q'][:20]:
            is_fallback = True
            print("⚠️  THIS LOOKS LIKE A FALLBACK QUESTION!")
        else:
            print("✅ This looks like a real AI-generated question")
    
    if is_fallback:
        print("\n" + "="*80)
        print("❌ PROBLEM FOUND: Using fallback questions!")
        print("="*80)
        print("\n🔧 This means AI generation is failing silently.")
        print("Let me check the ai_question_generator.py file...")
    else:
        print("\n" + "="*80)
        print("✅ SUCCESS! Real AI questions are being generated!")
        print("="*80)
        
except Exception as e:
    print(f"\n❌ Question generation failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 4: Detailed API Test
print("\n[Step 4] Detailed API Generation Test...")

try:
    import google.generativeai as genai
    import json
    
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(working_model)
    
    # Test with the exact prompt from ai_question_generator.py
    test_prompt = """You are an expert quiz creator for placement preparation. Generate 2 multiple-choice questions about: Arrays in C programming language

Difficulty Level: BEGINNER
Instructions: Focus on basic concepts, simple syntax, and fundamental understanding. Questions should test foundational knowledge.

CRITICAL REQUIREMENTS:
1. Each question MUST have EXACTLY 4 options
2. Questions must be at beginner difficulty level
3. The answer must be one of the 4 options (exact match)
4. Make questions practical and relevant to placement exams
5. Return ONLY valid JSON - no markdown, no code blocks, no extra text

JSON Format (return ONLY this):
{
    "questions": [
        {
            "q": "What is the time complexity of binary search?",
            "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
            "answer": "O(log n)"
        }
    ]
}

Generate exactly 2 questions now."""
    
    print("Sending test prompt to Gemini...")
    response = model.generate_content(test_prompt)
    
    print("\n📥 RAW RESPONSE:")
    print("-"*80)
    print(response.text[:500])  # First 500 chars
    print("-"*80)
    
    # Try to parse it
    response_text = response.text.strip()
    
    # Clean markdown if present
    if '```json' in response_text:
        response_text = response_text.split('```json')[1].split('```')[0].strip()
    elif '```' in response_text:
        response_text = response_text.split('```')[1].split('```')[0].strip()
    
    print("\n📝 CLEANED RESPONSE:")
    print("-"*80)
    print(response_text[:500])
    print("-"*80)
    
    # Try to parse JSON
    try:
        data = json.loads(response_text)
        questions = data.get('questions', [])
        
        print(f"\n✅ Successfully parsed {len(questions)} questions from JSON")
        
        if len(questions) > 0:
            print("\n✅✅✅ AI IS WORKING CORRECTLY! ✅✅✅")
            print("\nSample question from API:")
            print(f"Q: {questions[0]['q']}")
            print(f"Answer: {questions[0]['answer']}")
        else:
            print("\n⚠️  JSON parsed but no questions found")
            
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON parsing failed: {e}")
        print("\nThis means the API is returning text but not valid JSON")
        print("The prompt might need adjustment in ai_question_generator.py")
        
except Exception as e:
    print(f"\n❌ Detailed test failed: {e}")
    import traceback
    traceback.print_exc()

# Final Report
print("\n" + "="*80)
print("📊 DIAGNOSIS COMPLETE")
print("="*80)

if working_model and not is_fallback:
    print("\n✅ EVERYTHING LOOKS GOOD!")
    print("\n🎯 Next Steps:")
    print("1. Restart your Flask app: python app.py")
    print("2. Take a quiz")
    print("3. You should see real AI-generated questions")
    print("\n💡 If you still see fallback questions:")
    print("   - Check terminal output when taking quiz")
    print("   - Look for error messages in console")
    print("   - The app might be catching errors silently")
else:
    print("\n❌ ISSUES FOUND")
    print("\n🔧 FIXES TO TRY:")
    print("1. Get a NEW Gemini API key: https://aistudio.google.com/app/apikey")
    print("2. Wait 1-2 minutes after creating key for it to activate")
    print("3. Replace old key in .env file")
    print("4. Restart app and test again")
    print("\n5. If still not working, check if your region has access to Gemini API")
    print("6. Try using a VPN if Gemini is blocked in your region")

print("\n" + "="*80)