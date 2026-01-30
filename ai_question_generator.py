# ai_question_generator.py - FIXED VERSION WITH IMPROVED JSON HANDLING

import os
import json
from dotenv import load_dotenv
import random
import time
from datetime import datetime, timedelta

load_dotenv()

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️  Install: pip install google-generativeai python-dotenv")

# ============================================================================
# SMART API KEY ROTATION WITH QUOTA TRACKING
# ============================================================================
API_KEYS = []
for i in range(1, 10):
    key = os.getenv(f"GEMINI_API_KEY_{i}")
    if key and key.strip():
        API_KEYS.append(key.strip())

print(f"✅ Loaded {len(API_KEYS)} API keys")

key_usage = {i: {'calls': 0, 'reset_time': datetime.now(), 'failed': False} for i in range(len(API_KEYS))}
current_key_index = 0
MAX_CALLS_PER_MINUTE = 20
QUOTA_RESET_SECONDS = 65

question_cache = {}
MAX_CACHE_SIZE = 100

if GENAI_AVAILABLE and API_KEYS:
    try:
        genai.configure(api_key=API_KEYS[0])
        print(f"✅ GenAI configured with {len(API_KEYS)} API key(s)")
    except Exception as e:
        print(f"⚠️  Config failed: {e}")
        GENAI_AVAILABLE = False

# ============================================================================
# COMPREHENSIVE FALLBACK QUESTIONS
# ============================================================================
FALLBACK_QUESTIONS = {
    'C': {
        'Arrays': [
            {"q": "What is the output of: int arr[5]={1,2}; printf(\"%d\", arr[3]);", 
             "options": ["0", "Garbage value", "3", "Compilation error"], 
             "answer": "0"},
            {"q": "Which correctly accesses the third element of array int a[10];?", 
             "options": ["a[2]", "a[3]", "*(a+3)", "Both a[2] and *(a+2)"], 
             "answer": "Both a[2] and *(a+2)"},
            {"q": "What does sizeof(arr)/sizeof(arr[0]) calculate for int arr[]={1,2,3,4,5};?", 
             "options": ["Number of elements", "Array size in bytes", "First element value", "Pointer size"], 
             "answer": "Number of elements"},
            {"q": "What happens: char str[5]=\"Hello\"; printf(\"%s\", str);?", 
             "options": ["Buffer overflow", "Prints Hello", "Compilation error", "Undefined behavior"], 
             "answer": "Buffer overflow"},
            {"q": "Which is valid 2D array declaration?", 
             "options": ["int arr[3][4];", "int arr[][];", "int arr[3][];", "int [][]arr;"], 
             "answer": "int arr[3][4];"}
        ],
        'Pointers': [
            {"q": "What is the output: int x=10; int *p=&x; printf(\"%d\", *p);", 
             "options": ["10", "Address of x", "0", "Garbage"], 
             "answer": "10"},
            {"q": "What does int *p; *p=10; cause?", 
             "options": ["Segmentation fault", "Assigns 10 to random location", "Compilation error", "Creates variable p"], 
             "answer": "Segmentation fault"},
        ],
    },
    'Java': {
        'OOPs': [
            {"q": "What is runtime polymorphism demonstrated by: Parent p = new Child(); p.display();?", 
             "options": ["Method overriding", "Method overloading", "Encapsulation", "Abstraction"], 
             "answer": "Method overriding"},
        ],
    },
    'Python': {
        'Lists': [
            {"q": "What is the output of: L=[1,2,3]; print(L[::-1])?", 
             "options": ["[3, 2, 1]", "[1, 2, 3]", "Error", "None"], 
             "answer": "[3, 2, 1]"},
        ],
    },
}

