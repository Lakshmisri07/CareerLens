#!/usr/bin/env python3
"""
Test script to verify answer validation fix
"""

def normalize_and_match(question_dict):
    """
    Simulate the AI question normalization process
    """
    normalized_options = [str(opt).strip() for opt in question_dict['options']]
    normalized_answer = str(question_dict['answer']).strip()

    # Check if answer exists in options (case-insensitive)
    answer_in_options = False
    matched_option = normalized_answer

    for opt in normalized_options:
        if opt.lower() == normalized_answer.lower():
            answer_in_options = True
            matched_option = opt  # Use the exact option text as answer
            break

    return {
        'q': question_dict['q'],
        'options': normalized_options,
        'answer': matched_option,
        'valid': answer_in_options
    }

# Test cases
test_questions = [
    {
        'q': 'What is 2+2?',
        'options': ['3', '4', '5', '6'],
        'answer': '4'  # Exact match
    },
    {
        'q': 'What is the capital of France?',
        'options': ['London', 'Paris', 'Berlin', 'Madrid'],
        'answer': 'paris'  # Different case
    },
    {
        'q': 'Which is a programming language?',
        'options': ['Python', 'Snake', 'Java', 'Coffee'],
        'answer': ' Python '  # Extra spaces
    },
    {
        'q': 'What is the result?',
        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
        'answer': 'B'  # Wrong format - should fail
    }
]

print("="*80)
print("Testing Answer Normalization and Validation")
print("="*80)

for i, q in enumerate(test_questions):
    print(f"\nTest {i+1}:")
    print(f"Question: {q['q']}")
    print(f"Options: {q['options']}")
    print(f"Raw Answer: '{q['answer']}'")

    result = normalize_and_match(q)

    if result['valid']:
        print(f"✅ VALID - Normalized Answer: '{result['answer']}'")

        # Simulate user selecting the correct option
        user_selection = result['answer']
        is_correct = user_selection.lower() == result['answer'].lower()
        print(f"   User selects: '{user_selection}' -> {'CORRECT' if is_correct else 'WRONG'}")
    else:
        print(f"❌ INVALID - Answer '{q['answer']}' not found in options")

print("\n" + "="*80)
print("Test complete!")
print("="*80)
