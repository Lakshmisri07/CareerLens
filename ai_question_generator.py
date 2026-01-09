# ai_question_generator.py - MULTI-KEY VERSION

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Get multiple API keys from environment
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
    os.getenv("GEMINI_API_KEY_4"),
]
# Remove None values
API_KEYS = [k for k in API_KEYS if k]

if not API_KEYS:
    print("WARNING: No API keys found in .env file!")

current_key_index = 0

def get_client():
    """Get a working GenAI client, rotating through available keys"""
    global current_key_index
    
    if not API_KEYS:
        return None
    
    # Try each key once
    for attempt in range(len(API_KEYS)):
        try:
            key = API_KEYS[current_key_index]
            client = genai.Client(api_key=key)
            print(f"✓ Using API key #{current_key_index + 1}")
            return client
        except Exception as e:
            print(f"✗ Key #{current_key_index + 1} failed: {str(e)[:50]}")
            current_key_index = (current_key_index + 1) % len(API_KEYS)
    
    return None

def rotate_key():
    """Move to next API key"""
    global current_key_index
    current_key_index = (current_key_index + 1) % len(API_KEYS)
    print(f"🔄 Rotating to API key #{current_key_index + 1}")

# Initialize client
try:
    client = get_client()
except Exception as e:
    print(f"Warning: Could not initialize GenAI client: {e}")
    client = None

def generate_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Generate adaptive quiz questions for ANY topic or subtopic using NEW Google GenAI SDK.
    Auto-rotates API keys if quota exceeded.
    Returns:
        questions (list), difficulty (str)
    """
    
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""

    # Determine approximate difficulty
    difficulty = "intermediate"
    for r in user_scores:
        if r["topic"] == topic and r["subtopic"] == subtopic:
            percent = (r["score"] / max(1, r["total_questions"])) * 100
            if percent < 40:
                difficulty = "beginner"
            elif percent >= 80:
                difficulty = "advanced"
            else:
                difficulty = "intermediate"
            break

    # Build prompt
    prompt_text = f"""Generate {num_questions} multiple choice questions.

Topic: {topic}
Subtopic: {subtopic if subtopic else 'General'}
Difficulty: {difficulty}

Return ONLY valid JSON (no markdown, no extra text) in this exact format:
[
  {{
    "q": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A"
  }}
]

CRITICAL RULES:
1. "answer" must be the EXACT text of the correct option (not A, B, C, D)
2. Each question must have exactly 4 options
3. Questions must be relevant to {topic} {subtopic}
4. Return ONLY the JSON array, nothing else"""

    # Try with current key, rotate if needed
    max_retries = len(API_KEYS)
    
    for retry in range(max_retries):
        try:
            current_client = get_client() if not client else client
            
            if not current_client:
                raise Exception("No working API keys available")
            
            # Use NEW API syntax
            response = current_client.models.generate_content(
                model='gemini-2.0-flash-exp',  # Using stable model
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.7
                )
            )

            raw = response.text.strip()
            
            # Clean response
            if '```json' in raw:
                raw = raw.split('```json')[1].split('```')[0].strip()
            elif '```' in raw:
                raw = raw.split('```')[1].split('```')[0].strip()
            
            data = json.loads(raw)
            
            if isinstance(data, list) and len(data) > 0:
                # Validate structure
                for item in data:
                    if 'q' not in item or 'options' not in item or 'answer' not in item:
                        raise ValueError("Invalid question structure")
                    if len(item['options']) != 4:
                        raise ValueError("Each question must have 4 options")
                
                print(f"✅ Generated {len(data)} {difficulty} questions for {topic} {subtopic}")
                return data, difficulty

        except Exception as e:
            error_str = str(e)
            
            # Check if quota exceeded
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                print(f"⚠️ Quota exceeded on key #{current_key_index + 1}")
                rotate_key()
                
                # If this was last retry, fall through to fallback
                if retry < max_retries - 1:
                    continue
            else:
                print(f"[AI ERROR] Generation failed: {e}")
                import traceback
                traceback.print_exc()
            
            # If not quota error or last retry, break
            break

    # Fallback questions
    print(f"⚠️ Using fallback questions for {topic} {subtopic}")
    fallback = [{
        "q": f"What is a key concept in {topic} {subtopic}?",
        "options": ["Concept A", "Concept B", "Concept C", "Concept D"],
        "answer": "Concept A"
    } for _ in range(num_questions)]

    return fallback, difficulty


def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Wrapper function that returns questions in app.py expected format.
    Returns: dict with 'questions' and 'difficulty'
    """
    questions, difficulty = generate_questions(user_email, topic, subtopic, user_scores, num_questions)
    
    return {
        'questions': questions,
        'difficulty': difficulty
    }


def generate_quiz_questions(topic, context, difficulty, num_questions=5):
    """
    Generate quiz questions for Grand Test (no user history needed).
    """
    prompt_text = f"""Generate {num_questions} multiple choice questions.

Topic: {topic}
Context: {context}
Difficulty: {difficulty}

Return ONLY valid JSON (no markdown) in this format:
[
  {{
    "q": "Question text?",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Make questions relevant to {topic} and {context}."""

    max_retries = len(API_KEYS)
    
    for retry in range(max_retries):
        try:
            current_client = get_client() if not client else client
            
            if not current_client:
                raise Exception("No working API keys")
            
            response = current_client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.7
                )
            )

            raw = response.text.strip()
            
            if '```json' in raw:
                raw = raw.split('```json')[1].split('```')[0].strip()
            elif '```' in raw:
                raw = raw.split('```')[1].split('```')[0].strip()
            
            data = json.loads(raw)
            
            if isinstance(data, list):
                return data

        except Exception as e:
            error_str = str(e)
            
            if '429' in error_str or 'RESOURCE_EXHAUSTED' in error_str or 'quota' in error_str.lower():
                print(f"⚠️ Quota exceeded on key #{current_key_index + 1}")
                rotate_key()
                if retry < max_retries - 1:
                    continue
            else:
                print(f"[ERROR] Grand Test generation failed: {e}")
            
            break

    # Fallback
    return [{
        "q": f"Basic question about {topic}?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "Option A"
    } for _ in range(num_questions)]


def determine_difficulty_level(user_scores, topic, subtopic):
    """
    Determine difficulty level based on past performance.
    """
    if not user_scores:
        return "intermediate"
    
    relevant_scores = [
        s for s in user_scores 
        if s['topic'] == topic and (not subtopic or s.get('subtopic') == subtopic)
    ]
    
    if not relevant_scores:
        return "intermediate"
    
    total_score = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    
    if total_questions == 0:
        return "intermediate"
    
    percent = (total_score / total_questions) * 100
    
    if percent < 40:
        return "beginner"
    elif percent >= 75:
        return "advanced"
    else:
        return "intermediate"