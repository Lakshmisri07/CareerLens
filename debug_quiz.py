"""
Debug script to see actual questions and answers
"""

from ai_question_generator import get_adaptive_questions

print("=" * 80)
print("🔍 DEBUGGING QUIZ QUESTIONS")
print("=" * 80)

# Generate a test quiz
result = get_adaptive_questions(
    user_email="debug@test.com",
    topic="C",
    subtopic="Arrays",
    user_scores=[],
    num_questions=3
)

print(f"\nDifficulty: {result['difficulty']}")
print(f"Total Questions: {len(result['questions'])}\n")

# Print each question with details
for i, q in enumerate(result['questions'], 1):
    print(f"\n{'='*80}")
    print(f"QUESTION {i}:")
    print(f"{'='*80}")
    print(f"Q: {q['q']}")
    print(f"\nOptions:")
    for j, opt in enumerate(q['options'], 1):
        marker = "✓ CORRECT" if opt == q['answer'] else ""
        print(f"  {j}. {opt} {marker}")
    print(f"\nCorrect Answer: '{q['answer']}'")
    print(f"Answer Type: {type(q['answer'])}")
    print(f"Answer Length: {len(q['answer'])} chars")
    print(f"Answer repr: {repr(q['answer'])}")
    
    # Check if answer is in options
    if q['answer'] in q['options']:
        print("✅ Answer IS in options")
    else:
        print("❌ Answer NOT in options - THIS IS THE PROBLEM!")
        print(f"   Checking similarity...")
        for opt in q['options']:
            if q['answer'].strip().lower() == opt.strip().lower():
                print(f"   ⚠️  Case/whitespace mismatch: '{q['answer']}' vs '{opt}'")

print("\n" + "=" * 80)
print("🔍 DEBUG COMPLETE")
print("=" * 80)