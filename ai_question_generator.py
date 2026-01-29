# ai_question_generator.py - PRODUCTION with SMART QUOTA MANAGEMENT

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
    print("⚠️  Install: pip install google-generativeai")

# ============================================================================
# SMART API KEY ROTATION WITH QUOTA TRACKING
# ============================================================================
API_KEYS = []
for i in range(1, 5):
    key = os.getenv(f"GEMINI_API_KEY_{i}") or (os.getenv("GEMINI_API_KEY") if i == 1 else None)
    if key:
        API_KEYS.append(key)

# Track quota for each key
key_usage = {i: {'calls': 0, 'reset_time': datetime.now()} for i in range(len(API_KEYS))}
current_key_index = 0
MAX_CALLS_PER_MINUTE = 14  # Stay under 15/min limit
QUOTA_RESET_SECONDS = 60

# Question cache
question_cache = {}

if GENAI_AVAILABLE and API_KEYS:
    try:
        genai.configure(api_key=API_KEYS[0])
        print(f"✅ GenAI configured with {len(API_KEYS)} API key(s)")
    except Exception as e:
        print(f"⚠️  Config failed: {e}")
        GENAI_AVAILABLE = False

# ============================================================================
# FALLBACK QUESTIONS
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
        'Loops': [
            {"q": "Which loop is guaranteed to execute at least once?", 
             "options": ["do-while", "while", "for", "None"], 
             "answer": "do-while"},
            {"q": "What does 'break' do in a loop?", 
             "options": ["Exits the loop", "Skips current iteration", "Restarts loop", "Pauses loop"], 
             "answer": "Exits the loop"},
            {"q": "What does 'continue' do in a loop?", 
             "options": ["Skips to next iteration", "Exits loop", "Restarts loop", "Stops program"], 
             "answer": "Skips to next iteration"},
            {"q": "What is an infinite loop?", 
             "options": ["Loop that never terminates", "Loop with no body", "Nested loop", "Loop with break"], 
             "answer": "Loop that never terminates"},
            {"q": "Which loop is best when iterations are known?", 
             "options": ["for loop", "while loop", "do-while loop", "goto loop"], 
             "answer": "for loop"}
        ],
        'Pointers': [
            {"q": "What does the * operator do in pointer declaration?", 
             "options": ["Declares a pointer", "Dereferences a pointer", "Gets address", "Multiplies values"], 
             "answer": "Declares a pointer"},
            {"q": "What does the & operator return?", 
             "options": ["Address of variable", "Value of variable", "Pointer to pointer", "Reference"], 
             "answer": "Address of variable"}
        ]
    },
    'Quantitative Aptitude': [
        {"q": "If 20% of x is 50, what is x?", 
         "options": ["250", "200", "300", "150"], 
         "answer": "250"},
        {"q": "What is 15% of 200?", 
         "options": ["30", "25", "35", "20"], 
         "answer": "30"}
    ],
    'Java': {'OOPs': [{"q": "What are the four pillars of OOP?", "options": ["Encapsulation, Inheritance, Polymorphism, Abstraction", "Classes, Objects, Methods, Variables", "Public, Private, Protected, Default", "None"], "answer": "Encapsulation, Inheritance, Polymorphism, Abstraction"}]},
    'Python': {'Lists': [{"q": "How do you create an empty list?", "options": ["[]", "{}", "()", "list"], "answer": "[]"}]}
}

GENERIC_FALLBACK = [
    {"q": "What is a key concept in this topic?", 
     "options": ["Understanding core principles", "Memorizing facts", "Ignoring details", "Guessing answers"], 
     "answer": "Understanding core principles"}
]

