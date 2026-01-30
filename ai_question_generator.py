# ai_question_generator.py - OPTIMIZED VERSION
# Combines best features from both versions with improved reliability

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
for i in range(1, 10):  # Load 10 keys
    key = os.getenv(f"GEMINI_API_KEY_{i}")
    if key and key.strip():
        API_KEYS.append(key.strip())

print(f"✅ Loaded {len(API_KEYS)} API keys")

# Track quota for each key
key_usage = {i: {'calls': 0, 'reset_time': datetime.now(), 'failed': False} for i in range(len(API_KEYS))}
current_key_index = 0
MAX_CALLS_PER_MINUTE = 20  # Conservative limit (stay under 15/min)
QUOTA_RESET_SECONDS = 65   # Slightly longer reset to avoid edge cases

# Question cache to reduce API calls
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
            {"q": "Which joins returns all rows from both tables?", 
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
            {"q": "What is deadlock?", 
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
        {"q": "A product costs ₹500. After 20% discount and 18% GST, what is the final price?", 
         "options": ["₹472", "₹590", "₹400", "₹520"], 
         "answer": "₹472"},
        {"q": "Train A (60 km/h) and Train B (90 km/h) travel towards each other from 300 km apart. When do they meet?", 
         "options": ["2 hours", "2.5 hours", "3 hours", "1.5 hours"], 
         "answer": "2 hours"},
        {"q": "If x% of 80 is 16, what is x?", 
         "options": ["20", "25", "30", "15"], 
         "answer": "20"},
        {"q": "A can do work in 12 days, B in 15 days. Together in how many days?", 
         "options": ["6.67 days", "8 days", "10 days", "5 days"], 
         "answer": "6.67 days"},
        {"q": "Simple interest on ₹1000 at 5% for 2 years?", 
         "options": ["₹100", "₹50", "₹150", "₹200"], 
         "answer": "₹100"}
    ],
    'Logical Reasoning': [
        {"q": "If A>B, B>C, then?", 
         "options": ["A>C", "A<C", "A=C", "Cannot determine"], 
         "answer": "A>C"},
        {"q": "Complete: 2, 4, 8, 16, __?", 
         "options": ["32", "24", "20", "30"], 
         "answer": "32"},
        {"q": "If all cats are animals, all animals have tails, then?", 
         "options": ["All cats have tails", "Some cats have tails", "No cats have tails", "Cannot say"], 
         "answer": "All cats have tails"},
        {"q": "Find odd one: 3, 5, 7, 9, 12", 
         "options": ["12", "3", "5", "9"], 
         "answer": "12"},
        {"q": "If BOOK is coded as 2151511, what is CODE?", 
         "options": ["31545", "315145", "3154", "Cannot determine"], 
         "answer": "31545"}
    ],
    'Grammar': [
        {"q": "Identify the error: 'Neither of the students have submitted their assignment.'", 
         "options": ["'have' should be 'has'", "No error", "'their' should be 'his'", "'students' should be 'student'"], 
         "answer": "'have' should be 'has'"},
        {"q": "Choose correct: 'The data ___ that climate change is real.'", 
         "options": ["shows", "show", "showing", "shown"], 
         "answer": "shows"},
        {"q": "Which is passive voice: 'The cat chased the mouse'?", 
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
    
    # Try to get from specific topic/subtopic
    if topic in FALLBACK_QUESTIONS:
        if isinstance(FALLBACK_QUESTIONS[topic], dict) and subtopic in FALLBACK_QUESTIONS[topic]:
            pool = FALLBACK_QUESTIONS[topic][subtopic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
        elif isinstance(FALLBACK_QUESTIONS[topic], list):
            pool = FALLBACK_QUESTIONS[topic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
    
    # Fill remaining with generic fallback
    while len(questions) < num_questions:
        default_pool = GENERIC_FALLBACK[:]
        random.shuffle(default_pool)
        questions.extend(default_pool[:num_questions - len(questions)])
    
    # Shuffle options for each question
    for q in questions:
        opts = q['options'][:]
        random.shuffle(opts)
        q['options'] = opts
    
    return questions[:num_questions]

def determine_difficulty_level(user_scores, topic, subtopic):
    """Adaptive difficulty based on user performance"""
    if not user_scores:
        return "beginner"
    
    # Filter scores for THIS specific topic/subtopic
    relevant_scores = [
        s for s in user_scores 
        if s['topic'] == topic and (not subtopic or s.get('subtopic', '') == subtopic)
    ]
    
    if not relevant_scores:
        return "beginner"
    
    # Calculate performance metrics
    total_score = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    attempt_count = len(relevant_scores)
    
    if total_questions == 0:
        return "beginner"
    
    percent = (total_score / total_questions) * 100
    
    # Get recent performance (last 3 attempts)
    recent_scores = relevant_scores[-3:] if len(relevant_scores) >= 3 else relevant_scores
    recent_total = sum(s['score'] for s in recent_scores)
    recent_questions = sum(s['total_questions'] for s in recent_scores)
    recent_percent = (recent_total / recent_questions * 100) if recent_questions > 0 else 0
    
    print(f"   📊 Performance: {percent:.1f}% overall | {recent_percent:.1f}% recent | {attempt_count} attempts")
    
    # Progressive difficulty rules
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
    """Remove old entries from cache"""
    global question_cache
    if len(question_cache) > MAX_CACHE_SIZE:
        # Remove oldest 20% of entries
        items = list(question_cache.items())
        question_cache = dict(items[int(len(items) * 0.2):])

# ============================================================================
# AI GENERATION WITH CORRECT MODEL NAMES & ROBUST ERROR HANDLING
# ============================================================================
def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=20):
    """Generate questions with proper Gemini models and error handling"""
    global current_key_index, key_usage, question_cache
    
    if not GENAI_AVAILABLE or not API_KEYS:
        return None
    
    # DON'T cache - we want fresh questions each time
    # Only cache if explicitly requested for performance
    
    try:
        print(f"🤖 AI Generation: {topic}/{subtopic} ({difficulty})...")
        
        # Randomize model order to distribute load
        import random
        models_to_try = [
            'gemini-2.0-flash-001',
            'gemini-2.0-flash-lite-001',
            'gemini-flash-latest',
            'gemini-flash-lite-latest',
            'gemini-pro-latest',
        ]
        random.shuffle(models_to_try)  # Different order each time
        # ✅ CORRECT Gemini model names (verified Jan 2025)
        models_to_try = [
            'gemini-flash-latest',
            'gemini-flash-lite-latest',
            'gemini-pro-latest',
            'gemini-2.0-flash-001',
            'gemini-2.0-flash-lite-001',
            'gemini-2.5-flash',
            'gemini-2.5-flash-lite',
            'gemini-2.5-pro',
            'gemini-exp-1206',
            'gemini-3-flash-preview',
            'gemini-2.0-flash',
            'gemini-2.5-flash-image',
            'gemma-3-27b-it',
            'gemma-3-12b-it',
            'gemma-3-4b-it',
            'gemini-2.5-flash-preview-09-2025',
            'gemini-3-pro-preview',
            'gemini-robotics-er-1.5-preview',
            'deep-research-pro-preview-12-2025',
            'gemini-2.5-computer-use-preview-10-2025',
        ]

        # Randomize order each time
        import random
        random.shuffle(models_to_try)
        
        # Enhanced prompt engineering
        difficulty_guidelines = {
            'beginner': "Focus on basic concepts and definitions. 70% accuracy expected.",
            'intermediate': "Multi-step problems requiring analysis. 50% accuracy expected.",
            'advanced': "Complex scenarios, edge cases, optimization. 30% accuracy expected."
        }
        
        for model_name in models_to_try:
        # Pick random key for this model
            key_idx = random.randint(0, len(API_KEYS) - 1)
    
            try:
                # Configure with selected key
                genai.configure(api_key=API_KEYS[key_idx])
        
                print(f"   🔑 Key {key_idx + 1}/{len(API_KEYS)} | Model: {model_name[:30]}")
        
                model = genai.GenerativeModel(model_name)
                
                # Add randomization seed to prompt for variety
                seed_phrases = [
                    "Focus on practical applications",
                    "Include real-world scenarios", 
                    "Emphasize problem-solving",
                    "Test conceptual understanding",
                    "Include edge cases and tricky scenarios"
                ]
                random_seed = random.choice(seed_phrases)
                
                # Construct detailed prompt
                prompt = f"""Generate {num_questions} UNIQUE multiple-choice questions for BTech/Engineering students.
{random_seed}. IMPORTANT: Generate FRESH questions, avoid common textbook examples.

TOPIC: {topic}
SUBTOPIC: {subtopic if subtopic else 'General'}
DIFFICULTY: {difficulty.upper()}
{difficulty_guidelines.get(difficulty, '')}

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
   
4. DIFFICULTY CALIBRATION:
   - BEGINNER: Core concepts, straightforward application
   - INTERMEDIATE: Multi-step reasoning, combining concepts
   - ADVANCED: Edge cases, optimization, complex scenarios

5. OUTPUT FORMAT - Return ONLY valid JSON array (no markdown, no explanations):
   CRITICAL JSON RULES:
   - Use plain text only in questions (no code symbols like %, ", \)
   - For math: write "percent" not "%", "dollars" not "$"
   - NO line breaks inside strings
   - Example:
[
  {{"q": "If 20 percent of x equals 50, what is x?", "options": ["250", "200", "100", "500"], "answer": "250"}}
]

VALIDATION:
- "answer" must EXACTLY match one option (case-sensitive)
- Question length: minimum 20 characters
- Avoid repetitive phrasing

Generate {num_questions} questions now:"""

                # Increment usage BEFORE call
                key_usage[key_idx]['calls'] += 1
                # Make API call with timeout
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.85,  # Balance creativity vs stability
                        max_output_tokens=4096,
                        top_p=0.95,
                        top_k=40
                    ),
                    request_options={'timeout': 30}
                )
                
                # Clean and parse response with aggressive repair
                raw = response.text.strip()
                
                # Remove markdown
                if '```json' in raw:
                    raw = raw.split('```json')[1].split('```')[0].strip()
                elif '```' in raw:
                    raw = raw.split('```')[1].split('```')[0].strip()
                
                # Extract JSON array
                if '[' in raw and ']' in raw:
                    start = raw.find('[')
                    end = raw.rfind(']') + 1
                    raw = raw[start:end]
                
                # Aggressive cleaning
                import re
                # Remove control characters
                raw = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
                # Normalize quotes
                raw = raw.replace('"', '"').replace('"', '"').replace("'", "'")
                
                # Try parsing
                data = None
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError as e:
                    print(f"   JSON error: {str(e)[:80]}")
                    
                    # Aggressive repair: extract valid question objects
                    try:
                        # More flexible pattern - allows newlines, varied spacing
                        pattern = r'\{[^{}]*"q"[^{}]*"options"[^{}]*"answer"[^{}]*\}'
                        matches = re.findall(pattern, raw, re.DOTALL)
                        
                        if matches:
                            # Try to parse each match
                            valid_objects = []
                            for match in matches:
                                try:
                                    obj = json.loads(match)
                                    if all(k in obj for k in ['q', 'options', 'answer']):
                                        valid_objects.append(obj)
                                except:
                                    continue
                            
                            if valid_objects:
                                data = valid_objects
                                print(f"   ✅ Repaired: extracted {len(data)} valid questions")
                    except Exception as repair_error:
                        print(f"   Repair failed: {str(repair_error)[:50]}")
                
                if not data:
                    raise json.JSONDecodeError("Could not parse JSON", raw, 0)
                
                # Validate questions
                if isinstance(data, list) and len(data) > 0:
                    valid = []
                    for item in data:
                        # Check all required fields
                        if not all(k in item for k in ['q', 'options', 'answer']):
                            continue
                        
                        # Validate structure
                        if not isinstance(item['options'], list) or len(item['options']) != 4:
                            continue
                        
                        # Validate answer matches an option
                        if item['answer'] not in item['options']:
                            continue
                        
                        # Validate question length
                        if len(item['q']) < 20:
                            continue
                        
                        valid.append(item)
                    
                    # Success if we got at least 60% of requested questions
                    if len(valid) >= num_questions * 0.6:
                        result = valid[:num_questions]
                        
                        # Don't cache - we want fresh questions each attempt
                        
                        print(f"✅ Generated {len(result)} questions using {model_name}")
                        return result
                    else:
                        print(f"⚠️  Only {len(valid)}/{num_questions} valid questions, trying next model...")
                
            except json.JSONDecodeError as e:
                print(f"⚠️  JSON parse error with {model_name}: {str(e)[:50]}")
                continue
                
            except Exception as model_error:
                error_msg = str(model_error)
                
                # Handle quota errors
                if '429' in error_msg or 'quota' in error_msg.lower() or 'Resource has been exhausted' in error_msg:
                    print(f"⚠️  Key {key_idx + 1} quota exhausted")
                    key_usage[key_idx]['calls'] = MAX_CALLS_PER_MINUTE
                    continue
                
                # Handle invalid API key
                elif 'API key not valid' in error_msg or '400' in error_msg:
                    print(f"❌ Key {key_idx + 1} invalid, marking as failed")
                    key_usage[key_idx]['failed'] = True
                    continue
                
                # Handle model errors
                elif 'models/' in error_msg or 'not found' in error_msg:
                    print(f"⚠️  {model_name} not available, trying next...")
                    continue
                
                else:
                    print(f"⚠️  {model_name} error: {error_msg[:80]}")
                    continue
        
        print(f"❌ All AI generation attempts failed")
        return None
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)[:100]}")
        return None

