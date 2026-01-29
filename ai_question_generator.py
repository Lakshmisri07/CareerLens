# ai_question_generator.py - WORKING VERSION with google-generativeai

import os
import json
from dotenv import load_dotenv
import random

load_dotenv()

# Use the CORRECT Google Generative AI SDK
try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️  Install: pip install google-generativeai")

# ============================================================================
# API KEY SETUP
# ============================================================================
API_KEYS = []
for i in range(1, 5):
    key = os.getenv(f"GEMINI_API_KEY_{i}") or (os.getenv("GEMINI_API_KEY") if i == 1 else None)
    if key:
        API_KEYS.append(key)

current_key_index = 0

# Configure GenAI with first key
if GENAI_AVAILABLE and API_KEYS:
    try:
        genai.configure(api_key=API_KEYS[0])
        print(f"✅ GenAI configured with {len(API_KEYS)} API key(s)")
    except Exception as e:
        print(f"⚠️  GenAI config failed: {e}")
        GENAI_AVAILABLE = False

# ============================================================================
# FALLBACK QUESTIONS (Keep your existing ones)
# ============================================================================
FALLBACK_QUESTIONS = {
    'C': {
        'Arrays': [
            {"q": "What is the correct way to declare an array of 10 integers in C?", 
             "options": ["int arr[10];", "int arr(10);", "array int[10];", "int[10] arr;"], 
             "answer": "int arr[10];"},
            {"q": "What is the index of the first element in a C array?", 
             "options": ["0", "1", "-1", "Depends on declaration"], 
             "answer": "0"},
            {"q": "Which function is used to find the length of an array in C?", 
             "options": ["sizeof()", "length()", "size()", "count()"], 
             "answer": "sizeof()"},
            {"q": "What happens when you access an array element beyond its size?", 
             "options": ["Undefined behavior", "Compilation error", "Returns 0", "Automatic resizing"], 
             "answer": "Undefined behavior"},
            {"q": "How do you initialize an array with all zeros in C?", 
             "options": ["int arr[5] = {0};", "int arr[5] = 0;", "int arr[5] = {};", "int arr[5];"], 
             "answer": "int arr[5] = {0};"}
        ],
        'Pointers': [
            {"q": "What does the * operator do in pointer declaration?", 
             "options": ["Declares a pointer", "Dereferences a pointer", "Gets address", "Multiplies values"], 
             "answer": "Declares a pointer"},
            {"q": "What does the & operator return?", 
             "options": ["Address of variable", "Value of variable", "Pointer to pointer", "Reference"], 
             "answer": "Address of variable"},
            {"q": "What is a NULL pointer?", 
             "options": ["Pointer pointing to nothing", "Pointer to zero", "Invalid pointer", "Deleted pointer"], 
             "answer": "Pointer pointing to nothing"},
            {"q": "What is pointer arithmetic?", 
             "options": ["Moving pointer by data type size", "Adding pointers", "Multiplying addresses", "None"], 
             "answer": "Moving pointer by data type size"},
            {"q": "What is a dangling pointer?", 
             "options": ["Pointer to freed memory", "NULL pointer", "Uninitialized pointer", "Valid pointer"], 
             "answer": "Pointer to freed memory"}
        ]
    },
    'Java': {
        'OOPs': [
            {"q": "What are the four pillars of OOP?", 
             "options": ["Encapsulation, Inheritance, Polymorphism, Abstraction", "Classes, Objects, Methods, Variables", "Public, Private, Protected, Default", "None"], 
             "answer": "Encapsulation, Inheritance, Polymorphism, Abstraction"},
        ]
    },
    'Python': {
        'Lists': [
            {"q": "How do you create an empty list?", 
             "options": ["[]", "{}", "()", "list"], 
             "answer": "[]"},
            {"q": "What method adds an element to the end of a list?", 
             "options": ["append()", "add()", "insert()", "extend()"], 
             "answer": "append()"},
        ]
    }
}

GENERIC_FALLBACK = [
    {"q": "What is a key concept in this topic?", 
     "options": ["Understanding core principles", "Memorizing facts", "Ignoring details", "Guessing answers"], 
     "answer": "Understanding core principles"},
]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_fallback_questions(topic, subtopic, num_questions=5):
    """Get randomized fallback questions"""
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
    
    if len(questions) < num_questions:
        default_pool = GENERIC_FALLBACK[:]
        random.shuffle(default_pool)
        questions.extend(default_pool[:num_questions - len(questions)])
    
    for q in questions:
        opts = q['options'][:]
        random.shuffle(opts)
        q['options'] = opts
    
    return questions[:num_questions]