# ============================================================================
# DIFFICULTY GUIDELINES FOR AI - PLACEMENT TEST FOCUSED
# ============================================================================
def get_difficulty_guidelines(difficulty):
    """Return specific guidelines for each difficulty level - PLACEMENT TEST STYLE"""
    
    # Topic-specific guidelines
    topic_examples = {
        "beginner": {
            "C": "Basic syntax: 'What is the output of printf(\"%d\", 5+3);?' or 'How to declare a variable?'",
            "Java": "Simple OOP: 'What is a class?' or 'Difference between public and private?'",
            "Python": "Basic syntax: 'How to create a list?' or 'What does append() do?'",
            "Reading Comprehension": "Simple passage (3-4 lines) about daily topics. Ask: What is the main idea? What does the author suggest?",
            "Logical Reasoning": "Simple patterns: 2,4,6,8,? or If A>B and B>C, then A__C",
            "Quantitative Aptitude": "Basic arithmetic: percentages, ratios, simple interest"
        },
        "intermediate": {
            "C": "Code analysis: 'What's the output of this loop?' or 'Find the error in this code'",
            "Java": "Inheritance/polymorphism: 'What happens when you override?' or 'Constructor behavior?'",
            "Python": "List comprehensions, dictionary operations, simple error handling",
            "Reading Comprehension": "Medium passage (6-8 lines) from news/business. Ask: Author's opinion? Supporting evidence?",
            "Logical Reasoning": "Syllogisms, coded relationships, data sufficiency",
            "Quantitative Aptitude": "Time & work, profit & loss, compound interest"
        },
        "advanced": {
            "C": "Pointers, memory management: 'What's wrong with this malloc?' or 'Pointer arithmetic result?'",
            "Java": "Exception handling, multithreading, collections framework edge cases",
            "Python": "Decorators, generators, context managers, advanced OOP",
            "Reading Comprehension": "Complex passage with multiple viewpoints. Ask: Implicit assumptions? Weaknesses in argument?",
            "Logical Reasoning": "Complex puzzles, analytical reasoning with constraints",
            "Quantitative Aptitude": "Permutations/combinations, probability, data interpretation"
        }
    }
    
    guidelines = {
        "beginner": f"""
BEGINNER Level - Entry-level placement test questions:

STYLE: Direct, clear, one-step problems
FOCUS: Basic definitions, simple recall, fundamental concepts
AVOID: Multi-step reasoning, complex scenarios, edge cases

QUESTION TYPES YOU MUST USE:
✓ "What is [concept]?" - Test basic definitions
✓ "Which statement is TRUE about [topic]?" - Simple facts
✓ "What does [function/command] do?" - Basic functionality
✓ For Reading: Short passage (3-4 lines), ask main idea or direct fact
✓ For Aptitude: Simple arithmetic (10% of 200 = ?)
✓ For Coding: Basic syntax questions, not code execution

EXAMPLE FORMATS:
- C: "What is the correct way to declare an integer variable?"
- Java: "Which keyword is used to create a class?"
- Reading: [Short passage about climate] "What is the author's main concern?"
- Aptitude: "If 20% of 500 = x, then x = ?"

Keep it SIMPLE and CONFIDENCE-BUILDING.""",
        
        "intermediate": f"""
INTERMEDIATE Level - Standard placement test difficulty:

STYLE: Practical, scenario-based, requires application
FOCUS: Problem-solving, code analysis, application of concepts
AVOID: Extremely tricky edge cases, PhD-level analysis

QUESTION TYPES YOU MUST USE:
✓ "What is the OUTPUT of this code?" - Code execution (5-6 lines max)
✓ "Which approach is BEST for [scenario]?" - Practical application
✓ "Find the ERROR in this code" - Debugging skills
✓ For Reading: Medium passage (6-8 lines), ask inference or author's opinion
✓ For Aptitude: Word problems (time-distance, profit-loss)
✓ For Coding: Simple algorithm questions

EXAMPLE FORMATS:
- C: "What will this loop print?" [show simple for loop]
- Java: "What happens when a subclass overrides a method?"
- Reading: [News article paragraph] "What does the author imply about the policy?"
- Aptitude: "A train travels 60 km/h for 2 hours. Distance covered?"

Keep it PRACTICAL and INTERVIEW-RELEVANT.""",
        
        "advanced": f"""
ADVANCED Level - Senior placement test / competitive difficulty:

STYLE: Complex scenarios, optimization, deep understanding
FOCUS: Edge cases, efficiency, design decisions, critical thinking
AVOID: Theoretical computer science, research-level questions

QUESTION TYPES YOU MUST USE:
✓ "What's the TIME COMPLEXITY of [algorithm]?" - Efficiency
✓ "What happens in THIS edge case?" - Boundary conditions
✓ "How would you OPTIMIZE this?" - Design thinking
✓ For Reading: Complex argument analysis, identify assumptions
✓ For Aptitude: Permutations, probability, complex word problems
✓ For Coding: Data structure design, algorithm optimization

EXAMPLE FORMATS:
- C: "What's the output if malloc fails in this code?" [show pointer code]
- Java: "How do you prevent deadlock in multithreading?"
- Reading: [Opinion piece] "What assumption does the author make about the economy?"
- Aptitude: "In how many ways can 5 people sit in a circle?"

Keep it CHALLENGING but FAIR for experienced candidates."""
    }
    
    return guidelines.get(difficulty, guidelines["intermediate"])

