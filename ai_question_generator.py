# ai_question_generator.py - FIXED VERSION

import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# Get API key from environment
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Create client (NEW API)
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"Warning: Could not initialize GenAI client: {e}")
    client = None

def generate_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Generate adaptive quiz questions for ANY topic or subtopic using NEW Google GenAI SDK.
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

    try:
        if not client:
            raise Exception("GenAI client not initialized")
        
        # Use NEW API syntax
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
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
        print(f"[AI ERROR] Generation failed: {e}")
        import traceback
        traceback.print_exc()

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

    try:
        if not client:
            raise Exception("GenAI client not initialized")
        
        response = client.models.generate_content(
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
        print(f"[ERROR] Grand Test generation failed: {e}")

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