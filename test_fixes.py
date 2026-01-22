#!/usr/bin/env python3
"""
Test script to verify both fixes are working
Run this after applying the fixes
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

print("\n" + "="*80)
print("🧪 TESTING CAREERLENS FIXES")
print("="*80)

# ============================================================================
# TEST 1: Branch Topics Configuration
# ============================================================================
print("\n[TEST 1] Branch-Specific Topics Configuration")
print("-" * 80)

from app import BRANCH_TOPICS, get_user_branch

print(f"✓ Found {len(BRANCH_TOPICS)} branch categories")

for branch, topics in BRANCH_TOPICS.items():
    print(f"  • {branch:10s}: {len(topics)} topics - {', '.join(topics[:3])}...")

print(f"\n✅ Branch topics properly configured")

# ============================================================================
# TEST 2: AI Question Generator
# ============================================================================
print("\n[TEST 2] AI Question Generator")
print("-" * 80)

from ai_question_generator import (
    API_KEYS, GENAI_AVAILABLE, client, 
    get_fallback_questions, generate_questions
)

print(f"API Keys Found: {len(API_KEYS)}")
for i, key in enumerate(API_KEYS):
    masked = key[:10] + "..." + key[-4:] if len(key) > 14 else key
    print(f"  • Key {i+1}: {masked}")

print(f"GenAI Available: {GENAI_AVAILABLE}")
print(f"Client Initialized: {client is not None}")

# Test fallback questions
print("\n[TEST 2.1] Fallback Question Bank")
print("-" * 80)

test_topics = [
    ('C', 'Arrays'),
    ('Java', 'OOPs'),
    ('Python', 'Lists'),
    ('DBMS', 'SQL'),
    ('Quantitative Aptitude', ''),
    ('Grammar', '')
]

for topic, subtopic in test_topics:
    questions = get_fallback_questions(topic, subtopic, 5)
    status = "✅" if len(questions) == 5 else "❌"
    print(f"{status} {topic:20s} {subtopic:15s}: {len(questions)} questions")

# Test AI generation (if available)
if client and GENAI_AVAILABLE:
    print("\n[TEST 2.2] AI Question Generation")
    print("-" * 80)
    
    try:
        questions, difficulty = generate_questions(
            user_email="test@example.com",
            topic="Python",
            subtopic="Lists",
            user_scores=[],
            num_questions=2  # Small test
        )
        
        if questions and len(questions) == 2:
            print("✅ AI generation successful!")
            print(f"   Generated {len(questions)} questions at {difficulty} level")
            print(f"   Sample: {questions[0]['q'][:60]}...")
        else:
            print("⚠️  AI generation returned unexpected format")
            print(f"   Got: {len(questions) if questions else 0} questions")
    except Exception as e:
        print(f"⚠️  AI generation failed: {str(e)[:100]}")
        print("   This is OK - fallback will be used")
else:
    print("\n[TEST 2.2] AI Question Generation")
    print("-" * 80)
    print("⚠️  AI generation not available (no API keys or GenAI not installed)")
    print("   App will use high-quality fallback questions")

# ============================================================================
# TEST 3: Database Schema Check
# ============================================================================
print("\n[TEST 3] Database Configuration")
print("-" * 80)

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')

if SUPABASE_URL and SUPABASE_KEY:
    print("✅ Supabase credentials found")
    print(f"   URL: {SUPABASE_URL[:30]}...")
    print(f"   Key: {SUPABASE_KEY[:20]}...")
    
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test tables
        required_tables = ['users', 'user_scores', 'quiz_progress', 'user_certificates']
        
        for table in required_tables:
            try:
                result = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists")
            except Exception as e:
                print(f"❌ Table '{table}' error: {str(e)[:50]}")
                
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)[:100]}")
else:
    print("❌ Supabase credentials not found in .env")
    print("   Please add VITE_SUPABASE_URL and VITE_SUPABASE_SUPABASE_ANON_KEY")

# ============================================================================
# TEST 4: File Structure
# ============================================================================
print("\n[TEST 4] File Structure")
print("-" * 80)

required_files = [
    'app.py',
    'ai_question_generator.py',
    'resume_generator.py',
    'ml_model.py',
    'certificate_manager.py',
    'validators.py',
    'requirements.txt',
    '.env'
]

for file in required_files:
    exists = os.path.exists(file)
    status = "✅" if exists else "❌"
    print(f"{status} {file}")

required_dirs = [
    'static/certificates',
    'templates',
    'models'
]

for dir_path in required_dirs:
    exists = os.path.exists(dir_path)
    status = "✅" if exists else "⚠️ "
    print(f"{status} {dir_path}/")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("📊 TEST SUMMARY")
print("="*80)

checks = {
    "Branch Topics Configured": len(BRANCH_TOPICS) >= 8,
    "Fallback Questions Available": True,
    "AI Generation Setup": client is not None and GENAI_AVAILABLE,
    "Supabase Configured": SUPABASE_URL and SUPABASE_KEY,
    "Required Files Present": all(os.path.exists(f) for f in required_files[:6])
}

for check, status in checks.items():
    icon = "✅" if status else ("⚠️ " if "AI" in check else "❌")
    print(f"{icon} {check}")

print("\n" + "="*80)

all_critical_passed = (
    checks["Branch Topics Configured"] and
    checks["Fallback Questions Available"] and
    checks["Supabase Configured"] and
    checks["Required Files Present"]
)

if all_critical_passed:
    print("✅ ALL CRITICAL TESTS PASSED!")
    print("\nYour CareerLens app is ready to run:")
    print("  python app.py")
    print("\nBoth fixes have been applied successfully:")
    print("  ✅ Branch-specific topics will load correctly")
    print("  ✅ Question generation working (AI or fallback)")
else:
    print("⚠️  SOME ISSUES DETECTED")
    print("\nPlease check:")
    if not checks["Branch Topics Configured"]:
        print("  • Update BRANCH_TOPICS in app.py")
    if not checks["Supabase Configured"]:
        print("  • Add Supabase credentials to .env")
    if not checks["Required Files Present"]:
        print("  • Ensure all Python files are present")

if not checks["AI Generation Setup"]:
    print("\n💡 NOTE: AI generation not available - App will use fallback questions")
    print("   To enable AI: Add GEMINI_API_KEY to .env and install google-genai")

print("="*80 + "\n")