def get_example_question(topic, difficulty):
    """Provide a good example question for the prompt"""
    examples = {
        ("C", "beginner"): '"What is the correct way to declare an integer variable in C?" → ["int x;", "integer x;", "x: int;", "var int x;"]',
        ("C", "intermediate"): '"What is the output of: for(int i=0; i<3; i++) printf(\\"%d\\", i);" → ["012", "123", "0123", "Error"]',
        ("C", "advanced"): '"What happens if malloc() fails in this code: int *p = (int*)malloc(sizeof(int)); *p = 10;" → ["Segmentation fault", "Returns NULL", "Compiler error", "Undefined behavior"]',
        
        ("Java", "beginner"): '"Which keyword is used to inherit a class in Java?" → ["extends", "inherits", "implements", "derives"]',
        ("Java", "intermediate"): '"What is the output of: System.out.println(10 + 20 + \\"30\\");" → ["3030", "50", "102030", "Error"]',
        ("Java", "advanced"): '"Which collection is thread-safe in Java?" → ["Vector", "ArrayList", "HashMap", "HashSet"]',
        
        ("Reading Comprehension", "beginner"): '[Passage: "Solar energy is becoming popular. It is clean and renewable."] "What is the main topic?" → ["Solar energy benefits", "Energy crisis", "Renewable resources", "Clean technology"]',
        ("Reading Comprehension", "intermediate"): '[Passage: 6-line news article] "What does the author suggest about the policy?" → [4 inference-based options]',
        ("Reading Comprehension", "advanced"): '[Passage: Opinion piece] "What assumption does the author make?" → [4 critical analysis options]',
        
        ("Quantitative Aptitude", "beginner"): '"What is 20% of 500?" → ["100", "50", "200", "250"]',
        ("Quantitative Aptitude", "intermediate"): '"A train travels 60 km/h for 2 hours, then 80 km/h for 3 hours. Total distance?" → ["360 km", "420 km", "280 km", "340 km"]',
        ("Quantitative Aptitude", "advanced"): '"In how many ways can 5 people sit in a circle?" → ["24", "120", "60", "20"]',
        
        ("Logical Reasoning", "beginner"): '"Complete: 2, 4, 6, 8, __" → ["10", "9", "12", "16"]',
        ("Logical Reasoning", "intermediate"): '"If A > B and B > C, then:" → ["A > C", "C > A", "A = C", "Cannot determine"]',
        ("Logical Reasoning", "advanced"): '"If all programmers are logical, and some logical people are creative, can we conclude some programmers are creative?" → ["No", "Yes", "Sometimes", "Insufficient data"]',
    }
    
    # Try to find exact match
    key = (topic, difficulty)
    if key in examples:
        return examples[key]
    
    # Try topic-only match
    for (t, d), example in examples.items():
        if topic.lower() in t.lower() and d == difficulty:
            return example
    
    # Default
    return '"What is a key concept in this topic?" → ["Understanding fundamentals", "Memorizing syntax", "Random guessing", "Ignoring details"]'

# ============================================================================
# SMART QUOTA MANAGEMENT
# ============================================================================
def get_available_key():
    """Find a key that hasn't exceeded quota"""
    global current_key_index, key_usage
    
    now = datetime.now()
    
    # Check each key
    for attempt in range(len(API_KEYS)):
        key_idx = (current_key_index + attempt) % len(API_KEYS)
        usage = key_usage[key_idx]
        
        # Reset counter if minute passed
        if (now - usage['reset_time']).total_seconds() >= QUOTA_RESET_SECONDS:
            usage['calls'] = 0
            usage['reset_time'] = now
        
        # Check if key has quota available
        if usage['calls'] < MAX_CALLS_PER_MINUTE:
            current_key_index = key_idx
            return key_idx, True
    
    # All keys exhausted - find next reset time
    earliest_reset = min(key_usage.values(), key=lambda x: x['reset_time'])
    wait_seconds = QUOTA_RESET_SECONDS - (now - earliest_reset['reset_time']).total_seconds()
    
    if wait_seconds > 0:
        print(f"⏰ All keys exhausted. Waiting {int(wait_seconds)}s for quota reset...")
        time.sleep(wait_seconds + 1)
        # Reset all counters
        for usage in key_usage.values():
            usage['calls'] = 0
            usage['reset_time'] = datetime.now()
        return 0, True
    
    return 0, False

