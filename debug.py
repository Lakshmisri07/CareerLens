from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Replace with your actual email
USER_EMAIL = "your_email@example.com"

print("\n" + "="*80)
print("CHECKING GRAMMAR QUIZ SAVE")
print("="*80)

# Check saved progress
result = supabase.table('quiz_progress').select('*').eq('user_email', USER_EMAIL).execute()

if result.data:
    print(f"\nFound {len(result.data)} saved quiz(es):")
    for item in result.data:
        print(f"\nTopic: '{item['topic']}'")
        print(f"Subtopic: '{item['subtopic']}' (value: {repr(item['subtopic'])})")
        print(f"Question: {item['current_question']}/5")
        print(f"Time: {item['time_left']}s")
else:
    print("\n❌ No saved progress")

print("\n" + "="*80)