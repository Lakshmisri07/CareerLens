# ai_question_generator.py - WITH SMART CONTEXT FIX
# Changes from original:
# 1. generate_questions_with_ai() gets ai_context='' parameter
# 2. generate_questions() gets ai_context='' parameter  
# 3. Prompt now includes PLACEMENT CONTEXT and STRICT INSTRUCTION
# Everything else is identical to your working version.

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
# COMPREHENSIVE FALLBACK QUESTIONS (BTech Level)
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
            {"q": "What is the size of pointer on 64-bit system?",
             "options": ["8 bytes", "4 bytes", "Depends on data type", "2 bytes"],
             "answer": "8 bytes"},
            {"q": "What does int **p represent?",
             "options": ["Pointer to pointer", "Double pointer value", "Array of pointers", "Invalid syntax"],
             "answer": "Pointer to pointer"},
            {"q": "What is output: int a=5; int *p=&a; (*p)++; printf(\"%d\", a);",
             "options": ["6", "5", "Address", "Error"],
             "answer": "6"}
        ],
        'Loops': [
            {"q": "What is output: for(int i=0; i<3; i++) printf(\"%d \", i);",
             "options": ["0 1 2", "1 2 3", "0 1 2 3", "Infinite loop"],
             "answer": "0 1 2"},
            {"q": "Which loop executes at least once?",
             "options": ["do-while", "while", "for", "All loops"],
             "answer": "do-while"},
            {"q": "What does 'break' do in a loop?",
             "options": ["Exits the loop", "Skips current iteration", "Stops program", "Restarts loop"],
             "answer": "Exits the loop"},
            {"q": "What does 'continue' do?",
             "options": ["Skips to next iteration", "Exits loop", "Restarts loop", "Stops program"],
             "answer": "Skips to next iteration"},
            {"q": "What is output: int i=0; while(i<2) { printf(\"%d\", i); i++; }",
             "options": ["01", "12", "012", "Infinite loop"],
             "answer": "01"}
        ],
        'Functions': [
            {"q": "What is return type of main function?",
             "options": ["int", "void", "char", "float"],
             "answer": "int"},
            {"q": "Can a function return multiple values directly in C?",
             "options": ["No", "Yes", "Only using pointers", "Only arrays"],
             "answer": "No"},
            {"q": "What is function prototype?",
             "options": ["Declaration before definition", "Function body", "Return value", "Parameter list"],
             "answer": "Declaration before definition"},
            {"q": "What is recursion?",
             "options": ["Function calling itself", "Loop", "Function pointer", "Inline function"],
             "answer": "Function calling itself"},
            {"q": "What happens if function doesn't have return statement?",
             "options": ["Returns garbage for non-void", "Compilation error", "Returns 0", "Returns NULL"],
             "answer": "Returns garbage for non-void"}
        ]
    },
    'Java': {
        'OOPs': [
            {"q": "What is runtime polymorphism demonstrated by: Parent p = new Child(); p.display();?",
             "options": ["Method overriding", "Method overloading", "Encapsulation", "Abstraction"],
             "answer": "Method overriding"},
            {"q": "If class A has private int x, can class B (extends A) access x?",
             "options": ["No, private members are not inherited", "Yes, through inheritance", "Yes, using super.x", "Only if B is in same package"],
             "answer": "No, private members are not inherited"},
            {"q": "What is the purpose of 'this' keyword?",
             "options": ["Refers to current object", "Calls parent class", "Creates new object", "Static reference"],
             "answer": "Refers to current object"},
            {"q": "Which supports multiple inheritance in Java?",
             "options": ["Interfaces", "Classes", "Abstract classes", "None"],
             "answer": "Interfaces"},
            {"q": "What is encapsulation?",
             "options": ["Data hiding with methods", "Inheritance", "Polymorphism", "Abstraction"],
             "answer": "Data hiding with methods"}
        ],
        'Inheritance': [
            {"q": "Which keyword is used for inheritance?",
             "options": ["extends", "implements", "inherits", "super"],
             "answer": "extends"},
            {"q": "Can a class extend multiple classes in Java?",
             "options": ["No", "Yes", "Only interfaces", "Depends"],
             "answer": "No"},
            {"q": "What is super keyword used for?",
             "options": ["Call parent class members", "Create object", "Define interface", "Static access"],
             "answer": "Call parent class members"},
            {"q": "What is multilevel inheritance?",
             "options": ["A->B->C chain", "A extends B, C", "Multiple parents", "No inheritance"],
             "answer": "A->B->C chain"},
            {"q": "Can constructor be inherited?",
             "options": ["No", "Yes", "Only default", "Only parameterized"],
             "answer": "No"}
        ],
        'Exceptions': [
            {"q": "Which is checked exception?",
             "options": ["IOException", "NullPointerException", "ArithmeticException", "ArrayIndexOutOfBounds"],
             "answer": "IOException"},
            {"q": "What does 'finally' block do?",
             "options": ["Always executes", "Only on exception", "Only on success", "Never executes"],
             "answer": "Always executes"},
            {"q": "Which keyword throws exception?",
             "options": ["throw", "throws", "catch", "finally"],
             "answer": "throw"},
            {"q": "Can we have multiple catch blocks?",
             "options": ["Yes", "No", "Only two", "Only one"],
             "answer": "Yes"},
            {"q": "What is try-catch used for?",
             "options": ["Handle exceptions", "Create loops", "Define methods", "Import packages"],
             "answer": "Handle exceptions"}
        ]
    },
    'Python': {
        'Lists': [
            {"q": "What is the output of: L=[1,2,3]; print(L[::-1])?",
             "options": ["[3, 2, 1]", "[1, 2, 3]", "Error", "None"],
             "answer": "[3, 2, 1]"},
            {"q": "What does list comprehension [x**2 for x in range(3)] produce?",
             "options": ["[0, 1, 4]", "[1, 4, 9]", "[0, 1, 2]", "Error"],
             "answer": "[0, 1, 4]"},
            {"q": "How to add element to end of list?",
             "options": ["append()", "add()", "insert()", "push()"],
             "answer": "append()"},
            {"q": "What does L.pop() do?",
             "options": ["Removes last element", "Removes first element", "Clears list", "Returns list"],
             "answer": "Removes last element"},
            {"q": "How to get length of list L?",
             "options": ["len(L)", "L.length()", "L.size()", "count(L)"],
             "answer": "len(L)"}
        ],
        'Dictionaries': [
            {"q": "How to create empty dictionary?",
             "options": ["Both {} and dict()", "{}", "[]", "dict()"],
             "answer": "Both {} and dict()"},
            {"q": "How to access value with key 'name' in dict d?",
             "options": ["d['name']", "d.name", "d.get(name)", "d[name]"],
             "answer": "d['name']"},
            {"q": "What does d.keys() return?",
             "options": ["All keys", "All values", "Key-value pairs", "Length"],
             "answer": "All keys"},
            {"q": "How to add new key-value pair?",
             "options": ["d['key'] = value", "d.add(key, value)", "d.insert(key, value)", "d.append(key, value)"],
             "answer": "d['key'] = value"},
            {"q": "What happens if key doesn't exist in d[key]?",
             "options": ["KeyError", "Returns None", "Returns empty string", "Creates key"],
             "answer": "KeyError"}
        ],
        'File Handling': [
            {"q": "Which mode opens file for reading?",
             "options": ["'r'", "'w'", "'a'", "'x'"],
             "answer": "'r'"},
            {"q": "What does 'w' mode do to existing file?",
             "options": ["Overwrites content", "Appends content", "Reads content", "Error"],
             "answer": "Overwrites content"},
            {"q": "How to close file f?",
             "options": ["f.close()", "close(f)", "f.end()", "end(f)"],
             "answer": "f.close()"},
            {"q": "What is advantage of 'with' statement?",
             "options": ["Auto closes file", "Faster execution", "Better syntax", "Less memory"],
             "answer": "Auto closes file"},
            {"q": "How to read entire file?",
             "options": ["f.read()", "f.readall()", "f.get()", "f.fetch()"],
             "answer": "f.read()"}
        ]
    },
    'DBMS': {
        'SQL': [
            {"q": "Which command retrieves data from database?",
             "options": ["SELECT", "INSERT", "UPDATE", "DELETE"],
             "answer": "SELECT"},
            {"q": "What does WHERE clause do?",
             "options": ["Filters rows", "Sorts data", "Groups data", "Joins tables"],
             "answer": "Filters rows"},
            {"q": "Which is aggregate function?",
             "options": ["COUNT()", "WHERE", "SELECT", "FROM"],
             "answer": "COUNT()"},
            {"q": "What does DISTINCT do?",
             "options": ["Removes duplicates", "Sorts data", "Groups data", "Filters data"],
             "answer": "Removes duplicates"},
            {"q": "Which join returns all rows from both tables?",
             "options": ["FULL OUTER JOIN", "INNER JOIN", "LEFT JOIN", "RIGHT JOIN"],
             "answer": "FULL OUTER JOIN"}
        ],
        'Normalization': [
            {"q": "What is 1NF?",
             "options": ["Atomic values in columns", "No partial dependency", "No transitive dependency", "BCNF"],
             "answer": "Atomic values in columns"},
            {"q": "What is purpose of normalization?",
             "options": ["Reduce redundancy", "Increase redundancy", "Speed up queries", "Create backups"],
             "answer": "Reduce redundancy"},
            {"q": "What is 2NF?",
             "options": ["No partial dependency", "Atomic values", "No transitive dependency", "BCNF"],
             "answer": "No partial dependency"},
            {"q": "What is 3NF?",
             "options": ["No transitive dependency", "Atomic values", "No partial dependency", "BCNF"],
             "answer": "No transitive dependency"},
            {"q": "What is primary key?",
             "options": ["Unique identifier", "Foreign key reference", "Index", "Constraint"],
             "answer": "Unique identifier"}
        ],
        'Transactions': [
            {"q": "What is ACID property?",
             "options": ["Atomicity, Consistency, Isolation, Durability", "All Changes In Database", "Automatic Commit In Database", "None"],
             "answer": "Atomicity, Consistency, Isolation, Durability"},
            {"q": "What does COMMIT do?",
             "options": ["Saves changes permanently", "Reverts changes", "Starts transaction", "Ends transaction"],
             "answer": "Saves changes permanently"},
            {"q": "What does ROLLBACK do?",
             "options": ["Reverts changes", "Saves changes", "Starts transaction", "Ends transaction"],
             "answer": "Reverts changes"},
            {"q": "What is isolation level?",
             "options": ["Controls concurrent access", "Speed of transaction", "Size of transaction", "Type of transaction"],
             "answer": "Controls concurrent access"},
            {"q": "What is deadlock in DBMS?",
             "options": ["Two transactions waiting for each other", "Transaction timeout", "Database crash", "Slow query"],
             "answer": "Two transactions waiting for each other"}
        ]
    },
    'OS': {
        'Processes': [
            {"q": "What is process?",
             "options": ["Program in execution", "Compiled code", "Source code", "Binary file"],
             "answer": "Program in execution"},
            {"q": "What is PCB?",
             "options": ["Process Control Block", "Program Counter Block", "Process Creation Block", "Program Control Block"],
             "answer": "Process Control Block"},
            {"q": "What is context switching?",
             "options": ["Switching between processes", "Starting process", "Ending process", "Creating process"],
             "answer": "Switching between processes"},
            {"q": "What is zombie process?",
             "options": ["Terminated but entry exists", "Running process", "Blocked process", "Ready process"],
             "answer": "Terminated but entry exists"},
            {"q": "What is fork() system call?",
             "options": ["Creates child process", "Terminates process", "Blocks process", "Resumes process"],
             "answer": "Creates child process"}
        ],
        'Threads': [
            {"q": "What is thread?",
             "options": ["Lightweight process", "Heavyweight process", "Independent process", "System process"],
             "answer": "Lightweight process"},
            {"q": "Threads share what?",
             "options": ["Code, data, files", "Stack", "Registers", "Program counter"],
             "answer": "Code, data, files"},
            {"q": "What is multithreading?",
             "options": ["Multiple threads in process", "Multiple processes", "Single thread", "No threads"],
             "answer": "Multiple threads in process"},
            {"q": "Advantage of threads?",
             "options": ["Faster than processes", "More memory", "Better security", "Easier debugging"],
             "answer": "Faster than processes"},
            {"q": "What is race condition?",
             "options": ["Multiple threads accessing shared data", "Thread deadlock", "Thread starvation", "Thread termination"],
             "answer": "Multiple threads accessing shared data"}
        ],
        'Memory Management': [
            {"q": "What is paging?",
             "options": ["Dividing memory into fixed blocks", "Variable blocks", "Continuous allocation", "Random allocation"],
             "answer": "Dividing memory into fixed blocks"},
            {"q": "What is page fault?",
             "options": ["Page not in memory", "Page in memory", "Invalid page", "Duplicate page"],
             "answer": "Page not in memory"},
            {"q": "What is virtual memory?",
             "options": ["Uses hard disk as RAM", "Physical memory", "Cache memory", "Register memory"],
             "answer": "Uses hard disk as RAM"},
            {"q": "What is thrashing?",
             "options": ["Excessive paging", "Normal paging", "No paging", "Efficient paging"],
             "answer": "Excessive paging"},
            {"q": "What is segmentation?",
             "options": ["Logical division of memory", "Physical division", "Fixed blocks", "Random division"],
             "answer": "Logical division of memory"}
        ]
    },
    'Data Structures': {
        'Linked List': [
            {"q": "What is advantage of linked list over array?",
             "options": ["Dynamic size", "Fixed size", "Faster access", "Less memory"],
             "answer": "Dynamic size"},
            {"q": "What is time complexity of insertion at beginning?",
             "options": ["O(1)", "O(n)", "O(log n)", "O(n^2)"],
             "answer": "O(1)"},
            {"q": "What is doubly linked list?",
             "options": ["Two pointers per node", "One pointer", "Three pointers", "No pointers"],
             "answer": "Two pointers per node"},
            {"q": "What is circular linked list?",
             "options": ["Last node points to first", "No last node", "Multiple lists", "Linear list"],
             "answer": "Last node points to first"},
            {"q": "What does head pointer store?",
             "options": ["First node address", "Last node address", "Data", "Size"],
             "answer": "First node address"}
        ],
        'Stacks': [
            {"q": "What is stack principle?",
             "options": ["LIFO", "FIFO", "Random", "Priority"],
             "answer": "LIFO"},
            {"q": "What operations are in stack?",
             "options": ["Push, Pop", "Enqueue, Dequeue", "Insert, Delete", "Add, Remove"],
             "answer": "Push, Pop"},
            {"q": "What is stack overflow?",
             "options": ["Stack is full", "Stack is empty", "Stack is normal", "Stack is null"],
             "answer": "Stack is full"},
            {"q": "What is stack underflow?",
             "options": ["Pop from empty stack", "Push to full stack", "Normal operation", "Stack overflow"],
             "answer": "Pop from empty stack"},
            {"q": "Stack is used in?",
             "options": ["Function calls", "BFS", "Sorting", "Searching"],
             "answer": "Function calls"}
        ],
        'Queues': [
            {"q": "What is queue principle?",
             "options": ["FIFO", "LIFO", "Random", "Priority"],
             "answer": "FIFO"},
            {"q": "What operations are in queue?",
             "options": ["Enqueue, Dequeue", "Push, Pop", "Insert, Delete", "Add, Remove"],
             "answer": "Enqueue, Dequeue"},
            {"q": "What is circular queue?",
             "options": ["Last position connects to first", "Linear queue", "Priority queue", "Double ended queue"],
             "answer": "Last position connects to first"},
            {"q": "What is priority queue?",
             "options": ["Elements have priorities", "Normal queue", "LIFO queue", "Stack queue"],
             "answer": "Elements have priorities"},
            {"q": "Queue is used in?",
             "options": ["BFS", "DFS", "Recursion", "Backtracking"],
             "answer": "BFS"}
        ],
        'Trees': [
            {"q": "What is binary tree?",
             "options": ["Max 2 children per node", "Max 3 children", "Any children", "No children"],
             "answer": "Max 2 children per node"},
            {"q": "What is BST property?",
             "options": ["Left < Root < Right", "Left > Root > Right", "No order", "Balanced"],
             "answer": "Left < Root < Right"},
            {"q": "What is tree traversal?",
             "options": ["Visiting all nodes", "Creating tree", "Deleting tree", "Searching node"],
             "answer": "Visiting all nodes"},
            {"q": "What is inorder traversal?",
             "options": ["Left, Root, Right", "Root, Left, Right", "Left, Right, Root", "Random"],
             "answer": "Left, Root, Right"},
            {"q": "What is height of tree?",
             "options": ["Longest path from root to leaf", "Number of nodes", "Number of edges", "Width of tree"],
             "answer": "Longest path from root to leaf"}
        ]
    },
    'Quantitative Aptitude': [
        {"q": "A product costs 500 rupees. After 20 percent discount and 18 percent GST, what is the final price?",
         "options": ["472 rupees", "590 rupees", "400 rupees", "520 rupees"],
         "answer": "472 rupees"},
        {"q": "Train A at 60 kmph and Train B at 90 kmph travel towards each other from 300 km apart. When do they meet?",
         "options": ["2 hours", "2.5 hours", "3 hours", "1.5 hours"],
         "answer": "2 hours"},
        {"q": "If x percent of 80 is 16, what is x?",
         "options": ["20", "25", "30", "15"],
         "answer": "20"},
        {"q": "A can do work in 12 days, B in 15 days. Together in how many days?",
         "options": ["6.67 days", "8 days", "10 days", "5 days"],
         "answer": "6.67 days"},
        {"q": "Simple interest on 1000 rupees at 5 percent for 2 years?",
         "options": ["100 rupees", "50 rupees", "150 rupees", "200 rupees"],
         "answer": "100 rupees"}
    ],
    'Logical Reasoning': [
        {"q": "If A>B, B>C, then what is the relation between A and C?",
         "options": ["A>C", "A<C", "A=C", "Cannot determine"],
         "answer": "A>C"},
        {"q": "Complete the series: 2, 4, 8, 16, __?",
         "options": ["32", "24", "20", "30"],
         "answer": "32"},
        {"q": "If all cats are animals, all animals have tails, then?",
         "options": ["All cats have tails", "Some cats have tails", "No cats have tails", "Cannot say"],
         "answer": "All cats have tails"},
        {"q": "Find the odd one: 3, 5, 7, 9, 12",
         "options": ["12", "3", "5", "9"],
         "answer": "12"},
        {"q": "If BOOK is coded as 2-15-15-11, what is CODE coded as?",
         "options": ["3-15-4-5", "3-14-4-5", "4-15-4-5", "3-15-3-5"],
         "answer": "3-15-4-5"}
    ],
    'Grammar': [
        {"q": "Identify the error: 'Neither of the students have submitted their assignment.'",
         "options": ["'have' should be 'has'", "No error", "'their' should be 'his'", "'students' should be 'student'"],
         "answer": "'have' should be 'has'"},
        {"q": "Choose correct: 'The data ___ that climate change is real.'",
         "options": ["shows", "show", "showing", "shown"],
         "answer": "shows"},
        {"q": "Which is passive voice of: 'The cat chased the mouse'?",
         "options": ["The mouse was chased by the cat", "The mouse chased the cat", "The cat was chasing the mouse", "The cat chases the mouse"],
         "answer": "The mouse was chased by the cat"},
        {"q": "Find error: 'She don't like coffee.'",
         "options": ["'don't' should be 'doesn't'", "No error", "'like' should be 'likes'", "'coffee' is wrong"],
         "answer": "'don't' should be 'doesn't'"},
        {"q": "Correct form: 'I ___ to the store yesterday.'",
         "options": ["went", "go", "goes", "going"],
         "answer": "went"}
    ],
    'Synonyms and Antonyms': [
        {"q": "Synonym for AMELIORATE:",
         "options": ["Improve", "Deteriorate", "Stagnate", "Complicate"],
         "answer": "Improve"},
        {"q": "Antonym for VERBOSE:",
         "options": ["Concise", "Wordy", "Elaborate", "Detailed"],
         "answer": "Concise"},
        {"q": "Synonym for ABUNDANT:",
         "options": ["Plentiful", "Scarce", "Limited", "Rare"],
         "answer": "Plentiful"},
        {"q": "Antonym for ARTIFICIAL:",
         "options": ["Natural", "Fake", "Synthetic", "Man-made"],
         "answer": "Natural"},
        {"q": "Synonym for BENEVOLENT:",
         "options": ["Kind", "Cruel", "Harsh", "Mean"],
         "answer": "Kind"}
    ]
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

    total_score     = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    attempt_count   = len(relevant_scores)

    if total_questions == 0:
        return "beginner"

    percent = (total_score / total_questions) * 100

    recent_scores    = relevant_scores[-3:] if len(relevant_scores) >= 3 else relevant_scores
    recent_total     = sum(s['score'] for s in recent_scores)
    recent_questions = sum(s['total_questions'] for s in recent_scores)
    recent_percent   = (recent_total / recent_questions * 100) if recent_questions > 0 else 0

    print(f"   📊 Performance: {percent:.1f}% overall | {recent_percent:.1f}% recent | {attempt_count} attempts")

    if percent < 40:
        return "beginner"
    elif 40 <= percent < 70:
        if attempt_count >= 2 and recent_percent >= 55:
            return "intermediate"
        return "beginner"
    elif 70 <= percent < 85:
        if attempt_count >= 3 and recent_percent >= 75:
            return "advanced"
        return "intermediate"
    else:
        return "advanced"