# ============================================================================
# HELPERS
# ============================================================================
def get_fallback_questions(topic, subtopic, num_questions=5):
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
    """
    Advanced adaptive difficulty - starts at BEGINNER, progresses based on performance
    Each topic has independent difficulty progression
    """
    # NEW USERS start at BEGINNER (not intermediate!)
    if not user_scores:
        return "beginner"
    
    # Filter scores for THIS specific topic/subtopic
    relevant_scores = [
        s for s in user_scores 
        if s['topic'] == topic and (not subtopic or s.get('subtopic', '') == subtopic)
    ]
    
    # NO HISTORY for this topic? Start at BEGINNER
    if not relevant_scores:
        return "beginner"
    
    # Calculate performance metrics
    total_score = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    attempt_count = len(relevant_scores)
    
    if total_questions == 0:
        return "beginner"
    
    # Calculate percentage
    percent = (total_score / total_questions) * 100
    
    # Get recent performance (last 3 attempts)
    recent_scores = relevant_scores[-3:] if len(relevant_scores) >= 3 else relevant_scores
    recent_total = sum(s['score'] for s in recent_scores)
    recent_questions = sum(s['total_questions'] for s in recent_scores)
    recent_percent = (recent_total / recent_questions * 100) if recent_questions > 0 else 0
    
    # STRICT PROGRESSION RULES
    print(f"   📊 Performance Analysis:")
    print(f"      Overall: {percent:.1f}% ({total_score}/{total_questions})")
    print(f"      Recent: {recent_percent:.1f}% (last {len(recent_scores)} attempts)")
    print(f"      Total Attempts: {attempt_count}")
    
    # BEGINNER → INTERMEDIATE: Need consistent good performance
    if percent < 50:
        # Poor performance - stay at beginner
        return "beginner"
    
    elif 50 <= percent < 70:
        # Moderate performance
        if attempt_count < 3:
            # Not enough attempts - stay at beginner
            return "beginner"
        elif recent_percent >= 60:
            # Recent improvement - move to intermediate
            return "intermediate"
        else:
            # Inconsistent - stay at beginner
            return "beginner"
    
    elif 70 <= percent < 85:
        # Good performance
        if attempt_count < 5:
            # Building consistency - intermediate
            return "intermediate"
        elif recent_percent >= 75:
            # Ready for advanced
            return "advanced"
        else:
            # Stay at intermediate
            return "intermediate"
    
    else:  # percent >= 85
        # Excellent performance
        if attempt_count >= 5 and recent_percent >= 80:
            # Mastery - advanced level
            return "advanced"
        else:
            # Stay at intermediate until consistent
            return "intermediate"