def determine_difficulty_level(user_scores, topic, subtopic):
    """Determine difficulty based on performance"""
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

# ============================================================================
# AI GENERATION (CORRECT SDK)
# ============================================================================

def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=5):
    """Generate questions using Gemini with CORRECT SDK"""
    if not GENAI_AVAILABLE:
        return None
    
    try:
        print(f"🤖 AI Generation: {topic}/{subtopic} ({difficulty})...")
        
        # Create the model
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Craft prompt
        prompt = f"""Generate EXACTLY {num_questions} multiple choice questions for technical interview preparation.

Topic: {topic}
Subtopic: {subtopic if subtopic else 'General'}
Difficulty: {difficulty}

RULES:
1. Return ONLY valid JSON array - no markdown, no explanations
2. Each question has EXACTLY 4 options
3. "answer" must be EXACT text of correct option (not A/B/C/D)
4. Difficulty meanings:
   - beginner: Basic definitions, simple syntax
   - intermediate: Problem-solving, code analysis
   - advanced: Complex scenarios, optimization

Format:
[
  {{
    "q": "What is the time complexity of binary search?",
    "options": ["O(log n)", "O(n)", "O(n^2)", "O(1)"],
    "answer": "O(log n)"
  }}
]

Generate {num_questions} questions now:"""

        # Generate with retry
        for attempt in range(2):
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=2048,
                    )
                )
                
                raw = response.text.strip()
                
                # Clean markdown
                if '```json' in raw:
                    raw = raw.split('```json')[1].split('```')[0].strip()
                elif '```' in raw:
                    raw = raw.split('```')[1].split('```')[0].strip()
                
                # Extract JSON array
                if '[' in raw and ']' in raw:
                    raw = raw[raw.find('['):raw.rfind(']')+1]
                
                # Parse
                data = json.loads(raw)
                
                # Validate
                if not isinstance(data, list) or len(data) == 0:
                    raise ValueError("Not a valid list")
                
                valid = []
                for item in data:
                    if all(k in item for k in ['q', 'options', 'answer']):
                        if isinstance(item['options'], list) and len(item['options']) == 4:
                            if item['answer'] in item['options']:
                                valid.append(item)
                
                if len(valid) >= num_questions * 0.6:
                    print(f"✅ Generated {len(valid)} AI questions")
                    return valid[:num_questions]
                
            except Exception as e:
                print(f"⚠️  Attempt {attempt+1} failed: {str(e)[:100]}")
                if attempt == 1:
                    return None
        
        return None
        
    except Exception as e:
        print(f"❌ AI generation error: {str(e)[:200]}")
        return None

# ============================================================================
# PUBLIC API
# ============================================================================

def generate_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """Main function - generate questions with fallback"""
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    
    difficulty = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 QUESTION GENERATION")
    print(f"Topic: {topic}/{subtopic} | Difficulty: {difficulty} | Count: {num_questions}")
    print(f"{'='*80}")
    
    # Try AI first
    ai_questions = generate_questions_with_ai(topic, subtopic, difficulty, num_questions)
    
    if ai_questions and len(ai_questions) >= num_questions:
        return ai_questions[:num_questions], difficulty
    
    # Fallback
    print(f"📚 Using fallback questions")
    fallback = get_fallback_questions(topic, subtopic, num_questions)
    print(f"✅ Loaded {len(fallback)} fallback questions")
    
    return fallback, difficulty


def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """Wrapper for app.py compatibility"""
    questions, difficulty = generate_questions(user_email, topic, subtopic, user_scores, num_questions)
    return {'questions': questions, 'difficulty': difficulty}


def generate_quiz_questions(topic, context, difficulty, num_questions=5):
    """For Grand Test"""
    ai_q = generate_questions_with_ai(topic, '', difficulty, num_questions)
    if ai_q:
        return ai_q
    return get_fallback_questions(topic, '', num_questions)


# ============================================================================
# STARTUP
# ============================================================================
print("\n" + "="*80)
print("🎓 CAREERLENS QUESTION GENERATOR")
print("="*80)
if GENAI_AVAILABLE and API_KEYS:
    print(f"✅ AI Mode: ACTIVE ({len(API_KEYS)} keys)")
else:
    print("📚 Fallback Mode: ACTIVE")
print("="*80 + "\n")