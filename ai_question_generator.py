# ai_question_generator.py - IMPROVED VERSION WITH ASYNC GENERATION

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
# API KEY MANAGEMENT
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
# FALLBACK QUESTIONS (Enhanced)
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
    'Technical': [
        {"q": "What is time complexity of binary search?", 
         "options": ["O(n)", "O(log n)", "O(n log n)", "O(1)"], 
         "answer": "O(log n)"},
        {"q": "Which data structure uses LIFO principle?", 
         "options": ["Queue", "Stack", "Tree", "Graph"], 
         "answer": "Stack"},
    ],
    'Quantitative Aptitude': [
        {"q": "If 20% of x is 40, what is 50% of x?", 
         "options": ["100", "80", "120", "200"], 
         "answer": "100"},
        {"q": "A train travels 120 km in 2 hours. What is its speed in km/h?", 
         "options": ["60", "50", "70", "80"], 
         "answer": "60"},
    ],
    'Grammar': [
        {"q": "Choose the correct sentence:", 
         "options": ["She don't like apples", "She doesn't like apples", "She not like apples", "She didn't likes apples"], 
         "answer": "She doesn't like apples"},
    ],
}

GENERIC_FALLBACK = [
    {"q": "What is a fundamental principle in solving placement test questions?", 
     "options": ["Understand the core concept, not just memorize", "Guess randomly", "Skip difficult ones", "Only practice easy questions"], 
     "answer": "Understand the core concept, not just memorize"}
]

# ============================================================================
# PROGRESS TRACKING FOR UI FEEDBACK
# ============================================================================
class ProgressTracker:
    """Track question generation progress for UI updates"""
    
    def __init__(self, callback=None):
        self.callback = callback
        self.current_step = 0
        self.total_steps = 4
        self.messages = []
    
    def update(self, step, message):
        """Update progress"""
        self.current_step = step
        self.messages.append(message)
        progress = int((step / self.total_steps) * 100)
        
        if self.callback:
            self.callback(progress, message)
        
        print(f"[{progress}%] {message}")
    
    def complete(self):
        """Mark as complete"""
        if self.callback:
            self.callback(100, "Questions ready!")

# ============================================================================
# PERFORMANCE ANALYSIS
# ============================================================================
def analyze_performance_history(user_scores, topic, subtopic):
    """
    Analyze user's performance history to determine optimal difficulty
    Returns: dict with analysis results
    """
    if not user_scores:
        return {
            'difficulty': 'intermediate',
            'avg_score': 0,
            'attempts': 0,
            'trend': 'new',
            'weak_areas': [],
            'strong_areas': []
        }
    
    # Filter relevant scores
    relevant = [
        s for s in user_scores 
        if s['topic'] == topic and (not subtopic or s.get('subtopic') == subtopic)
    ]
    
    if not relevant:
        return {
            'difficulty': 'intermediate',
            'avg_score': 0,
            'attempts': 0,
            'trend': 'new',
            'weak_areas': [],
            'strong_areas': []
        }
    
    # Calculate statistics
    total_score = sum(s['score'] for s in relevant)
    total_q = sum(s['total_questions'] for s in relevant)
    avg_percent = (total_score / total_q * 100) if total_q > 0 else 0
    attempts = len(relevant)
    
    # Determine trend
    if attempts >= 3:
        recent_scores = [s['score'] / s['total_questions'] * 100 for s in relevant[-3:]]
        older_scores = [s['score'] / s['total_questions'] * 100 for s in relevant[:-3]]
        
        if older_scores:
            recent_avg = sum(recent_scores) / len(recent_scores)
            older_avg = sum(older_scores) / len(older_scores)
            
            if recent_avg > older_avg + 10:
                trend = 'improving'
            elif recent_avg < older_avg - 10:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'new'
    else:
        trend = 'new'
    
    # Determine difficulty
    if avg_percent < 40:
        difficulty = 'beginner'
    elif avg_percent < 70:
        difficulty = 'intermediate' if attempts >= 2 else 'beginner'
    elif avg_percent < 85:
        difficulty = 'advanced' if attempts >= 3 else 'intermediate'
    else:
        difficulty = 'advanced'
    
    return {
        'difficulty': difficulty,
        'avg_score': round(avg_percent, 1),
        'attempts': attempts,
        'trend': trend,
        'weak_areas': [],
        'strong_areas': []
    }

