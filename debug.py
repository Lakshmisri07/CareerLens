"""
DEBUG: Check what's actually in the database
Run this to see the saved quiz data
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Replace with your email
USER_EMAIL = "your_email@example.com"  # <-- CHANGE THIS

print("\n" + "="*80)
print("CHECKING SAVED QUIZ PROGRESS")
print("="*80)

# Check what's saved
result = supabase.table('quiz_progress').select('*').eq('user_email', USER_EMAIL).execute()

if result.data:
    print(f"\n✅ Found {len(result.data)} saved quiz(es):\n")
    for item in result.data:
        print(f"Topic: '{item['topic']}'")
        print(f"Subtopic: '{item['subtopic']}' (type: {type(item['subtopic'])})")
        print(f"Subtopic is empty string: {item['subtopic'] == ''}")
        print(f"Subtopic is None: {item['subtopic'] is None}")
        print(f"Question: {item['current_question']}")
        print(f"Time left: {item['time_left']}")
        print("-" * 80)
else:
    print("\n❌ No saved progress found!")
    print("\nSteps to test:")
    print("1. Start a Grammar quiz")
    print("2. Answer 1 question")
    print("3. Click Save & Exit")
    print("4. Run this script again")

print("\n" + "="*80)
print("TESTING QUERY")
print("="*80)

# Test the exact query used
topic = "Grammar"
subtopic = None
search_subtopic = subtopic if subtopic else ''

print(f"\nSearching for:")
print(f"  topic = '{topic}'")
print(f"  subtopic = '{search_subtopic}' (type: {type(search_subtopic)})")

result2 = supabase.table('quiz_progress').select('*').eq('user_email', USER_EMAIL).eq('topic', topic).eq('subtopic', search_subtopic).execute()

if result2.data:
    print(f"\n✅ FOUND IT! Query works!")
else:
    print(f"\n❌ NOT FOUND! Query doesn't match!")
    print("\nThis means:")
    print("- Data is saved with different subtopic value")
    print("- Check what's actually in database above")