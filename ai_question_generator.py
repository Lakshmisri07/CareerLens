# ai_question_generator.py - PRODUCTION with BTECH-LEVEL PROMPT ENGINEERING

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

# Question cache - DISABLED to prevent repetition
# question_cache = {}

if GENAI_AVAILABLE and API_KEYS:
    try:
        genai.configure(api_key=API_KEYS[0])
        print(f"✅ GenAI configured with {len(API_KEYS)} API key(s)")
    except Exception as e:
        print(f"⚠️  Config failed: {e}")
        GENAI_AVAILABLE = False

# ============================================================================
# FALLBACK QUESTIONS - UPDATED TO BTECH LEVEL
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
             "answer": "Segmentation fault"}
        ]
    },
    'Quantitative Aptitude': [
        {"q": "A product costs ₹500. After 20% discount and 18% GST, what is the final price?", 
         "options": ["₹472", "₹590", "₹400", "₹520"], 
         "answer": "₹472"},
        {"q": "Train A (60 km/h) and Train B (90 km/h) travel towards each other from 300 km apart. When do they meet?", 
         "options": ["2 hours", "2.5 hours", "3 hours", "1.5 hours"], 
         "answer": "2 hours"}
    ],
    'Synonyms and Antonyms': [
        {"q": "Synonym for AMELIORATE:", 
         "options": ["Improve", "Deteriorate", "Stagnate", "Complicate"], 
         "answer": "Improve"},
        {"q": "Antonym for VERBOSE:", 
         "options": ["Concise", "Wordy", "Elaborate", "Detailed"], 
         "answer": "Concise"}
    ],
    'Grammar': [
        {"q": "Identify the error: 'Neither of the students have submitted their assignment.'", 
         "options": ["'have' should be 'has'", "No error", "'their' should be 'his'", "'students' should be 'student'"], 
         "answer": "'have' should be 'has'"},
        {"q": "Choose correct: 'The data ___ that climate change is real.'", 
         "options": ["shows", "show", "showing", "shown"], 
         "answer": "shows"}
    ],
    'Java': {
        'OOPs': [
            {"q": "What is runtime polymorphism demonstrated by: Parent p = new Child(); p.display();?", 
             "options": ["Method overriding", "Method overloading", "Encapsulation", "Abstraction"], 
             "answer": "Method overriding"},
            {"q": "If class A has private int x, can class B (extends A) access x?", 
             "options": ["No, private members are not inherited", "Yes, through inheritance", "Yes, using super.x", "Only if B is in same package"], 
             "answer": "No, private members are not inherited"}
        ]
    },
    'Python': {
        'Lists': [
            {"q": "What is the output of: L=[1,2,3]; print(L[::−1])?", 
             "options": ["[3, 2, 1]", "[1, 2, 3]", "Error", "None"], 
             "answer": "[3, 2, 1]"},
            {"q": "What does list comprehension [x**2 for x in range(3)] produce?", 
             "options": ["[0, 1, 4]", "[1, 4, 9]", "[0, 1, 2]", "Error"], 
             "answer": "[0, 1, 4]"}
        ]
    }
}

GENERIC_FALLBACK = [
    {"q": "What is a fundamental principle in solving placement test questions?", 
     "options": ["Understand the core concept, not just memorize", "Guess randomly", "Skip difficult ones", "Only practice easy questions"], 
     "answer": "Understand the core concept, not just memorize"}
]