def clean_cache():
    global question_cache
    if len(question_cache) > MAX_CACHE_SIZE:
        items = list(question_cache.items())
        question_cache = dict(items[int(len(items) * 0.2):])


# ============================================================================
# AI GENERATION  ←  ONLY CHANGE: added ai_context='' parameter + prompt update
# ============================================================================

def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=20,
                                progress_callback=None, ai_context=''):
    """
    Generate questions with Gemini.
    ai_context: optional placement-specific description that tells the AI
                exactly what concept to test (e.g. 'upstream downstream problems,
                speed of boat in still water, speed of current').
                When provided, the prompt includes a STRICT INSTRUCTION so the
                AI never generates off-topic questions.
    """
    global current_key_index, key_usage, question_cache

    if not GENAI_AVAILABLE or not API_KEYS:
        return None

    if progress_callback:
        progress_callback(10, f"Starting AI generation for {topic}...")

    try:
        print(f"🤖 AI Generation: {topic}/{subtopic} ({difficulty})...")

        models_to_try = [
            'gemini-2.5-pro',
            'gemini-2.5-flash',
            'gemini-2.0-flash-001',
            'gemini-2.0-flash-lite-001',
            'gemini-2.0-flash-lite',
            'gemini-flash-latest',
            'gemini-flash-lite-latest',
            'gemini-pro-latest',
            'gemini-2.5-flash-lite',
            'gemini-2.5-flash-image',
            'gemini-2.5-flash-lite-preview-09-2025',
            'gemini-3-pro-preview',
            'gemini-3-flash-preview',
            'gemini-3.1-pro-preview',
            'gemini-3.1-pro-preview-customtools',
            'gemini-3.1-flash-lite-preview',
            'gemini-3-pro-image-preview',
            'gemini-3.1-flash-image-preview',
            'gemini-2.5-flash-preview-tts',
            'gemini-2.5-pro-preview-tts',
            'gemma-3-1b-it',
            'gemma-3-4b-it',
            'gemma-3-12b-it',
            'gemma-3-27b-it',
            'gemma-3n-e4b-it',
            'gemma-3n-e2b-it',
            'nano-banana-pro-preview',
            'gemini-2.5-computer-use-preview-10-2025',
            'gemini-robotics-er-1.5-preview',
            'deep-research-pro-preview-12-2025',
        ]
        random.shuffle(models_to_try)

        difficulty_guidelines = {
            'beginner':     "Focus on basic concepts and definitions. 70% accuracy expected.",
            'intermediate': "Multi-step problems requiring analysis. 50% accuracy expected.",
            'advanced':     "Complex scenarios, edge cases, optimization. 30% accuracy expected."
        }

        # ── Build placement context lines ────────────────────────────────
        if ai_context:
            placement_context_lines = f"""PLACEMENT CONTEXT: {ai_context}

STRICT INSTRUCTION: Every single question MUST test the concept described in
PLACEMENT CONTEXT above. Do NOT generate questions about the literal or
everyday meaning of any word in the topic/subtopic name. For example, if the
context says "upstream downstream problems, speed of current", generate ONLY
aptitude math problems about boats and streams — never questions about physical
boats, ships, or nautical topics."""
        else:
            placement_context_lines = (
                f"PLACEMENT CONTEXT: Generate questions about {subtopic or topic} "
                f"as tested in engineering placement exams and technical interviews."
            )
        # ─────────────────────────────────────────────────────────────────

        seed_phrases = [
            "Focus on practical applications",
            "Include real-world scenarios",
            "Emphasize problem-solving",
            "Test conceptual understanding",
            "Include edge cases and tricky scenarios"
        ]

        for idx, model_name in enumerate(models_to_try):
            if progress_callback:
                progress = 20 + (idx * 60 // len(models_to_try))
                progress_callback(progress, f"Trying model {idx+1}/{len(models_to_try)}...")

            key_idx = random.randint(0, len(API_KEYS) - 1)

            try:
                genai.configure(api_key=API_KEYS[key_idx])
                print(f"   🔑 Key {key_idx + 1}/{len(API_KEYS)} | Model: {model_name[:30]}")
                model = genai.GenerativeModel(model_name)

                random_seed = random.choice(seed_phrases)

                prompt = f"""Generate {num_questions} UNIQUE multiple-choice questions for BTech/Engineering students.
{random_seed}. IMPORTANT: Generate FRESH questions, avoid common textbook examples.

TOPIC: {topic}
SUBTOPIC: {subtopic if subtopic else 'General'}
DIFFICULTY: {difficulty.upper()}
{difficulty_guidelines.get(difficulty, '')}

{placement_context_lines}

UNIQUENESS REQUIREMENT:
- Create NEW scenarios and contexts
- Use DIFFERENT numerical values/names/variables each time
- Vary question phrasing and approach
- DO NOT use standard textbook examples

CRITICAL REQUIREMENTS:
1. UNIQUENESS: Each question must be distinctly different
2. QUALITY STANDARDS:
   - For programming: Include code snippets, ask about output/behavior
   - For theory: Scenario-based, not just "What is X?" definitions
   - Test UNDERSTANDING and APPLICATION, not memorization

3. OPTIONS QUALITY:
   - Exactly 4 options per question
   - All options must be plausible and relevant
   - Include common misconceptions as distractors
   - NO obviously wrong options like "None of these" or random values

4. ANSWER FORMAT - CRITICAL FOR SCORING:
   - The "answer" field must EXACTLY match one of the options (word-for-word)
   - Use simple, short answers when possible
   - Avoid special characters, extra spaces, or punctuation in answers

5. OUTPUT FORMAT - Return ONLY valid JSON array:
[
  {{
    "q": "A boat travels 20 km upstream in 4 hours and 20 km downstream in 2 hours. What is the speed of the current?",
    "options": ["2.5 kmph", "5 kmph", "3 kmph", "4 kmph"],
    "answer": "2.5 kmph"
  }}
]

IMPORTANT: The answer must be a simple string that exactly matches one option.

CRITICAL JSON RULES:
- Output ONLY the JSON array, no markdown, no backticks, no explanation
- Every string value must use double quotes
- Every object must have exactly: "q", "options" (array of 4), "answer"
- No trailing commas anywhere
- The entire output must be parseable by Python's json.loads()

Generate {num_questions} questions now:"""
                key_usage[key_idx]['calls'] += 1

                if progress_callback:
                    progress_callback(progress + 10, "Generating questions...")

                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.85,
                        max_output_tokens=8192,   # ← doubled
                        top_p=0.95,
                        top_k=40
                    ),
                    request_options={'timeout': 30}
                )

                if progress_callback:
                    progress_callback(85, "Processing response...")

                raw = response.text.strip()

                if '```json' in raw:
                    raw = raw.split('```json')[1].split('```')[0].strip()
                elif '```' in raw:
                    raw = raw.split('```')[1].split('```')[0].strip()

                if '[' in raw and ']' in raw:
                    start = raw.find('[')
                    end   = raw.rfind(']') + 1
                    raw   = raw[start:end]

                import re
                raw = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
                raw = raw.replace('\u201c', '"').replace('\u201d', '"').replace('\u2019', "'")

                data = None
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError:
                # Strategy 1: truncate at last complete object and close the array
                    try:
                        last_brace = raw.rfind('},')
                        if last_brace == -1:
                            last_brace = raw.rfind('}')
                        if last_brace != -1:
                            truncated = raw[:last_brace + 1] + ']'
                            # ensure it starts with [
                            start = truncated.find('[')
                        if start != -1:
                            truncated = truncated[start:]
                        data = json.loads(truncated)
                        print(f"   ✅ Repaired by truncation: {len(data)} questions")
                    except Exception:
                        pass

                # Strategy 2: regex extraction of individual objects
                if not data:
                    try:
                        pattern = r'\{\s*"q"\s*:[^{}]+?"options"\s*:\s*\[[^\[\]]+?\]\s*,\s*"answer"\s*:\s*"[^"]+"\s*\}'
                        matches = re.findall(pattern, raw, re.DOTALL)
                        valid_objects = []
                        for match in matches:
                            try:
                                obj = json.loads(match)
                                if all(k in obj for k in ['q', 'options', 'answer']):
                                    valid_objects.append(obj)
                            except Exception:
                                continue
                        if valid_objects:
                            data = valid_objects
                            print(f"   ✅ Repaired by regex: {len(data)} questions")
                    except Exception as e:
                        print(f"   Repair failed: {str(e)[:50]}")

                if isinstance(data, list) and len(data) > 0:
                    valid = []
                    for item in data:
                        if not all(k in item for k in ['q', 'options', 'answer']):
                            continue
                        if not isinstance(item['options'], list) or len(item['options']) != 4:
                            continue

                        answer  = str(item['answer']).strip()
                        options = [str(opt).strip() for opt in item['options']]
                        answer_lower = answer.lower()

                        if not any(answer_lower == opt.lower() for opt in options):
                            print(f"   ⚠️ Answer mismatch: '{answer}' not in {options}")
                            for opt in options:
                                if answer_lower in opt.lower() or opt.lower() in answer_lower:
                                    item['answer'] = opt
                                    print(f"   ✅ Fixed answer to: '{opt}'")
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
                        if progress_callback:
                            progress_callback(100, "Questions generated successfully!")
                        print(f"✅ Generated {len(result)} questions using {model_name}")
                        return result

                    # NEW: if we got some valid questions, try a second smaller call to top up
                    elif len(valid) >= 3:
                        still_needed = num_questions - len(valid)
                        print(f"   🔄 Got {len(valid)}, requesting {still_needed} more...")
                        try:
                            # reduce prompt size for top-up call
                            top_up_prompt = prompt.replace(
                                f"Generate {num_questions} UNIQUE",
                                f"Generate {still_needed} UNIQUE"
                            ).replace(f"Generate {num_questions} questions now:", 
                                f"Generate {still_needed} questions now:")
                            top_up_response = model.generate_content(
                                top_up_prompt,
                                generation_config=genai.types.GenerationConfig(
                                    temperature=0.9,
                                    max_output_tokens=4096,
                                ),
                                request_options={'timeout': 30}
                            )
                            # reuse same parse logic inline
                            raw2 = top_up_response.text.strip()
                            if '```json' in raw2:
                                raw2 = raw2.split('```json')[1].split('```')[0].strip()
                            elif '```' in raw2:
                                raw2 = raw2.split('```')[1].split('```')[0].strip()
                            s, e = raw2.find('['), raw2.rfind(']') + 1
                            if s != -1 and e > s:
                                raw2 = raw2[s:e]
                            extra = json.loads(raw2)
                            for item in extra:
                                if all(k in item for k in ['q', 'options', 'answer']) and len(item['options']) == 4:
                                    valid.append(item)
                                    if len(valid) >= num_questions:
                                        break
                            print(f"   ✅ After top-up: {len(valid)} total questions")
                        except Exception as topup_err:
                            print(f"   ⚠️ Top-up failed: {str(topup_err)[:60]}")

                        if len(valid) >= num_questions * 0.6:
                            result = valid[:num_questions]
                            if progress_callback:
                                progress_callback(100, "Questions generated successfully!")
                            return result
                        else:
                            print(f"⚠️  Only {len(valid)}/{num_questions} valid after top-up, trying next model...")
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parse error with {model_name}: {str(e)[:50]}")
                continue

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
# PUBLIC API  ←  ONLY CHANGE: added ai_context='' parameter, passed through
# ============================================================================