# ============================================================================
# PUBLIC API
# ============================================================================
def generate_questions(user_email, topic, subtopic, user_scores, num_questions=20):
    """
    Main entry point for question generation
    
    Args:
        user_email: User identifier
        topic: Main topic (e.g., 'C', 'Java', 'Python')
        subtopic: Subtopic (e.g., 'Arrays', 'OOPs')
        user_scores: List of previous score records
        num_questions: Number of questions to generate (default: 20)
    
    Returns:
        Tuple of (questions_list, difficulty_level)
    """
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    difficulty = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 QUESTION GENERATION REQUEST")
    print(f"   Topic: {topic} / {subtopic if subtopic else 'General'}")
    print(f"   Difficulty: {difficulty.upper()}")
    print(f"   Count: {num_questions}")
    # Time: 1.5 min per question (20 ques = 30 min, 40 ques = 60 min)
    time_minutes = int(num_questions * 1.5)
    print(f"   Questions: {num_questions} | Time: {time_minutes} minutes")
    print(f"{'='*80}")
    
    # Try AI generation first
    ai_questions = generate_questions_with_ai(topic, subtopic, difficulty, num_questions)
    
    if ai_questions and len(ai_questions) >= num_questions:
        print(f"✅ Successfully generated {len(ai_questions)} AI questions")
        return ai_questions[:num_questions], difficulty
    
    # Fallback to static questions
    print(f"📚 Using fallback questions (AI generation failed or incomplete)")
    fallback = get_fallback_questions(topic, subtopic, num_questions)
    print(f"✅ Loaded {len(fallback)} fallback questions")
    
    return fallback, difficulty