# ============================================================================
# BTECH-LEVEL DIFFICULTY GUIDELINES - ENHANCED PROMPT ENGINEERING
# ============================================================================
def get_difficulty_guidelines(difficulty):
    """Return sophisticated guidelines for BTECH placement test level questions"""
    
    # BTECH-level topic-specific guidelines with realistic examples
    topic_examples = {
        "beginner": {
            "C": "Code output questions: 'What prints: int x=5; printf(\"%d\", ++x);' → [5, 6, Undefined, Error]. Test fundamentals with actual code execution.",
            "Java": "OOP fundamentals with context: 'If class A has private int x=10, can class B (extends A) access x directly?' → [Yes, No, Only via getter, Only in same package]",
            "Python": "Type system: 'What is type([1, 2, \"3\"])?' → [list, tuple, dict, error]. Python-specific behavior.",
            "Reading Comprehension": "Professional passage (5-6 lines) about technology/business trends. Ask: What is the author's primary concern? What evidence supports the claim?",
            "Logical Reasoning": "Number/letter coding: 'If CAT=315, DOG=426, then BAT=?' → Pattern recognition with logic",
            "Quantitative Aptitude": "Real-world calculations: 'A product costs ₹500. After 20% discount and 18% GST, final price?' → Multi-step percentage problems",
            "Synonyms and Antonyms": "Advanced vocabulary (GRE-level): 'Synonym for AMELIORATE' → [Improve, Deteriorate, Worsen, Stagnate]",
            "Grammar": "Error identification: 'Neither of the students (have/has) completed the assignment.' → Subject-verb agreement",
            "DBMS": "SQL basics: 'Which clause filters rows BEFORE grouping?' → [WHERE, HAVING, ORDER BY, GROUP BY]",
            "OS": "Process concepts: 'What scheduling algorithm can cause starvation?' → [FCFS, SJF, Round Robin, Priority]",
            "Data Structures": "Complexity: 'Worst-case time for binary search?' → [O(log n), O(n), O(n²), O(1)]"
        },
        "intermediate": {
            "C": "Pointer arithmetic: 'Output: int arr[]={1,2,3}; printf(\"%d\", *(arr+1));' → [1, 2, 3, Address]. Requires understanding of pointer-array relationship.",
            "Java": "Polymorphism behavior: 'Parent p = new Child(); p.show(); Which show() executes?' → Runtime binding concepts",
            "Python": "Slicing mechanics: 'L=[1,2,3,4,5]; L[1::2] produces?' → [2,4] or [1,3,5] - exact syntax understanding",
            "Reading Comprehension": "Policy/economics article (8-10 lines). Ask: What assumption underlies the argument? Identify supporting evidence vs opinion.",
            "Logical Reasoning": "Syllogisms: 'All engineers are logical. Some logical people are creative. Can we conclude some engineers are creative?' → [No, Yes, Maybe, Insufficient data]",
            "Quantitative Aptitude": "Relative speed: 'Train A (60 km/h) and B (80 km/h) travel towards each other from 280 km apart. When do they meet?' → Time calculation",
            "Synonyms and Antonyms": "Contextual usage: 'The manager's approach was PRAGMATIC during the crisis.' Synonym → [Practical, Idealistic, Theoretical, Emotional]",
            "Grammar": "Sentence correction: 'The data shows that climate change are affecting regions.' → Identify error (data=singular, are=wrong)",
            "DBMS": "Normalization: 'A table with partial dependency is in which normal form?' → [1NF, 2NF, 3NF, BCNF]",
            "OS": "Deadlock conditions: 'Which is NOT a Coffman condition?' → Specific OS knowledge",
            "Data Structures": "Tree properties: 'A BST with n nodes has minimum height?' → [log n, n, n/2, sqrt(n)]"
        },
        "advanced": {
            "C": "Undefined behavior: 'char *p=\"hello\"; p[0]='H'; What happens?' → [Works fine, Undefined behavior, Segfault, Compiler error]. String literal immutability.",
            "Java": "Thread safety: 'Two threads increment shared variable 1000 times. Final value without synchronization?' → [2000, <2000, >2000, Compile error]",
            "Python": "Decorators: 'What does @functools.lru_cache do and why use it?' → Memoization and performance optimization",
            "Reading Comprehension": "Complex editorial (12-15 lines) with nuanced argument. Ask: Identify the logical fallacy. What counterargument would most weaken this?",
            "Logical Reasoning": "Constraint-based: '5 people (A,B,C,D,E) in row. A not at ends. B next to C. D not next to E. Valid arrangements?' → Systematic elimination",
            "Quantitative Aptitude": "Combinatorics: 'Committee of 5 from 6 men, 4 women with at least 2 women. How many ways?' → nCr with conditions",
            "Synonyms and Antonyms": "Subtle distinctions: 'In technical writing, antonym for VERBOSE' → [Concise, Terse, Brief, Laconic] - nuanced differences",
            "Grammar": "Advanced syntax: 'Having been CEO for 10 years, the company was led with vision.' → Dangling modifier identification",
            "DBMS": "Transaction isolation: 'Which isolation level prevents phantom reads?' → [Read Uncommitted, Read Committed, Repeatable Read, Serializable]",
            "OS": "Memory management: 'In paging, what is internal fragmentation?' → Deep OS concepts",
            "Data Structures": "Algorithm design: 'Optimal algorithm to find kth smallest element in unsorted array?' → Quickselect vs other approaches"
        }
    }
    
    # Difficulty-specific guidelines with BTECH placement test focus
    guidelines = {
        "beginner": f"""
BEGINNER Level - Entry BTECH Placement Test (First Round):

CRITICAL: Questions must test UNDERSTANDING, not just definitions.

QUESTION STYLE:
✓ Code execution problems (small code snippets with output questions)
✓ Scenario-based (not "what is X?" but "given scenario Y, what happens?")
✓ Practical applications with concrete examples
✓ Single-step problem solving

MANDATORY FORMAT:
1. Use REAL code snippets (3-5 lines max)
2. Ask "What is the OUTPUT?" or "What happens?"
3. Options must include common mistakes students make
4. One clearly correct answer, three plausible distractors

EXAMPLES BY TOPIC:
{topic_examples['beginner'].get('C', '')}
{topic_examples['beginner'].get('Java', '')}
{topic_examples['beginner'].get('Python', '')}
{topic_examples['beginner'].get('Quantitative Aptitude', '')}
{topic_examples['beginner'].get('Grammar', '')}
{topic_examples['beginner'].get('Reading Comprehension', '')}

AVOID:
✗ "What is the definition of X?"
✗ "Which keyword is used for Y?"
✗ Trivial yes/no questions
✗ Questions without context

Remember: This is for BTECH students preparing for TCS/Infosys/Wipro campus placements!
""",
        
        "intermediate": f"""
INTERMEDIATE Level - Standard BTECH Placement (Technical Round):

FOCUS: Problem-solving with moderate complexity, application of concepts

QUESTION STYLE:
✓ Multi-step reasoning required
✓ Code analysis with edge cases
✓ "Given scenario X, determine outcome Y" format
✓ Compare/contrast different approaches
✓ Real-world application scenarios

MANDATORY CHARACTERISTICS:
1. Code snippets 5-8 lines (not trivial)
2. Requires understanding of TWO concepts together (e.g., pointers + arrays)
3. Options include subtle mistakes (not obviously wrong)
4. Test depth, not just recall

EXAMPLES BY TOPIC:
{topic_examples['intermediate'].get('C', '')}
{topic_examples['intermediate'].get('Java', '')}
{topic_examples['intermediate'].get('Python', '')}
{topic_examples['intermediate'].get('Quantitative Aptitude', '')}
{topic_examples['intermediate'].get('Logical Reasoning', '')}
{topic_examples['intermediate'].get('Grammar', '')}

COMPLEXITY INDICATORS:
- Requires 2-3 mental steps to solve
- Tests interaction between concepts
- Common interview question difficulty
- TCS NQT / Infosys HackWithInfy level

AVOID:
✗ Simple definitions
✗ One-step lookups
✗ Unrealistic code scenarios
""",
        
        "advanced": f"""
ADVANCED Level - Competitive BTECH Placement (Product Companies):

TARGET: Google/Microsoft/Amazon campus placement difficulty

QUESTION STYLE:
✓ Complex scenarios requiring deep understanding
✓ Edge cases and undefined behavior
✓ Algorithm optimization problems
✓ Tradeoff analysis (time vs space)
✓ Multi-concept integration
✓ Critical thinking about assumptions

MANDATORY CHARACTERISTICS:
1. Tests MASTERY, not just knowledge
2. Multiple valid-looking answers (subtle differences)
3. Requires systematic problem-solving approach
4. May involve constraints/optimizations
5. Real interview questions from top companies

EXAMPLES BY TOPIC:
{topic_examples['advanced'].get('C', '')}
{topic_examples['advanced'].get('Java', '')}
{topic_examples['advanced'].get('Python', '')}
{topic_examples['advanced'].get('Quantitative Aptitude', '')}
{topic_examples['advanced'].get('Logical Reasoning', '')}
{topic_examples['advanced'].get('Grammar', '')}

COMPLEXITY INDICATORS:
- Requires 4-5 mental steps
- Multiple concepts tested simultaneously
- Edge cases / undefined behavior
- Algorithm design and optimization
- Google/Amazon interview level

FOCUS AREAS:
- Memory management and pointers (C)
- Concurrency and thread safety (Java)
- Language-specific optimizations (Python)
- Complex probability/combinatorics (Aptitude)
- Logical fallacies and argument analysis (Reading)

This is for students targeting top product companies!
"""
    }
    
    return guidelines.get(difficulty, guidelines["intermediate"])