# ============================================================================
# AI GENERATION WITH SMART QUOTA
# ============================================================================
def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=5):
    """Generate with smart quota management"""
    global current_key_index, key_usage
    
    if not GENAI_AVAILABLE or not API_KEYS:
        return None
    
    # Check cache
    cache_key = f"{topic}_{subtopic}_{difficulty}_{num_questions}"
    if cache_key in question_cache:
        print(f"💾 Using cached questions")
        return question_cache[cache_key]
    
    try:
        print(f"🤖 AI Generation: {topic}/{subtopic} ({difficulty})...")
        
        models_to_try = [
            'models/gemini-2.5-flash',
            'models/gemini-flash-latest',
            'models/gemini-2.0-flash'
        ]
        
        for model_name in models_to_try:
            # Get available key with quota
            key_idx, available = get_available_key()
            
            if not available:
                print(f"❌ No API quota available across all keys")
                return None
            
            try:
                # Configure with available key
                if key_idx != current_key_index:
                    genai.configure(api_key=API_KEYS[key_idx])
                    current_key_index = key_idx
                
                print(f"   Using Key {key_idx + 1} (calls: {key_usage[key_idx]['calls']}/{MAX_CALLS_PER_MINUTE})")
                
                model = genai.GenerativeModel(model_name)
                
                prompt = f"""You are creating {difficulty.upper()} level placement test questions for campus recruitment.

TOPIC: {topic}
SUBTOPIC: {subtopic if subtopic else 'General'}
DIFFICULTY: {difficulty}
NUMBER OF QUESTIONS: {num_questions}

{get_difficulty_guidelines(difficulty)}

STRICT OUTPUT FORMAT - Return ONLY this JSON array (no markdown, no explanation):
[
  {{"q": "Question text here?", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Option A"}},
  {{"q": "Question text here?", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Option A"}}
]

MANDATORY RULES:
1. Generate EXACTLY {num_questions} questions
2. Each question: 1 question text + EXACTLY 4 options
3. "answer" = EXACT text from options (not A/B/C/D)
4. All 4 options must be plausible (no obviously wrong answers)
5. Match {difficulty} difficulty level precisely
6. Questions must be PLACEMENT TEST style (not academic theory)
7. Keep questions PRACTICAL and INTERVIEW-RELEVANT

BAD EXAMPLE (too academic):
"Analyze the rhetorical effect of qualified language in medical discourse..."

GOOD EXAMPLE for {difficulty}:
{get_example_question(topic, difficulty)}

Generate {num_questions} questions NOW:"""

                # Increment usage counter BEFORE call
                key_usage[key_idx]['calls'] += 1
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=2048
                    )
                )
                
                raw = response.text.strip()
                
                if '```json' in raw:
                    raw = raw.split('```json')[1].split('```')[0].strip()
                elif '```' in raw:
                    raw = raw.split('```')[1].split('```')[0].strip()
                
                if '[' in raw and ']' in raw:
                    raw = raw[raw.find('['):raw.rfind(']')+1]
                
                data = json.loads(raw)
                
                if isinstance(data, list) and len(data) > 0:
                    valid = []
                    for item in data:
                        if all(k in item for k in ['q', 'options', 'answer']):
                            if isinstance(item['options'], list) and len(item['options']) == 4:
                                if item['answer'] in item['options']:
                                    valid.append(item)
                    
                    if len(valid) >= num_questions * 0.6:
                        result = valid[:num_questions]
                        question_cache[cache_key] = result
                        print(f"✅ Generated {len(result)} questions using {model_name}")
                        return result
                
            except Exception as model_error:
                error_msg = str(model_error)
                if '429' in error_msg or 'quota' in error_msg.lower():
                    print(f"⚠️  Key {key_idx + 1} hit quota (marking exhausted)")
                    key_usage[key_idx]['calls'] = MAX_CALLS_PER_MINUTE  # Mark as exhausted
                    continue
                else:
                    print(f"⚠️  {model_name} failed: {error_msg[:50]}")
                    continue
        
        return None
        
    except Exception as e:
        print(f"❌ AI error: {str(e)[:100]}")
        return None

# ============================================================================
# PUBLIC API
# ============================================================================
def generate_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    difficulty = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 QUESTION GENERATION")
    print(f"Topic: {topic}/{subtopic} | Difficulty: {difficulty} | Count: {num_questions}")
    print(f"{'='*80}")
    
    ai_questions = generate_questions_with_ai(topic, subtopic, difficulty, num_questions)
    if ai_questions and len(ai_questions) >= num_questions:
        return ai_questions[:num_questions], difficulty
    
    print(f"📚 Using fallback questions")
    fallback = get_fallback_questions(topic, subtopic, num_questions)
    print(f"✅ Loaded {len(fallback)} fallback questions")
    return fallback, difficulty

def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    questions, difficulty = generate_questions(user_email, topic, subtopic, user_scores, num_questions)
    return {'questions': questions, 'difficulty': difficulty}

def generate_quiz_questions(topic, context, difficulty, num_questions=5):
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
    print(f"✅ AI Mode: ACTIVE ({len(API_KEYS)} keys with smart quota management)")
else:
    print("📚 Fallback Mode: ACTIVE")
print("="*80 + "\n")