def generate_questions(user_email, topic, subtopic, user_scores, num_questions=20,
                       progress_callback=None, ai_context=''):
    """
    Main entry point for question generation.
    ai_context: optional context string from smart_topic_resolver.
    """
    topic    = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    difficulty = determine_difficulty_level(user_scores, topic, subtopic)

    print(f"\n{'='*80}")
    print(f"🎯 QUESTION GENERATION REQUEST")
    print(f"   Topic: {topic} / {subtopic if subtopic else 'General'}")
    print(f"   Difficulty: {difficulty.upper()}")
    print(f"   Count: {num_questions}")
    if ai_context:
        print(f"   Context: {ai_context[:80]}…")
    time_minutes = int(num_questions * 1.5)
    print(f"   Questions: {num_questions} | Time: {time_minutes} minutes")
    print(f"{'='*80}")

    # ── Try AI generation ────────────────────────────────────────────────
    ai_questions = generate_questions_with_ai(
        topic, subtopic, difficulty, num_questions,
        progress_callback, ai_context          # pass context through
    )

    if ai_questions and len(ai_questions) >= num_questions:
        print(f"✅ Successfully generated {len(ai_questions)} AI questions")
        return ai_questions[:num_questions], difficulty

    # ── Fallback ─────────────────────────────────────────────────────────
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
    return {'questions': questions, 'difficulty': difficulty}


def generate_quiz_questions(topic, context, difficulty, num_questions=40):
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
    print("\n" + "="*80)
    print("🎓 CAREERLENS AI QUESTION GENERATOR - v4.0 (Smart Context)")
    print("="*80)
    if GENAI_AVAILABLE and API_KEYS:
        print(f"✅ AI Mode: ACTIVE")
        print(f"   - API Keys: {len(API_KEYS)} configured")
        print(f"   - Smart context injection: ENABLED")
    else:
        print("📚 Fallback Mode: ACTIVE (using static questions)")
    print("="*80 + "\n")

print_startup_info()