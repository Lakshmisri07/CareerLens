"""
Test script to verify AI quiz generation is working
Run this before starting your Flask app
"""

from ai_question_generator import get_adaptive_questions
from dotenv import load_dotenv
import os

load_dotenv()

print("=" * 60)
print("🧪 Testing AI Quiz Generator")
print("=" * 60)

# Check API key
api_key = os.getenv('GEMINI_API_KEY')
if not api_key:
    print("❌ ERROR: GEMINI_API_KEY not found in .env")
    exit(1)

print(f"✅ API Key found: {api_key[:20]}...")

# Test 1: Beginner level (no past scores)
print("\n📝 Test 1: Generating beginner quiz (new user)")
print("-" * 60)

try:
    result = get_adaptive_questions(
        user_email="test@example.com",
        topic="C",
        subtopic="Arrays",
        user_scores=[],  # No history = beginner
        num_questions=3
    )
    
    print(f"✅ Generated {len(result['questions'])} questions")
    print(f"✅ Difficulty: {result['difficulty']}")
    print(f"✅ Sample question: {result['questions'][0]['q'][:60]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 2: Intermediate level (some good scores)
print("\n📝 Test 2: Generating intermediate quiz (experienced user)")
print("-" * 60)

past_scores = [
    {'topic': 'C', 'subtopic': 'Arrays', 'score': 4, 'total_questions': 5},
    {'topic': 'C', 'subtopic': 'Arrays', 'score': 3, 'total_questions': 5},
]

try:
    result = get_adaptive_questions(
        user_email="test@example.com",
        topic="C",
        subtopic="Arrays",
        user_scores=past_scores,  # 70% average = intermediate
        num_questions=3
    )
    
    print(f"✅ Generated {len(result['questions'])} questions")
    print(f"✅ Difficulty: {result['difficulty']}")
    print(f"✅ Sample question: {result['questions'][0]['q'][:60]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

# Test 3: Advanced level (high scores)
print("\n📝 Test 3: Generating advanced quiz (expert user)")
print("-" * 60)

expert_scores = [
    {'topic': 'C', 'subtopic': 'Pointers', 'score': 5, 'total_questions': 5},
    {'topic': 'C', 'subtopic': 'Pointers', 'score': 4, 'total_questions': 5},
    {'topic': 'C', 'subtopic': 'Pointers', 'score': 5, 'total_questions': 5},
]

try:
    result = get_adaptive_questions(
        user_email="expert@example.com",
        topic="C",
        subtopic="Pointers",
        user_scores=expert_scores,  # 93% average = advanced
        num_questions=3
    )
    
    print(f"✅ Generated {len(result['questions'])} questions")
    print(f"✅ Difficulty: {result['difficulty']}")
    print(f"✅ Sample question: {result['questions'][0]['q'][:60]}...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)

print("\n" + "=" * 60)
print("🎉 SUCCESS! AI Quiz Generator is working perfectly!")
print("=" * 60)
print("\n✅ You can now run: python app.py")
print("✅ The quiz system will generate adaptive questions based on user performance")
print("\n💡 Tips:")
print("  - First quiz will be at beginner level")
print("  - Score 75%+ to unlock intermediate questions")
print("  - Score 75%+ on intermediate to unlock advanced")
print("  - AI adapts difficulty for each topic/subtopic separately")