# ============================================================================
# IMPROVED JSON HANDLING
# ============================================================================
def aggressive_json_clean(raw_text):
    """Ultra-aggressive JSON cleaning"""
    import re
    
    if '```json' in raw_text:
        raw_text = raw_text.split('```json')[1].split('```')[0].strip()
    elif '```' in raw_text:
        raw_text = raw_text.split('```')[1].split('```')[0].strip()
    
    if '[' in raw_text and ']' in raw_text:
        start = raw_text.find('[')
        end = raw_text.rfind(']') + 1
        raw_text = raw_text[start:end]
    
    raw_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_text)
    raw_text = raw_text.replace('"', '"').replace('"', '"')
    raw_text = raw_text.replace("'", "'").replace('`', "'")
    raw_text = raw_text.replace('}\n{', '},{')
    raw_text = raw_text.replace('} {', '},{')
    raw_text = re.sub(r',\s*}', '}', raw_text)
    raw_text = re.sub(r',\s*]', ']', raw_text)
    
    return raw_text

def extract_questions_from_broken_json(raw_text):
    """Extract valid question objects from broken JSON"""
    import re
    
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
# AI QUESTION GENERATION WITH PROGRESS TRACKING
# ============================================================================
def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=20, progress_callback=None):
    """Generate questions with progress tracking"""
    global current_key_index, key_usage
    
    if not GENAI_AVAILABLE or not API_KEYS:
        return None
    
    tracker = ProgressTracker(progress_callback)
    
    try:
        tracker.update(1, f"📊 Analyzing {topic} performance...")
        time.sleep(0.3)  # Brief pause for UI update
        
        # Try models
        models_to_try = [
            'gemini-2.0-flash-exp',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
        ]
        
        difficulty_guidelines = {
            'beginner': "Focus on basic concepts and definitions. 70% accuracy expected.",
            'intermediate': "Multi-step problems requiring analysis. 50% accuracy expected.",
            'advanced': "Complex scenarios, edge cases, optimization. 30% accuracy expected."
        }
        
        tracker.update(2, f"🎯 Setting difficulty: {difficulty.upper()}")
        time.sleep(0.3)
        
        for idx, model_name in enumerate(models_to_try):
            tracker.update(3, f"🤖 Generating questions (attempt {idx+1}/{len(models_to_try)})...")
            
            key_idx = random.randint(0, len(API_KEYS) - 1)
            
            try:
                genai.configure(api_key=API_KEYS[key_idx])
                model = genai.GenerativeModel(model_name)
                
                prompt = f"""Generate {num_questions} multiple-choice questions for BTech placement preparation.

TOPIC: {topic}
SUBTOPIC: {subtopic if subtopic else 'General'}
DIFFICULTY: {difficulty.upper()} - {difficulty_guidelines[difficulty]}

CRITICAL JSON RULES:
1. NO special characters in questions (%, $, \\)
2. Replace special chars: "%" → "percent", "$" → "dollars"
3. NO line breaks inside strings
4. Answer MUST exactly match one option (case-sensitive)

FORMAT:
[
  {{"q": "What is 20 percent of 100?", "options": ["20", "10", "30", "50"], "answer": "20"}},
  {{"q": "Which data structure uses LIFO?", "options": ["Queue", "Stack", "Tree", "Graph"], "answer": "Stack"}}
]

Generate EXACTLY {num_questions} questions. ONLY return valid JSON array."""

                key_usage[key_idx]['calls'] += 1
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=4096,
                        top_p=0.9,
                        top_k=40
                    ),
                    request_options={'timeout': 30}
                )
                
                tracker.update(4, "✨ Processing questions...")
                
                raw = response.text.strip()
                raw = aggressive_json_clean(raw)
                
                data = None
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                    extracted = extract_questions_from_broken_json(raw)
                    if extracted:
                        data = extracted
                
                if not data:
                    continue
                
                # Validate questions
                if isinstance(data, list) and len(data) > 0:
                    valid = []
                    for item in data:
                        if not all(k in item for k in ['q', 'options', 'answer']):
                            continue
                        
                        if not isinstance(item['options'], list) or len(item['options']) != 4:
                            continue
                        
                        # Normalize answer
                        answer = str(item['answer']).strip()
                        options = [str(opt).strip() for opt in item['options']]
                        
                        answer_lower = answer.lower()
                        if not any(answer_lower == opt.lower() for opt in options):
                            for opt in options:
                                if answer_lower in opt.lower() or opt.lower() in answer_lower:
                                    item['answer'] = opt
                                    break
                            else:
                                continue
                        else:
                            for opt in options:
                                if answer_lower == opt.lower():
                                    item['answer'] = opt
                                    break
                        
                        if len(item['q']) < 20:
                            continue
                        
                        valid.append(item)
                    
                    if len(valid) >= num_questions * 0.6:
                        result = valid[:num_questions]
                        tracker.complete()
                        print(f"✅ Generated {len(result)} questions using {model_name}")
                        return result
                
            except Exception as model_error:
                error_msg = str(model_error)
                
                if '429' in error_msg or 'quota' in error_msg.lower():
                    print(f"⚠️  Key {key_idx + 1} quota exhausted")
                    key_usage[key_idx]['calls'] = MAX_CALLS_PER_MINUTE
                    continue
                elif 'API key not valid' in error_msg or '400' in error_msg:
                    print(f"❌ Key {key_idx + 1} invalid")
                    key_usage[key_idx]['failed'] = True
                    continue
                else:
                    continue
        
        print(f"❌ All AI attempts failed")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)[:100]}")
        return None