def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=20):
    """
    Wrapper for backward compatibility - returns dict format
    
    Returns:
        Dict with 'questions' and 'difficulty' keys
    """
    questions, difficulty = generate_questions(user_email, topic, subtopic, user_scores, num_questions)
    return {
        'questions': questions,
        'difficulty': difficulty
    }

def generate_quiz_questions(topic, context, difficulty, num_questions=0):
    """
    For grand test / general quiz generation without user history
    
    Args:
        topic: Topic name
        context: Additional context (not currently used)
        difficulty: Explicit difficulty level
        num_questions: Number of questions
    
    Returns:
        List of questions
    """
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
    print("🎓 CAREERLENS AI QUESTION GENERATOR - OPTIMIZED v2.0")
    print("="*80)
    
    if GENAI_AVAILABLE and API_KEYS:
        print(f"✅ AI Mode: ACTIVE")
        print(f"   - API Keys: {len(API_KEYS)} configured")
        print(f"   - Rate Limit: {MAX_CALLS_PER_MINUTE} calls/minute per key")
        print(f"   - Models: gemini-1.5-flash-latest (primary)")
        print(f"   - Cache: Enabled (max {MAX_CACHE_SIZE} entries)")
    else:
        if not GENAI_AVAILABLE:
            print("⚠️  GenAI library not available")
            print("   Install: pip install google-generativeai")
        if not API_KEYS:
            print("⚠️  No API keys configured")
            print("   Set: GEMINI_API_KEY or GEMINI_API_KEY_1/2/3/4/5 in .env")
        print("📚 Fallback Mode: ACTIVE (using static questions)")
    
    print(f"\n📊 Quiz Configurations:")
    print(f"   - Normal Quiz: 20 questions / 30 minutes")
    print(f"   - Grand Test: 40 questions / 60 minutes")
    print(f"   - Adaptive difficulty based on performance")
    print("="*80 + "\n")# ai_question_generator.py - FIXED VERSION with Progress Updates & Correct Scoring
