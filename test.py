import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Load keys
API_KEYS = []
for i in range(1, 11):
    key = os.getenv(f"GEMINI_API_KEY_{i}")
    if key:
        API_KEYS.append(key.strip())

print(f"✅ Loaded {len(API_KEYS)} API keys\n")

# Test 5 models with random keys
test_models = [
    'gemini-flash-latest',
    'gemini-2.0-flash-001',
    'gemini-2.5-flash-lite',
    'gemini-exp-1206',
    'gemini-3-flash-preview',
]

import random
success = 0
for model_name in test_models:
    key_idx = random.randint(0, len(API_KEYS) - 1)
    try:
        genai.configure(api_key=API_KEYS[key_idx])
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say OK")
        print(f"✅ Key {key_idx+1} + {model_name[:25]}: SUCCESS")
        success += 1
    except Exception as e:
        if '429' in str(e):
            print(f"⚠️ Key {key_idx+1} + {model_name[:25]}: QUOTA")
        else:
            print(f"❌ Key {key_idx+1} + {model_name[:25]}: ERROR")

print(f"\n🎯 Result: {success}/5 models working")