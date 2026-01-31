from supabase import create_client, Client

SUPABASE_URL = input("Enter your Supabase URL: ")
SUPABASE_KEY = input("Enter your Supabase API Key: ")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Fetch one question to test
result = supabase.table('predefined_questions')\
    .select('*')\
    .eq('topic', 'Quantitative Aptitude')\
    .limit(1)\
    .execute()

if result.data:
    question = result.data[0]
    print("Sample question from database:")
    print("="*70)
    print(f"ID: {question['id']}")
    print(f"Topic: {question['topic']}")
    print(f"Question: {question['question']}")
    print(f"Options: {question['options']}")
    print(f"Options type: {type(question['options'])}")
    print(f"Answer: {question['answer']}")
    print(f"Answer type: {type(question['answer'])}")
    print("="*70)
    
    # Validation checks
    print("\nValidation checks:")
    print(f"✓ Options is list: {isinstance(question['options'], list)}")
    print(f"✓ Options has 4 items: {len(question['options']) == 4 if isinstance(question['options'], list) else False}")
    print(f"✓ Answer is string: {isinstance(question['answer'], str)}")
    print(f"✓ Answer is A/B/C/D: {question['answer'] in ['A', 'B', 'C', 'D']}")
    
    if isinstance(question['options'], list) and len(question['options']) == 4:
        print("\nOptions content:")
        for i, opt in enumerate(question['options']):
            print(f"  {i}: {opt}")
else:
    print("No questions found!")