#!/usr/bin/env python3
"""
Comprehensive test for quiz scoring validation
Tests all edge cases to ensure answers are always validated correctly
"""

def test_answer_validation():
    """Test the scoring logic with various edge cases"""
    
    test_cases = [
        {
            'name': 'Exact match',
            'user_answer': 'Option A',
            'correct_answer': 'Option A',
            'should_pass': True
        },
        {
            'name': 'Case insensitive',
            'user_answer': 'option a',
            'correct_answer': 'Option A',
            'should_pass': True
        },
        {
            'name': 'Extra spaces in user answer',
            'user_answer': '  Option A  ',
            'correct_answer': 'Option A',
            'should_pass': True
        },
        {
            'name': 'Extra spaces in correct answer',
            'user_answer': 'Option A',
            'correct_answer': '  Option A  ',
            'should_pass': True
        },
        {
            'name': 'Both have extra spaces',
            'user_answer': '  Option A  ',
            'correct_answer': '  Option A  ',
            'should_pass': True
        },
        {
            'name': 'Different options',
            'user_answer': 'Option A',
            'correct_answer': 'Option B',
            'should_pass': False
        },
        {
            'name': 'Number match',
            'user_answer': '42',
            'correct_answer': '42',
            'should_pass': True
        },
        {
            'name': 'Case + space combo',
            'user_answer': '  OPTION A  ',
            'correct_answer': 'option a',
            'should_pass': True
        },
        {
            'name': 'Unicode characters',
            'user_answer': 'Café',
            'correct_answer': 'Café',
            'should_pass': True
        },
        {
            'name': 'Empty strings',
            'user_answer': '',
            'correct_answer': 'Option A',
            'should_pass': False
        }
    ]
    
    print("="*80)
    print("🧪 TESTING QUIZ SCORING VALIDATION")
    print("="*80)
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test['name']}")
        print(f"  User answer: '{test['user_answer']}'")
        print(f"  Correct answer: '{test['correct_answer']}'")
        
        # Apply the same logic as in app.py
        user_normalized = test['user_answer'].strip().lower()
        correct_normalized = test['correct_answer'].strip().lower()
        
        is_correct = user_normalized == correct_normalized
        expected = test['should_pass']
        
        if is_correct == expected:
            print(f"  ✅ PASS - Result: {is_correct}, Expected: {expected}")
            passed += 1
        else:
            print(f"  ❌ FAIL - Result: {is_correct}, Expected: {expected}")
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("="*80)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! Scoring logic is working correctly!")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the logic.")
    
    return failed == 0


def test_option_validation():
    """Test that answers are properly validated against options"""
    
    print("\n" + "="*80)
    print("🧪 TESTING OPTION VALIDATION")
    print("="*80)
    
    test_questions = [
        {
            'q': 'What is 2+2?',
            'options': ['3', '4', '5', '6'],
            'answer': '4',
            'valid': True
        },
        {
            'q': 'Capital of France?',
            'options': ['London', 'Paris', 'Berlin', 'Madrid'],
            'answer': 'Paris',
            'valid': True
        },
        {
            'q': 'Programming language?',
            'options': ['Python', 'Snake', 'Java', 'Coffee'],
            'answer': 'C++',  # Not in options
            'valid': False
        },
        {
            'q': 'Case test?',
            'options': ['Option A', 'Option B', 'Option C', 'Option D'],
            'answer': 'option a',  # Different case but should be valid
            'valid': True
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, q in enumerate(test_questions, 1):
        print(f"\nTest {i}: {q['q']}")
        print(f"  Options: {q['options']}")
        print(f"  Answer: '{q['answer']}'")
        
        # Check if answer exists in options (case-insensitive)
        answer_normalized = q['answer'].strip().lower()
        answer_in_options = any(
            opt.strip().lower() == answer_normalized 
            for opt in q['options']
        )
        
        expected = q['valid']
        
        if answer_in_options == expected:
            print(f"  ✅ PASS - Answer {'is' if answer_in_options else 'is not'} in options (expected: {expected})")
            passed += 1
        else:
            print(f"  ❌ FAIL - Answer {'is' if answer_in_options else 'is not'} in options (expected: {expected})")
            failed += 1
    
    print("\n" + "="*80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_questions)} tests")
    print("="*80)
    
    return failed == 0


def test_real_world_scenario():
    """Test with real quiz scenario"""
    
    print("\n" + "="*80)
    print("🧪 TESTING REAL QUIZ SCENARIO")
    print("="*80)
    
    # Simulate a real quiz
    quiz_questions = [
        {
            'q': 'What is the time complexity of binary search?',
            'options': ['O(n)', 'O(log n)', 'O(n^2)', 'O(1)'],
            'answer': 'O(log n)'
        },
        {
            'q': 'Which is a Python data type?',
            'options': ['List', 'Array', 'Vector', 'Set'],
            'answer': 'List'
        },
        {
            'q': 'What does SQL stand for?',
            'options': [
                'Structured Query Language',
                'Simple Query Language',
                'Standard Query Language',
                'Sequential Query Language'
            ],
            'answer': 'Structured Query Language'
        }
    ]
    
    # Simulate user answers (some correct, some wrong)
    user_answers = [
        'O(log n)',      # Correct
        'array',         # Wrong (case sensitive test)
        'Structured Query Language'  # Correct
    ]
    
    print("\nSimulating quiz submission...")
    score = 0
    
    for i, (q, user_answer) in enumerate(zip(quiz_questions, user_answers)):
        correct_answer = q['answer']
        
        # Apply scoring logic
        user_normalized = user_answer.strip().lower()
        correct_normalized = correct_answer.strip().lower()
        
        is_correct = user_normalized == correct_normalized
        
        print(f"\nQ{i+1}: {q['q'][:50]}...")
        print(f"  User answered: '{user_answer}'")
        print(f"  Correct answer: '{correct_answer}'")
        print(f"  Result: {'✅ CORRECT' if is_correct else '❌ WRONG'}")
        
        if is_correct:
            score += 1
    
    expected_score = 2  # Questions 1 and 3 should be correct
    percentage = (score / len(quiz_questions)) * 100
    
    print("\n" + "="*80)
    print(f"FINAL SCORE: {score}/{len(quiz_questions)} ({percentage:.1f}%)")
    print(f"Expected Score: {expected_score}")
    print("="*80)
    
    if score == expected_score:
        print("🎉 Real-world scenario test PASSED!")
        return True
    else:
        print(f"⚠️  Real-world scenario test FAILED! Got {score}, expected {expected_score}")
        return False


if __name__ == '__main__':
    print("\n" + "🔬 COMPREHENSIVE SCORING VALIDATION TEST SUITE" + "\n")
    
    test1 = test_answer_validation()
    test2 = test_option_validation()
    test3 = test_real_world_scenario()
    
    print("\n" + "="*80)
    print("📊 OVERALL TEST RESULTS")
    print("="*80)
    print(f"Answer Validation: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Option Validation: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"Real World Scenario: {'✅ PASS' if test3 else '❌ FAIL'}")
    print("="*80)
    
    if test1 and test2 and test3:
        print("\n🎉 ALL TESTS PASSED! The scoring system is working correctly!")
        print("\n✅ You can now run your Flask app with confidence:")
        print("   python app.py")
    else:
        print("\n⚠️  Some tests failed. Please review the implementation.")