# ============================================================================
# FALLBACK QUESTION RETRIEVAL
# ============================================================================
def get_fallback_questions(topic, subtopic, num_questions=20):
    """Get fallback questions when AI fails"""
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

# ============================================================================
# PUBLIC API
# ============================================================================
def generate_questions(user_email, topic, subtopic, user_scores, num_questions=20, progress_callback=None):
    """Main entry point - with performance analysis first"""
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    
    # Step 1: Analyze performance (fast)
    analysis = analyze_performance_history(user_scores, topic, subtopic)
    difficulty = analysis['difficulty']
    
    if progress_callback:
        progress_callback(25, f"📊 Performance: {analysis['avg_score']}% • Difficulty: {difficulty}")
    
    print(f"\n{'='*80}")
    print(f"🎯 QUESTION GENERATION")
    print(f"   Topic: {topic} / {subtopic if subtopic else 'General'}")
    print(f"   Performance: {analysis['avg_score']}% ({analysis['attempts']} attempts)")
    print(f"   Difficulty: {difficulty.upper()}")
    print(f"   Trend: {analysis['trend']}")
    print(f"{'='*80}")
    
    # Step 2: Try AI generation
    ai_questions = generate_questions_with_ai(topic, subtopic, difficulty, num_questions, progress_callback)
    
    if ai_questions and len(ai_questions) >= num_questions:
        print(f"✅ AI generation successful: {len(ai_questions)} questions")
        return ai_questions[:num_questions], difficulty
    
    # Step 3: Fallback
    if progress_callback:
        progress_callback(75, "Using fallback questions...")
    
    print(f"📚 Using fallback questions")
    fallback = get_fallback_questions(topic, subtopic, num_questions)
    
    if progress_callback:
        progress_callback(100, "Questions ready!")
    
    return fallback, difficulty

def determine_difficulty_level(user_scores, topic, subtopic):
    """Quick difficulty determination (for backward compatibility)"""
    analysis = analyze_performance_history(user_scores, topic, subtopic)
    return analysis['difficulty']

# ============================================================================
# STARTUP INFO
# ============================================================================
def print_startup_info():
    print("\n" + "="*80)
    print("🎓 CAREERLENS AI QUESTION GENERATOR v5.0 - ASYNC READY")
    print("="*80)
    
    if GENAI_AVAILABLE and API_KEYS:
        print(f"✅ AI Mode: ACTIVE")
        print(f"   - API Keys: {len(API_KEYS)}")
        print(f"   - Features: Progress tracking, Performance analysis")
    else:
        print("📚 Fallback Mode: ACTIVE")
    
    print("="*80 + "\n")

print_startup_info()