def get_example_question(topic, difficulty):
    """Provide BTECH-level example question for the prompt"""
    examples = {
        ("C", "beginner"): '"What is the output: int x=5; printf(\\"%d\\", ++x);" → ["5", "6", "Undefined", "Error"]',
        ("C", "intermediate"): '"What prints: int arr[]={10,20,30}; int *p=arr; printf(\\"%d\\", *(p+2));" → ["10", "20", "30", "Address"]',
        ("C", "advanced"): '"char *s=\\"hello\\"; s[0]=\'H\'; What happens?" → ["Works fine", "Segmentation fault", "Undefined behavior", "Compiler error"]',
        
        ("Java", "beginner"): '"If class A has private int x=10, can class B (extends A) access x directly?" → ["Yes", "No", "Only via super", "Only in same package"]',
        ("Java", "intermediate"): '"Parent p = new Child(); p.show(); Which show() method executes?" → ["Parent\'s", "Child\'s", "Compile error", "Runtime error"]',
        ("Java", "advanced"): '"Without synchronization, two threads increment shared variable 1000 times. Final value?" → ["2000", "Less than 2000", "More than 2000", "Compilation error"]',
        
        ("Python", "beginner"): '"What is the type of result: result = [1, 2, \\"3\\"]?" → ["list", "tuple", "dict", "str"]',
        ("Python", "intermediate"): '"What does L[1::2] return for L=[1,2,3,4,5]?" → ["[2,4]", "[1,3,5]", "[2,3,4]", "Error"]',
        ("Python", "advanced"): '"What does @functools.lru_cache decorator do?" → ["Memoizes function results", "Makes function async", "Adds logging", "Type checking"]',
        
        ("Reading Comprehension", "beginner"): '[Passage: "AI is transforming healthcare. Diagnosis accuracy has improved 40%. However, privacy concerns remain."] "What is the primary concern?" → ["Privacy issues with AI", "AI transformation", "Healthcare costs", "Diagnosis methods"]',
        ("Reading Comprehension", "intermediate"): '[Business article 8 lines] "What assumption does the author make about market trends?" → [4 analytical options]',
        ("Reading Comprehension", "advanced"): '[Complex editorial 12 lines] "Identify the logical fallacy in the author\'s argument:" → [Ad hominem, False dichotomy, Slippery slope, Hasty generalization]',
        
        ("Quantitative Aptitude", "beginner"): '"Product costs ₹500. After 20% discount then 18% GST, final price?" → ["₹472", "₹590", "₹400", "₹520"]',
        ("Quantitative Aptitude", "intermediate"): '"Train A (60 km/h) and B (90 km/h) approach from 300 km. Meeting time?" → ["2 hours", "2.5 hours", "3 hours", "3.33 hours"]',
        ("Quantitative Aptitude", "advanced"): '"Committee of 5 from 6 men, 4 women with at least 2 women. Ways?" → ["186", "120", "246", "210"]',
        
        ("Logical Reasoning", "beginner"): '"If CAT=315 and DOG=426, then BAT=?" → ["213", "214", "312", "215"]',
        ("Logical Reasoning", "intermediate"): '"All engineers are logical. Some logical people are creative. Conclusion?" → ["Some engineers are creative - Invalid", "Some engineers might be creative - Valid", "No engineers are creative - Invalid", "Cannot determine"]',
        ("Logical Reasoning", "advanced"): '"5 people in row: A not at ends, B next to C, D not next to E. Valid arrangements?" → ["24", "36", "48", "12"]',
        
        ("Synonyms and Antonyms", "beginner"): '"Synonym for AMELIORATE:" → ["Improve", "Deteriorate", "Worsen", "Stagnate"]',
        ("Synonyms and Antonyms", "intermediate"): '"In \\"The policy was PRAGMATIC\\", synonym:" → ["Practical", "Idealistic", "Theoretical", "Emotional"]',
        ("Synonyms and Antonyms", "advanced"): '"In technical writing, antonym for VERBOSE:" → ["Concise", "Terse", "Brief", "Laconic"]',
        
        ("Grammar", "beginner"): '"Correct: Neither of the students (have/has) submitted." → ["has", "have", "had", "having"]',
        ("Grammar", "intermediate"): '"Error: The data shows that prices are rising." → ["No error - data is singular", "shows→show", "are→is", "prices→price"]',
        ("Grammar", "advanced"): '"Error: Having been CEO for 10 years, the company was led well." → ["Dangling modifier - CEO did the leading", "No error", "was→is", "well→good"]',
    }
    
    # Try exact match
    key = (topic, difficulty)
    if key in examples:
        return examples[key]
    
    # Fallback to intermediate level
    fallback_key = (topic, "intermediate")
    if fallback_key in examples:
        return examples[fallback_key]
    
    # Generic fallback
    return '"Solve this problem using core concepts of the topic" → [Option A, Option B, Option C, Option D]'