# Fixes: 1) Score evaluation issues, 2) Real-time progress feedback

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
for i in range(1, 10):  # Load 10 keys
    key = os.getenv(f"GEMINI_API_KEY_{i}")
    if key and key.strip():
        API_KEYS.append(key.strip())

print(f"✅ Loaded {len(API_KEYS)} API keys")

# Track quota for each key
key_usage = {i: {'calls': 0, 'reset_time': datetime.now(), 'failed': False} for i in range(len(API_KEYS))}
current_key_index = 0
MAX_CALLS_PER_MINUTE = 20
QUOTA_RESET_SECONDS = 65

# Question cache to reduce API calls
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
    },
    'Java': {
        'OOPs': [
            {"q": "What is runtime polymorphism demonstrated by: Parent p = new Child(); p.display();?", 
             "options": ["Method overriding", "Method overloading", "Encapsulation", "Abstraction"], 
             "answer": "Method overriding"},
            {"q": "If class A has private int x, can class B (extends A) access x?", 
             "options": ["No, private members are not inherited", "Yes, through inheritance", "Yes, using super.x", "Only if B is in same package"], 
             "answer": "No, private members are not inherited"},
        ],
    },
    'Python': {
        'Lists': [
            {"q": "What is the output of: L=[1,2,3]; print(L[::-1])?", 
             "options": ["[3, 2, 1]", "[1, 2, 3]", "Error", "None"], 
             "answer": "[3, 2, 1]"},
        ],
    },
    'Quantitative Aptitude': [
        {"q": "A product costs ₹500. After 20% discount and 18% GST, what is the final price?", 
         "options": ["₹472", "₹590", "₹400", "₹520"], 
         "answer": "₹472"},
    ],
    'Logical Reasoning': [
        {"q": "If A>B, B>C, then?", 
         "options": ["A>C", "A<C", "A=C", "Cannot determine"], 
         "answer": "A>C"},
    ],
    'Grammar': [
        {"q": "Identify the error: 'Neither of the students have submitted their assignment.'", 
         "options": ["'have' should be 'has'", "No error", "'their' should be 'his'", "'students' should be 'student'"], 
         "answer": "'have' should be 'has'"},
    ],
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
    
    # Try to get from specific topic/subtopic
    if topic in FALLBACK_QUESTIONS:
        if isinstance(FALLBACK_QUESTIONS[topic], dict) and subtopic in FALLBACK_QUESTIONS[topic]:
            pool = FALLBACK_QUESTIONS[topic][subtopic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
        elif isinstance(FALLBACK_QUESTIONS[topic], list):
            pool = FALLBACK_QUESTIONS[topic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
    
    # Fill remaining with generic fallback
    while len(questions) < num_questions:
        default_pool = GENERIC_FALLBACK[:]
        random.shuffle(default_pool)
        questions.extend(default_pool[:num_questions - len(questions)])
    
    # Shuffle options for each question
    for q in questions:
        opts = q['options'][:]
        random.shuffle(opts)
        q['options'] = opts
    
    return questions[:num_questions]

def determine_difficulty_level(user_scores, topic, subtopic):
    """Adaptive difficulty based on user performance"""
    if not user_scores:
        return "beginner"
    
    # Filter scores for THIS specific topic/subtopic
    relevant_scores = [
        s for s in user_scores 
        if s['topic'] == topic and (not subtopic or s.get('subtopic', '') == subtopic)
    ]
    
    if not relevant_scores:
        return "beginner"
    
    # Calculate performance metrics
    total_score = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    attempt_count = len(relevant_scores)
    
    if total_questions == 0:
        return "beginner"
    
    percent = (total_score / total_questions) * 100
    
    print(f"   📊 Performance: {percent:.1f}% overall | {attempt_count} attempts")
    
    # Progressive difficulty rules
    if percent < 40:
        return "beginner"
    elif 40 <= percent < 70:
        return "intermediate" if attempt_count >= 2 else "beginner"
    elif 70 <= percent < 85:
        return "advanced" if attempt_count >= 3 else "intermediate"
    else:
        return "advanced"

# ============================================================================
# AI GENERATION WITH PROGRESS CALLBACK
# ============================================================================
def generate_questions_with_ai(topic, subtopic, difficulty, num_questions=20, progress_callback=None):
    """
    Generate questions with proper Gemini models and progress updates
    
    Args:
        progress_callback: Function to call with progress updates (percent, message)
    """
    global current_key_index, key_usage, question_cache
    
    if not GENAI_AVAILABLE or not API_KEYS:
        return None
    
    if progress_callback:
        progress_callback(10, f"Starting AI generation for {topic}...")
    
    try:
        print(f"🤖 AI Generation: {topic}/{subtopic} ({difficulty})...")
        
        # Randomize model order to distribute load
        models_to_try = [
            'gemini-2.0-flash-001',
            'gemini-flash-latest',
            'gemini-2.5-flash',
            'gemini-pro-latest',
        ]
        random.shuffle(models_to_try)
        
        # Enhanced prompt engineering
        difficulty_guidelines = {
            'beginner': "Focus on basic concepts and definitions. 70% accuracy expected.",
            'intermediate': "Multi-step problems requiring analysis. 50% accuracy expected.",
            'advanced': "Complex scenarios, edge cases, optimization. 30% accuracy expected."
        }
        
        for idx, model_name in enumerate(models_to_try):
            # Update progress
            if progress_callback:
                progress = 20 + (idx * 60 // len(models_to_try))
                progress_callback(progress, f"Trying model {idx+1}/{len(models_to_try)}...")
            
            # Pick random key for this model
            key_idx = random.randint(0, len(API_KEYS) - 1)
    
            try:
                # Configure with selected key
                genai.configure(api_key=API_KEYS[key_idx])
        
                print(f"   🔑 Key {key_idx + 1}/{len(API_KEYS)} | Model: {model_name[:30]}")
        
                model = genai.GenerativeModel(model_name)
                
                # Add randomization seed to prompt for variety
                seed_phrases = [
                    "Focus on practical applications",
                    "Include real-world scenarios", 
                    "Emphasize problem-solving",
                    "Test conceptual understanding",
                    "Include edge cases and tricky scenarios"
                ]
                random_seed = random.choice(seed_phrases)
                
                # Construct detailed prompt
                prompt = f"""Generate {num_questions} UNIQUE multiple-choice questions for BTech/Engineering students.
{random_seed}. IMPORTANT: Generate FRESH questions, avoid common textbook examples.

TOPIC: {topic}
SUBTOPIC: {subtopic if subtopic else 'General'}
DIFFICULTY: {difficulty.upper()}
{difficulty_guidelines.get(difficulty, '')}

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
   - Example: If option is "10", answer must be "10" (not "10 items" or "ten")

5. OUTPUT FORMAT - Return ONLY valid JSON array:
[
  {{
    "q": "What is 2 + 2?",
    "options": ["3", "4", "5", "6"],
    "answer": "4"
  }}
]

IMPORTANT: The answer must be a simple string that exactly matches one option.

Generate {num_questions} questions now:"""

                # Increment usage BEFORE call
                key_usage[key_idx]['calls'] += 1
                
                if progress_callback:
                    progress_callback(progress + 10, "Generating questions...")
                
                # Make API call with timeout
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.85,
                        max_output_tokens=4096,
                        top_p=0.95,
                        top_k=40
                    ),
                    request_options={'timeout': 30}
                )
                
                if progress_callback:
                    progress_callback(85, "Processing response...")
                
                # Clean and parse response
                raw = response.text.strip()
                
                # Remove markdown
                if '```json' in raw:
                    raw = raw.split('```json')[1].split('```')[0].strip()
                elif '```' in raw:
                    raw = raw.split('```')[1].split('```')[0].strip()
                
                # Extract JSON array
                if '[' in raw and ']' in raw:
                    start = raw.find('[')
                    end = raw.rfind(']') + 1
                    raw = raw[start:end]
                
                # Aggressive cleaning
                import re
                raw = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw)
                raw = raw.replace('"', '"').replace('"', '"').replace("'", "'")
                
                # Try parsing
                data = None
                try:
                    data = json.loads(raw)
                except json.JSONDecodeError as e:
                    print(f"   JSON error: {str(e)[:80]}")
                    
                    # Aggressive repair
                    try:
                        pattern = r'\{[^{}]*"q"[^{}]*"options"[^{}]*"answer"[^{}]*\}'
                        matches = re.findall(pattern, raw, re.DOTALL)
                        
                        if matches:
                            valid_objects = []
                            for match in matches:
                                try:
                                    obj = json.loads(match)
                                    if all(k in obj for k in ['q', 'options', 'answer']):
                                        valid_objects.append(obj)
                                except:
                                    continue
                            
                            if valid_objects:
                                data = valid_objects
                                print(f"   ✅ Repaired: extracted {len(data)} valid questions")
                    except Exception as repair_error:
                        print(f"   Repair failed: {str(repair_error)[:50]}")
                
                if not data:
                    raise json.JSONDecodeError("Could not parse JSON", raw, 0)
                
                # Validate questions with STRICT answer checking
                if isinstance(data, list) and len(data) > 0:
                    valid = []
                    for item in data:
                        # Check all required fields
                        if not all(k in item for k in ['q', 'options', 'answer']):
                            continue
                        
                        # Validate structure
                        if not isinstance(item['options'], list) or len(item['options']) != 4:
                            continue
                        
                        # CRITICAL: Normalize answer and options for comparison
                        answer = str(item['answer']).strip()
                        options = [str(opt).strip() for opt in item['options']]
                        
                        # Check if answer matches ANY option (case-insensitive, whitespace-normalized)
                        answer_lower = answer.lower()
                        if not any(answer_lower == opt.lower() for opt in options):
                            print(f"   ⚠️ Answer mismatch: '{answer}' not in {options}")
                            # Try to fix by matching to closest option
                            for opt in options:
                                if answer_lower in opt.lower() or opt.lower() in answer_lower:
                                    item['answer'] = opt
                                    print(f"   ✅ Fixed answer to: '{opt}'")
                                    break
                            else:
                                continue  # Skip if can't fix
                        else:
                            # Set answer to exact option match
                            for opt in options:
                                if answer_lower == opt.lower():
                                    item['answer'] = opt
                                    break
                        
                        # Validate question length
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
# PUBLIC API
# ============================================================================
def generate_questions(user_email, topic, subtopic, user_scores, num_questions=20, progress_callback=None):
    """
    Main entry point for question generation
    
    Args:
        user_email: User identifier
        topic: Main topic (e.g., 'C', 'Java', 'Python')
        subtopic: Subtopic (e.g., 'Arrays', 'OOPs')
        user_scores: List of previous score records
        num_questions: Number of questions to generate (default: 20)
        progress_callback: Optional callback for progress updates
    
    Returns:
        Tuple of (questions_list, difficulty_level)
    """
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
    print("🎓 CAREERLENS AI QUESTION GENERATOR - FIXED v3.0")
    print("="*80)
    
    if GENAI_AVAILABLE and API_KEYS:
        print(f"✅ AI Mode: ACTIVE")
        print(f"   - API Keys: {len(API_KEYS)} configured")
        print(f"   - Features: Progress updates, Fixed scoring")
    else:
        print("📚 Fallback Mode: ACTIVE (using static questions)")
    
    print("="*80 + "\n")

# Run startup diagnostics
print_startup_info()

# Run startup diagnostics
print_startup_info()