GENERIC_FALLBACK = [
    {"q": "What is a fundamental principle in solving placement test questions?", 
     "options": ["Understand the core concept, not just memorize", "Guess randomly", "Skip difficult ones", "Only practice easy questions"], 
     "answer": "Understand the core concept, not just memorize"}
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_fallback_questions(topic, subtopic, num_questions=20):
    """Get fallback questions when AI generation fails"""
    questions = []
    
    if topic in FALLBACK_QUESTIONS:
        if isinstance(FALLBACK_QUESTIONS[topic], dict) and subtopic in FALLBACK_QUESTIONS[topic]:
            pool = FALLBACK_QUESTIONS[topic][subtopic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
        elif isinstance(FALLBACK_QUESTIONS[topic], list):
            pool = FALLBACK_QUESTIONS[topic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
    
    while len(questions) < num_questions:
        default_pool = GENERIC_FALLBACK[:]
        random.shuffle(default_pool)
        questions.extend(default_pool[:num_questions - len(questions)])
    
    for q in questions:
        opts = q['options'][:]
        random.shuffle(opts)
        q['options'] = opts
    
    return questions[:num_questions]

def determine_difficulty_level(user_scores, topic, subtopic):
    """Adaptive difficulty based on user performance"""
    if not user_scores:
        return "beginner"
    
    relevant_scores = [
        s for s in user_scores 
        if s['topic'] == topic and (not subtopic or s.get('subtopic', '') == subtopic)
    ]
    
    if not relevant_scores:
        return "beginner"
    
    total_score = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    attempt_count = len(relevant_scores)
    
    if total_questions == 0:
        return "beginner"
    
    percent = (total_score / total_questions) * 100
    
    print(f"   📊 Performance: {percent:.1f}% overall | {attempt_count} attempts")
    
    if percent < 40:
        return "beginner"
    elif 40 <= percent < 70:
        return "intermediate" if attempt_count >= 2 else "beginner"
    elif 70 <= percent < 85:
        return "advanced" if attempt_count >= 3 else "intermediate"
    else:
        return "advanced"

# ============================================================================
# IMPROVED JSON CLEANING FUNCTION
# ============================================================================
def aggressive_json_clean(raw_text):
    """Ultra-aggressive JSON cleaning for Gemini responses"""
    import re
    
    # Remove markdown code blocks
    if '```json' in raw_text:
        raw_text = raw_text.split('```json')[1].split('```')[0].strip()
    elif '```' in raw_text:
        raw_text = raw_text.split('```')[1].split('```')[0].strip()
    
    # Extract JSON array if present
    if '[' in raw_text and ']' in raw_text:
        start = raw_text.find('[')
        end = raw_text.rfind(']') + 1
        raw_text = raw_text[start:end]
    
    # Remove control characters and normalize
    raw_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_text)
    raw_text = raw_text.replace('"', '"').replace('"', '"')
    raw_text = raw_text.replace("'", "'").replace('`', "'")
    
    # Fix common issues
    raw_text = raw_text.replace('}\n{', '},{')  # Missing commas between objects
    raw_text = raw_text.replace('} {', '},{')
    raw_text = re.sub(r',\s*}', '}', raw_text)  # Trailing commas
    raw_text = re.sub(r',\s*]', ']', raw_text)
    
    return raw_text

def extract_questions_from_broken_json(raw_text):
    """Extract valid question objects from broken JSON"""
    import re
    
    # Ultra-flexible pattern to match question objects
    pattern = r'\{\s*"q"\s*:\s*"[^"]+"\s*,\s*"options"\s*:\s*\[[^\]]+\]\s*,\s*"answer"\s*:\s*"[^"]+"\s*\}'
    matches = re.findall(pattern, raw_text, re.DOTALL)
    
    valid_questions = []
    for match in matches:
        try:
            obj = json.loads(match)
            if all(k in obj for k in ['q', 'options', 'answer']) and len(obj['options']) == 4:
                valid_questions.append(obj)
        except:
            continue
    
    return valid_questions

# ============================================================================
# AI GENERATION WITH ULTRA-STRICT PROMPTING
# ============================================================================
def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=20, progress_callback=None):
    """Generate questions with STRICT JSON validation"""
    global current_key_index, key_usage, question_cache
    
    if not GENAI_AVAILABLE or not API_KEYS:
        return None
    
    if progress_callback:
        progress_callback(10, f"Starting AI generation for {topic}...")
    
    try:
        print(f"🤖 AI Generation: {topic}/{subtopic} ({difficulty})...")
        
        # Try best models first
        models_to_try = [
            'gemini-2.0-flash-001',
            'gemini-flash-latest',
            'gemini-pro-latest',
        ]
        random.shuffle(models_to_try)
        
        difficulty_guidelines = {
            'beginner': "Focus on basic concepts and definitions. 70 percent accuracy expected.",
            'intermediate': "Multi-step problems requiring analysis. 50 percent accuracy expected.",
            'advanced': "Complex scenarios, edge cases, optimization. 30 percent accuracy expected."
        }
        
        for idx, model_name in enumerate(models_to_try):
            if progress_callback:
                progress = 20 + (idx * 60 // len(models_to_try))
                progress_callback(progress, f"Trying model {idx+1}/{len(models_to_try)}...")
            
            key_idx = random.randint(0, len(API_KEYS) - 1)
    
            try:
                genai.configure(api_key=API_KEYS[key_idx])
                print(f"   🔑 Key {key_idx + 1}/{len(API_KEYS)} | Model: {model_name[:30]}")
                
                model = genai.GenerativeModel(model_name)
                
                # ULTRA-STRICT PROMPT - NO SPECIAL CHARACTERS IN QUESTIONS
                prompt = f"""Generate {num_questions} multiple-choice questions for BTech students.

TOPIC: {topic}
SUBTOPIC: {subtopic if subtopic else 'General'}
DIFFICULTY: {difficulty.upper()}

CRITICAL RULES FOR VALID JSON:
1. NO special characters in questions: NO percent signs, NO dollar signs, NO backslashes
2. Replace "%" with "percent", "$" with "dollars", etc.
3. NO line breaks inside strings
4. Questions must be plain text only
5. Each answer MUST exactly match one option

EXAMPLE FORMAT:
[
  {{"q": "If x equals 50 and y equals 25, what is x plus y?", "options": ["75", "50", "25", "100"], "answer": "75"}},
  {{"q": "What is 20 percent of 100?", "options": ["20", "10", "30", "50"], "answer": "20"}}
]

REQUIREMENTS:
- Exactly {num_questions} questions
- Each question 20+ characters
- Exactly 4 options per question
- Answer must EXACTLY match one option
- NO code examples with special chars
- ONLY return valid JSON array

Generate now:"""

                key_usage[key_idx]['calls'] += 1
                
                if progress_callback:
                    progress_callback(progress + 10, "Generating questions...")
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,  # Lower temperature for more predictable output
                        max_output_tokens=4096,
                        top_p=0.9,
                        top_k=40
                    ),
                    request_options={'timeout': 30}
                )
                
                if progress_callback:
                    progress_callback(85, "Processing response...")
                
                raw = response.text.strip()
                
                # AGGRESSIVE CLEANING
                raw = aggressive_json_clean(raw)
                
                # Try parsing
                data = None
                try:
                    data = json.loads(raw)
                    print(f"   ✅ Successfully parsed JSON")
                except json.JSONDecodeError as e:
                    print(f"   ⚠️ JSON parse failed: {str(e)[:80]}")
                    
                    # FALLBACK: Extract valid questions from broken JSON
                    extracted = extract_questions_from_broken_json(raw)
                    if extracted:
                        data = extracted
                        print(f"   ✅ Extracted {len(data)} questions from broken JSON")
                
                if not data:
                    print(f"   ❌ No valid JSON found")
                    continue
                
                # Validate questions with STRICT checks
                if isinstance(data, list) and len(data) > 0:
                    valid = []
                    for item in data:
                        if not all(k in item for k in ['q', 'options', 'answer']):
                            continue
                        
                        if not isinstance(item['options'], list) or len(item['options']) != 4:
                            continue
                        
                        # Normalize answer matching
                        answer = str(item['answer']).strip()
                        options = [str(opt).strip() for opt in item['options']]
                        
                        answer_lower = answer.lower()
                        if not any(answer_lower == opt.lower() for opt in options):
                            # Try to fix
                            for opt in options:
                                if answer_lower in opt.lower() or opt.lower() in answer_lower:
                                    item['answer'] = opt
                                    break
                            else:
                                print(f"   ⚠️ Skipping question with invalid answer: '{answer}'")
                                continue
                        else:
                            for opt in options:
                                if answer_lower == opt.lower():
                                    item['answer'] = opt
                                    break
                        
                        if len(item['q']) < 20:
                            continue
                        
                        valid.append(item)
                    
                    # Success if we got at least 60% of requested questions
                    if len(valid) >= num_questions * 0.6:
                        result = valid[:num_questions]
                        
                        if progress_callback:
                            progress_callback(100, "Questions generated successfully!")
                        
                        print(f"✅ Generated {len(result)} questions using {model_name}")
                        return result
                    else:
                        print(f"⚠️  Only {len(valid)}/{num_questions} valid questions, trying next model...")
                
            except Exception as model_error:
                error_msg = str(model_error)
                
                if '429' in error_msg or 'quota' in error_msg.lower() or 'Resource has been exhausted' in error_msg:
                    print(f"⚠️  Key {key_idx + 1} quota exhausted")
                    key_usage[key_idx]['calls'] = MAX_CALLS_PER_MINUTE
                    continue
                elif 'API key not valid' in error_msg or '400' in error_msg:
                    print(f"❌ Key {key_idx + 1} invalid")
                    key_usage[key_idx]['failed'] = True
                    continue
                else:
                    print(f"⚠️  {model_name} error: {error_msg[:80]}")
                    continue
        
        if progress_callback:
            progress_callback(0, "AI generation failed, using fallback...")
        
        print(f"❌ All AI generation attempts failed")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)[:100]}")
        return None