# ============================================================================
# SMART QUOTA MANAGEMENT (Keep existing functions)
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
# HELPERS (Keep existing)
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
    """Advanced adaptive difficulty - BTECH placement test focused"""
    # NEW USERS start at BEGINNER
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
    
    # BTECH PLACEMENT TEST PROGRESSION RULES
    print(f"   📊 Performance Analysis:")
    print(f"      Overall: {percent:.1f}% ({total_score}/{total_questions})")
    print(f"      Recent: {recent_percent:.1f}% (last {len(recent_scores)} attempts)")
    print(f"      Total Attempts: {attempt_count}")
    
    # More aggressive progression for BTECH level
    if percent < 40:
        return "beginner"
    elif 40 <= percent < 65:
        if attempt_count >= 2 and recent_percent >= 50:
            return "intermediate"
        return "beginner"
    elif 65 <= percent < 80:
        if attempt_count >= 3 and recent_percent >= 70:
            return "advanced"
        return "intermediate"
    else:  # percent >= 80
        if attempt_count >= 4 and recent_percent >= 75:
            return "advanced"
        return "intermediate"

# ============================================================================
# AI GENERATION WITH ENHANCED PROMPT
# ============================================================================
def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=5):
    """Generate BTECH-level questions with sophisticated prompt engineering"""
    global current_key_index, key_usage
    
    if not GENAI_AVAILABLE or not API_KEYS:
        return None
    
    # NO CACHE - Always generate fresh questions to prevent repetition
    
    try:
        print(f"🤖 AI Generation: {topic}/{subtopic} ({difficulty})...")
        
        models_to_try = [
            'models/gemini-2.0-flash-exp',
            'models/gemini-1.5-flash',
            'models/gemini-flash-latest'
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
                
                # ENHANCED BTECH-LEVEL PROMPT
                prompt = f"""You are creating {difficulty.upper()} level questions for BTECH students preparing for campus placements (TCS, Infosys, Wipro, Accenture level).

TOPIC: {topic}
SUBTOPIC: {subtopic if subtopic else 'General'}
DIFFICULTY: {difficulty}
NUMBER OF QUESTIONS: {num_questions}

CRITICAL: Generate UNIQUE questions each time. Use different scenarios, code examples, and contexts. DO NOT repeat common patterns.

{get_difficulty_guidelines(difficulty)}

CRITICAL REQUIREMENTS:

1. QUESTION QUALITY:
   - NO simple "What is..." definition questions
   - Use code snippets for programming topics (show actual code, ask output)
   - Create scenario-based questions (Given X, what happens?)
   - Test UNDERSTANDING, not memorization

2. OUTPUT FORMAT - Return ONLY this JSON (no markdown, no explanation):
[
  {{"q": "Question text here?", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Option A"}},
  {{"q": "Next question?", "options": ["Option A", "Option B", "Option C", "Option D"], "answer": "Option B"}}
]

3. OPTIONS QUALITY:
   - All 4 options must look plausible to someone who doesn't know the answer
   - Include common misconceptions as wrong options
   - answer = EXACT text from options array (not A/B/C/D)
   - No obviously absurd options

4. DIFFICULTY CALIBRATION:
   - BEGINNER: Test fundamentals with simple code/scenarios (60% should get it right)
   - INTERMEDIATE: Multi-step reasoning, combine concepts (40% should get it right)
   - ADVANCED: Edge cases, optimization, deep understanding (20% should get it right)

5. PLACEMENT TEST STYLE:
   - Questions should feel like real TCS NQT / Infosys HackWithInfy
   - Practical scenarios over theoretical definitions
   - Similar to actual coding round MCQs

EXAMPLE OF GOOD {difficulty.upper()} QUESTION:
{get_example_question(topic, difficulty)}

Now generate {num_questions} questions that match this quality level:"""

                # Increment usage counter BEFORE call
                key_usage[key_idx]['calls'] += 1
                
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.95,  # Higher temperature = more creativity and variety
                        max_output_tokens=8000,  # Increased for 20 questions
                        top_p=0.95,
                        top_k=50  # More randomness
                    )
                )
                
                raw = response.text.strip()
                
                # Clean response
                if '```json' in raw:
                    raw = raw.split('```json')[1].split('```')[0].strip()
                elif '```' in raw:
                    raw = raw.split('```')[1].split('```')[0].strip()
                
                if '[' in raw and ']' in raw:
                    raw = raw[raw.find('['):raw.rfind(']')+1]
                
                data = json.loads(raw)
                
                # Validate questions
                if isinstance(data, list) and len(data) > 0:
                    valid = []
                    for item in data:
                        if all(k in item for k in ['q', 'options', 'answer']):
                            if isinstance(item['options'], list) and len(item['options']) == 4:
                                if item['answer'] in item['options']:
                                    # Additional quality check: question shouldn't be too short
                                    if len(item['q']) >= 20:
                                        valid.append(item)
                    
                    if len(valid) >= num_questions * 0.6:
                        result = valid[:num_questions]
                        # NO CACHE - Fresh questions each time
                        print(f"✅ Generated {len(result)} unique questions using {model_name}")
                        return result
                
            except Exception as model_error:
                error_msg = str(model_error)
                if '429' in error_msg or 'quota' in error_msg.lower():
                    print(f"⚠️  Key {key_idx + 1} hit quota (marking exhausted)")
                    key_usage[key_idx]['calls'] = MAX_CALLS_PER_MINUTE
                    continue
                else:
                    print(f"⚠️  {model_name} failed: {error_msg[:50]}")
                    continue
        
        return None
        
    except Exception as e:
        print(f"❌ AI error: {str(e)[:100]}")
        return None

# ============================================================================
# PUBLIC API (Keep existing)
# ============================================================================
def generate_questions(user_email, topic, subtopic, user_scores, num_questions=20):
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    difficulty = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 BTECH PLACEMENT QUESTION GENERATION")
    print(f"Topic: {topic}/{subtopic} | Difficulty: {difficulty} | Count: {num_questions}")
    print(f"{'='*80}")
    
    ai_questions = generate_questions_with_ai(topic, subtopic, difficulty, num_questions)
    if ai_questions and len(ai_questions) >= num_questions:
        return ai_questions[:num_questions], difficulty
    
    print(f"📚 Using fallback questions")
    fallback = get_fallback_questions(topic, subtopic, num_questions)
    print(f"✅ Loaded {len(fallback)} fallback questions")
    return fallback, difficulty

def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=20):
    questions, difficulty = generate_questions(user_email, topic, subtopic, user_scores, num_questions)
    return {'questions': questions, 'difficulty': difficulty}

def generate_quiz_questions(topic, context, difficulty, num_questions=20):
    ai_q = generate_questions_with_ai(topic, '', difficulty, num_questions)
    if ai_q:
        return ai_q
    return get_fallback_questions(topic, '', num_questions)

# ============================================================================
# STARTUP
# ============================================================================
print("\n" + "="*80)
print("🎓 CAREERLENS BTECH PLACEMENT QUESTION GENERATOR")
print("="*80)
if GENAI_AVAILABLE and API_KEYS:
    print(f"✅ AI Mode: ACTIVE ({len(API_KEYS)} keys with smart quota management)")
    print(f"✅ BTECH-Level Prompt Engineering: ENABLED")
else:
    print("📚 Fallback Mode: ACTIVE")
print("="*80 + "\n")