# ============================================================================
# PUBLIC API
# ============================================================================
def generate_questions(user_email, topic, subtopic, user_scores, num_questions=20, progress_callback=None):
    """Main entry point for question generation"""
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    difficulty = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 QUESTION GENERATION REQUEST")
    print(f"   Topic: {topic} / {subtopic if subtopic else 'General'}")
    print(f"   Difficulty: {difficulty.upper()}")
    print(f"   Count: {num_questions}")
    print(f"{'='*80}")
    
    # Try AI generation first
    ai_questions = generate_questions_with_ai(topic, subtopic, difficulty, num_questions, progress_callback)
    
    if ai_questions and len(ai_questions) >= num_questions:
        print(f"✅ Successfully generated {len(ai_questions)} AI questions")
        return ai_questions[:num_questions], difficulty
    
    # Fallback to static questions
    if progress_callback:
        progress_callback(50, "Using fallback questions...")
    
    print(f"📚 Using fallback questions")
    fallback = get_fallback_questions(topic, subtopic, num_questions)
    
    if progress_callback:
        progress_callback(100, "Questions ready!")
    
    print(f"✅ Loaded {len(fallback)} fallback questions")
    
    return fallback, difficulty

def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=20):
    """Wrapper for backward compatibility"""
    questions, difficulty = generate_questions(user_email, topic, subtopic, user_scores, num_questions)
    return {
        'questions': questions,
        'difficulty': difficulty
    }

def generate_quiz_questions(topic, context, difficulty, num_questions=0):
    """For grand test / general quiz generation without user history"""
    print(f"\n🎓 QUIZ GENERATION: {topic} ({difficulty}) - {num_questions} questions")
    
    ai_q = generate_questions_with_ai(topic, '', difficulty, num_questions)
    if ai_q and len(ai_q) >= num_questions:
        return ai_q
    
    print(f"📚 Using fallback for quiz")
    return get_fallback_questions(topic, '', num_questions)

# ============================================================================
# STARTUP DIAGNOSTICS
# ============================================================================
def print_startup_info():
    """Print configuration info on module load"""
    print("\n" + "="*80)
    print("🎓 CAREERLENS AI QUESTION GENERATOR - FIXED v4.0")
    print("="*80)
    
    if GENAI_AVAILABLE and API_KEYS:
        print(f"✅ AI Mode: ACTIVE")
        print(f"   - API Keys: {len(API_KEYS)} configured")
        print(f"   - Features: Improved JSON parsing, Stricter prompts")
    else:
        print("📚 Fallback Mode: ACTIVE (using static questions)")
    
    print("="*80 + "\n")

print_startup_info()