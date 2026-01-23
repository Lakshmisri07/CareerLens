# ai_question_generator.py - FIXED VERSION

import os
import json
from dotenv import load_dotenv
import random
load_dotenv()

# Try to import Google GenAI (optional)
try:
    from google import genai
    from google.genai import types
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False
    print("⚠️  Google GenAI not available - using fallback questions")

# ============================================================================
# FIX #1: BETTER API KEY HANDLING
# ============================================================================
API_KEYS = []
for i in range(1, 5):
    key = os.getenv(f"GEMINI_API_KEY_{i}") or (os.getenv("GEMINI_API_KEY") if i == 1 else None)
    if key:
        API_KEYS.append(key)

current_key_index = 0
client = None

# Initialize client only if GenAI is available and we have keys
if GENAI_AVAILABLE and API_KEYS:
    try:
        client = genai.Client(api_key=API_KEYS[0])
        print(f"✓ GenAI initialized with {len(API_KEYS)} API key(s)")
    except Exception as e:
        print(f"⚠️  Could not initialize GenAI: {e}")
        client = None

# ==================== COMPREHENSIVE FALLBACK QUESTION BANK ====================

FALLBACK_QUESTIONS = {
    # PROGRAMMING LANGUAGES
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
        ],
        'Loops': [
            {"q": "Which loop is guaranteed to execute at least once?", 
             "options": ["do-while", "while", "for", "None"], 
             "answer": "do-while"},
            {"q": "What does 'break' do in a loop?", 
             "options": ["Exits the loop", "Skips iteration", "Restarts loop", "Pauses loop"], 
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
        'Functions': [
            {"q": "What is a function prototype?", 
             "options": ["Function declaration", "Function definition", "Function call", "Function pointer"], 
             "answer": "Function declaration"},
            {"q": "What does 'void' return type mean?", 
             "options": ["Returns nothing", "Returns NULL", "Returns 0", "Returns empty string"], 
             "answer": "Returns nothing"},
            {"q": "What is recursion?", 
             "options": ["Function calling itself", "Nested functions", "Function overloading", "Function pointer"], 
             "answer": "Function calling itself"},
            {"q": "What is pass by value?", 
             "options": ["Copy of value is passed", "Address is passed", "Reference is passed", "Pointer is passed"], 
             "answer": "Copy of value is passed"},
            {"q": "What is the maximum number of arguments a function can have in C?", 
             "options": ["Implementation dependent", "256", "1024", "Unlimited"], 
             "answer": "Implementation dependent"}
        ]
    },
    
    'Java': {
        'OOPs': [
            {"q": "What are the four pillars of OOP?", 
             "options": ["Encapsulation, Inheritance, Polymorphism, Abstraction", "Classes, Objects, Methods, Variables", "Public, Private, Protected, Default", "None"], 
             "answer": "Encapsulation, Inheritance, Polymorphism, Abstraction"},
            {"q": "What is encapsulation?", 
             "options": ["Data hiding using access modifiers", "Code reusability", "Method overriding", "None"], 
             "answer": "Data hiding using access modifiers"},
            {"q": "What is a class in Java?", 
             "options": ["Blueprint for objects", "Object instance", "Data type", "Method collection"], 
             "answer": "Blueprint for objects"},
            {"q": "What is an object?", 
             "options": ["Instance of a class", "Class itself", "Method", "Variable"], 
             "answer": "Instance of a class"},
            {"q": "What is abstraction?", 
             "options": ["Hiding implementation details", "Showing all details", "Data binding", "Code duplication"], 
             "answer": "Hiding implementation details"}
        ],
        'Inheritance': [
            {"q": "What is inheritance?", 
             "options": ["Acquiring properties of parent class", "Creating new class", "Method overloading", "None"], 
             "answer": "Acquiring properties of parent class"},
            {"q": "Which keyword is used for inheritance in Java?", 
             "options": ["extends", "implements", "inherits", "derives"], 
             "answer": "extends"},
            {"q": "Does Java support multiple inheritance?", 
             "options": ["No, only through interfaces", "Yes, fully", "No, never", "Yes, with classes"], 
             "answer": "No, only through interfaces"},
            {"q": "What is the superclass of all classes in Java?", 
             "options": ["Object", "Class", "Super", "Base"], 
             "answer": "Object"},
            {"q": "What is method overriding?", 
             "options": ["Redefining parent method in child", "Same name different parameters", "Private method", "Static method"], 
             "answer": "Redefining parent method in child"}
        ],
        'Exceptions': [
            {"q": "What is an exception?", 
             "options": ["Runtime error", "Compile error", "Logic error", "Warning"], 
             "answer": "Runtime error"},
            {"q": "Which keyword is used to throw an exception?", 
             "options": ["throw", "throws", "try", "catch"], 
             "answer": "throw"},
            {"q": "What is the parent class of all exceptions?", 
             "options": ["Throwable", "Exception", "Error", "RuntimeException"], 
             "answer": "Throwable"},
            {"q": "What is a checked exception?", 
             "options": ["Exception checked at compile time", "Runtime exception", "Error", "Warning"], 
             "answer": "Exception checked at compile time"},
            {"q": "What does finally block do?", 
             "options": ["Executes always", "Executes on error", "Executes on success", "Never executes"], 
             "answer": "Executes always"}
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
            {"q": "How do you access the last element of a list?", 
             "options": ["list[-1]", "list[last]", "list.last()", "list[end]"], 
             "answer": "list[-1]"},
            {"q": "What does list slicing [1:3] return?", 
             "options": ["Elements at index 1 and 2", "Elements at index 1 to 3", "Elements at index 0 to 3", "Element at index 1"], 
             "answer": "Elements at index 1 and 2"},
            {"q": "Are Python lists mutable?", 
             "options": ["Yes", "No", "Sometimes", "Depends on type"], 
             "answer": "Yes"}
        ],
        'Dictionaries': [
            {"q": "How do you create an empty dictionary?", 
             "options": ["{}", "[]", "dict()", "Both {} and dict()"], 
             "answer": "Both {} and dict()"},
            {"q": "How do you access a value in a dictionary?", 
             "options": ["dict[key]", "dict.key", "dict(key)", "dict->key"], 
             "answer": "dict[key]"},
            {"q": "What method returns all keys in a dictionary?", 
             "options": ["keys()", "getKeys()", "allKeys()", "keyList()"], 
             "answer": "keys()"},
            {"q": "What happens when accessing a non-existent key?", 
             "options": ["KeyError", "Returns None", "Returns empty string", "Creates key"], 
             "answer": "KeyError"},
            {"q": "Which method safely gets a value with default?", 
             "options": ["get()", "fetch()", "retrieve()", "safe()"], 
             "answer": "get()"}
        ]
    },
    
    'DBMS': {
        'SQL': [
            {"q": "Which SQL command retrieves data?", 
             "options": ["SELECT", "GET", "FETCH", "RETRIEVE"], 
             "answer": "SELECT"},
            {"q": "Which clause filters results?", 
             "options": ["WHERE", "FILTER", "HAVING", "IF"], 
             "answer": "WHERE"},
            {"q": "What does JOIN do?", 
             "options": ["Combines rows from tables", "Merges databases", "Deletes data", "Updates records"], 
             "answer": "Combines rows from tables"},
            {"q": "Which is NOT a SQL aggregate function?", 
             "options": ["CONCAT", "COUNT", "SUM", "AVG"], 
             "answer": "CONCAT"},
            {"q": "What does DISTINCT do?", 
             "options": ["Removes duplicates", "Sorts data", "Filters nulls", "Joins tables"], 
             "answer": "Removes duplicates"}
        ],
        'Normalization': [
            {"q": "What is normalization?", 
             "options": ["Organizing data to reduce redundancy", "Adding more tables", "Deleting data", "Backup process"], 
             "answer": "Organizing data to reduce redundancy"},
            {"q": "What is 1NF (First Normal Form)?", 
             "options": ["No repeating groups, atomic values", "No partial dependencies", "No transitive dependencies", "All of above"], 
             "answer": "No repeating groups, atomic values"},
            {"q": "What does 2NF eliminate?", 
             "options": ["Partial dependencies", "All dependencies", "Transitive dependencies", "Foreign keys"], 
             "answer": "Partial dependencies"},
            {"q": "What is a primary key?", 
             "options": ["Unique identifier", "First column", "Indexed column", "Required field"], 
             "answer": "Unique identifier"},
            {"q": "Why normalize databases?", 
             "options": ["Reduce redundancy and anomalies", "Increase speed", "Add complexity", "More storage"], 
             "answer": "Reduce redundancy and anomalies"}
        ]
    },
    
    'OS': {
        'Processes': [
            {"q": "What is a process?", 
             "options": ["Program in execution", "Compiled code", "Source code", "Algorithm"], 
             "answer": "Program in execution"},
            {"q": "What is process scheduling?", 
             "options": ["Allocating CPU to processes", "Creating processes", "Terminating processes", "None"], 
             "answer": "Allocating CPU to processes"},
            {"q": "What is a PCB?", 
             "options": ["Process Control Block", "Program Control Block", "Process Code Block", "None"], 
             "answer": "Process Control Block"},
            {"q": "What are process states?", 
             "options": ["New, Ready, Running, Waiting, Terminated", "Start, Stop, Pause", "Active, Inactive", "None"], 
             "answer": "New, Ready, Running, Waiting, Terminated"},
            {"q": "What is context switching?", 
             "options": ["Switching between processes", "Switching threads", "Changing memory", "None"], 
             "answer": "Switching between processes"}
        ]
    },
    
    'Data Structures': {
        'Linked List': [
            {"q": "What is a linked list?", 
             "options": ["Linear data structure with nodes", "Array", "Tree", "Graph"], 
             "answer": "Linear data structure with nodes"},
            {"q": "What does each node contain?", 
             "options": ["Data and pointer", "Only data", "Only pointer", "Index"], 
             "answer": "Data and pointer"},
            {"q": "What is the time complexity of insertion at beginning?", 
             "options": ["O(1)", "O(n)", "O(log n)", "O(n²)"], 
             "answer": "O(1)"},
            {"q": "What is a circular linked list?", 
             "options": ["Last node points to first", "First node points to last", "No pointers", "None"], 
             "answer": "Last node points to first"},
            {"q": "Advantage of linked list over array?", 
             "options": ["Dynamic size", "Random access", "Less memory", "Faster access"], 
             "answer": "Dynamic size"}
        ]
    },
    'Digital Electronics': {
        'Logic Gates': [
            {"q": "Which gate gives HIGH output only when all inputs are HIGH?", "options": ["AND", "OR", "NAND", "XOR"], "answer": "AND"},
            {"q": "What is the output of a NOT gate when input is 1?", "options": ["0", "1", "Undefined", "High Impedance"], "answer": "0"},
            {"q": "Which gate is called a universal gate?", "options": ["NAND", "AND", "OR", "XOR"], "answer": "NAND"},
            {"q": "XOR gate gives HIGH when inputs are:", "options": ["Different", "Same", "All HIGH", "All LOW"], "answer": "Different"},
            {"q": "De Morgan's theorem converts AND to:", "options": ["OR with inverted inputs", "NAND", "NOR", "XOR"], "answer": "OR with inverted inputs"}
        ],
        'Boolean Algebra': [
            {"q": "A + A' = ?", "options": ["1", "0", "A", "A'"], "answer": "1"},
            {"q": "A . A' = ?", "options": ["0", "1", "A", "A'"], "answer": "0"},
            {"q": "A + AB = ?", "options": ["A", "B", "AB", "A+B"], "answer": "A"},
            {"q": "A(A+B) = ?", "options": ["A", "B", "AB", "A+B"], "answer": "A"},
            {"q": "(A+B)(A+C) = ?", "options": ["A+BC", "AC+BC", "A", "ABC"], "answer": "A+BC"}
        ]
    },
    'Signal Processing': {
        'Fourier Transform': [
            {"q": "Fourier Transform converts time domain to:", "options": ["Frequency domain", "Space domain", "Z-domain", "Laplace domain"], "answer": "Frequency domain"},
            {"q": "Inverse Fourier Transform converts back to:", "options": ["Time domain", "Frequency domain", "Both", "Neither"], "answer": "Time domain"},
            {"q": "DFT stands for:", "options": ["Discrete Fourier Transform", "Digital Fourier Transform", "Direct Fourier Transform", "None"], "answer": "Discrete Fourier Transform"},
            {"q": "FFT is faster version of:", "options": ["DFT", "DTFT", "Z-Transform", "Laplace"], "answer": "DFT"},
            {"q": "Convolution in time domain equals:", "options": ["Multiplication in frequency", "Addition in frequency", "Division in frequency", "None"], "answer": "Multiplication in frequency"}
        ]
    },
    
    # EEE Topics
    'Circuit Theory': {
        'Ohms Law': [
            {"q": "Ohm's Law: V = ?", "options": ["IR", "I/R", "R/I", "I+R"], "answer": "IR"},
            {"q": "If V=10V, R=5Ω, then I=?", "options": ["2A", "5A", "50A", "0.5A"], "answer": "2A"},
            {"q": "Unit of resistance is:", "options": ["Ohm", "Ampere", "Volt", "Watt"], "answer": "Ohm"},
            {"q": "Resistance increases with:", "options": ["Length increase", "Area increase", "Both", "Neither"], "answer": "Length increase"},
            {"q": "Conductance G = ?", "options": ["1/R", "R", "IR", "V/I"], "answer": "1/R"}
        ],
        'Kirchhoff Laws': [
            {"q": "KCL states sum of currents at node:", "options": ["Zero", "Maximum", "Minimum", "Variable"], "answer": "Zero"},
            {"q": "KVL states sum of voltages in loop:", "options": ["Zero", "Maximum", "Minimum", "Variable"], "answer": "Zero"},
            {"q": "KCL is based on:", "options": ["Charge conservation", "Energy conservation", "Both", "Neither"], "answer": "Charge conservation"},
            {"q": "KVL is based on:", "options": ["Energy conservation", "Charge conservation", "Both", "Neither"], "answer": "Energy conservation"},
            {"q": "Node analysis uses:", "options": ["KCL", "KVL", "Both", "Neither"], "answer": "KCL"}
        ]
    },
    'Power Systems': {
        'Generation': [
            {"q": "Most common frequency in power systems:", "options": ["50/60 Hz", "100 Hz", "200 Hz", "25 Hz"], "answer": "50/60 Hz"},
            {"q": "Thermal power plant uses:", "options": ["Steam", "Water", "Wind", "Solar"], "answer": "Steam"},
            {"q": "Hydroelectric plant converts:", "options": ["Potential to electrical", "Kinetic to electrical", "Chemical to electrical", "None"], "answer": "Potential to electrical"},
            {"q": "Nuclear plant uses:", "options": ["Uranium/Plutonium", "Coal", "Gas", "Oil"], "answer": "Uranium/Plutonium"},
            {"q": "Renewable energy includes:", "options": ["Solar, Wind, Hydro", "Coal", "Nuclear", "Gas"], "answer": "Solar, Wind, Hydro"}
        ]
    },
    
    # MECH Topics
    'Thermodynamics': {
        'Laws': [
            {"q": "Zeroth law defines:", "options": ["Temperature", "Energy", "Entropy", "Enthalpy"], "answer": "Temperature"},
            {"q": "First law is:", "options": ["Energy conservation", "Entropy increase", "Temperature equilibrium", "None"], "answer": "Energy conservation"},
            {"q": "Second law states entropy:", "options": ["Increases", "Decreases", "Constant", "Zero"], "answer": "Increases"},
            {"q": "Carnot cycle has:", "options": ["Maximum efficiency", "Minimum efficiency", "50% efficiency", "100% efficiency"], "answer": "Maximum efficiency"},
            {"q": "Isentropic process has constant:", "options": ["Entropy", "Temperature", "Pressure", "Volume"], "answer": "Entropy"}
        ]
    },
    'Mechanics': {
        'Statics': [
            {"q": "Sum of forces in equilibrium:", "options": ["Zero", "Maximum", "Minimum", "One"], "answer": "Zero"},
            {"q": "Sum of moments in equilibrium:", "options": ["Zero", "Maximum", "Minimum", "One"], "answer": "Zero"},
            {"q": "Free body diagram shows:", "options": ["All forces", "Only reactions", "Only loads", "None"], "answer": "All forces"},
            {"q": "Moment = ?", "options": ["Force × Distance", "Force / Distance", "Force + Distance", "None"], "answer": "Force × Distance"},
            {"q": "Centre of gravity is point where:", "options": ["Weight acts", "Force acts", "Moment acts", "None"], "answer": "Weight acts"}
        ]
    },
    # MECHANICAL ENGINEERING
'Manufacturing': [
    {"q": "Which process is used to join metals permanently?", 
     "options": ["Welding", "Bolting", "Riveting", "Gluing"], 
     "answer": "Welding"},
    {"q": "Lathe machine is primarily used for:", 
     "options": ["Turning operations", "Drilling", "Milling", "Grinding"], 
     "answer": "Turning operations"},
    {"q": "What is CNC?", 
     "options": ["Computer Numerical Control", "Central Numeric Code", "Cutting New Components", "None"], 
     "answer": "Computer Numerical Control"},
    {"q": "Casting process uses:", 
     "options": ["Molten metal in mold", "Solid metal", "Plastic", "Wood"], 
     "answer": "Molten metal in mold"},
    {"q": "Which is a cutting tool material?", 
     "options": ["High Speed Steel", "Aluminum", "Copper", "Brass"], 
     "answer": "High Speed Steel"}
],

# CIVIL ENGINEERING
'Surveying': [
    {"q": "Theodolite is used to measure:", 
     "options": ["Horizontal and vertical angles", "Only distance", "Only height", "Temperature"], 
     "answer": "Horizontal and vertical angles"},
    {"q": "Benchmark in surveying indicates:", 
     "options": ["Reference point for elevation", "Starting point", "End point", "Center point"], 
     "answer": "Reference point for elevation"},
    {"q": "Contour lines join points of:", 
     "options": ["Equal elevation", "Equal distance", "Equal temperature", "Equal pressure"], 
     "answer": "Equal elevation"},
    {"q": "Leveling is done to find:", 
     "options": ["Difference in elevation", "Horizontal distance", "Angles", "Areas"], 
     "answer": "Difference in elevation"},
    {"q": "Total Station combines:", 
     "options": ["Theodolite and EDM", "Compass and level", "GPS and radar", "None"], 
     "answer": "Theodolite and EDM"}
]
,
    # CIVIL Topics
    'Structural Analysis': {
        'Beams': [
            {"q": "Simply supported beam has:", "options": ["2 supports", "1 support", "3 supports", "No support"], "answer": "2 supports"},
            {"q": "Cantilever beam is fixed at:", "options": ["One end", "Both ends", "Middle", "Nowhere"], "answer": "One end"},
            {"q": "Bending moment causes:", "options": ["Bending", "Twisting", "Shearing", "Tension"], "answer": "Bending"},
            {"q": "Shear force is:", "options": ["Transverse force", "Axial force", "Bending force", "None"], "answer": "Transverse force"},
            {"q": "Maximum bending moment in cantilever with point load at free end:", "options": ["At fixed end", "At free end", "At center", "Uniform"], "answer": "At fixed end"}
        ]
    },
    
    # CHEM Topics
    'Chemical Thermodynamics': {
        'Laws of Thermodynamics': [
            {"q": "Enthalpy H = ?", "options": ["U + PV", "U - PV", "U × PV", "U / PV"], "answer": "U + PV"},
            {"q": "Gibbs free energy determines:", "options": ["Spontaneity", "Temperature", "Pressure", "Volume"], "answer": "Spontaneity"},
            {"q": "Exothermic reaction has ΔH:", "options": ["Negative", "Positive", "Zero", "Infinite"], "answer": "Negative"},
            {"q": "Endothermic reaction absorbs:", "options": ["Heat", "Work", "Light", "Sound"], "answer": "Heat"},
            {"q": "Standard conditions: T=?", "options": ["298K", "273K", "373K", "0K"], "answer": "298K"}
        ]
    },
    # APTITUDE
    'Quantitative Aptitude': [
        {"q": "If 20% of x is 50, what is x?", 
         "options": ["250", "200", "300", "150"], 
         "answer": "250"},
        {"q": "What is 15% of 200?", 
         "options": ["30", "25", "35", "20"], 
         "answer": "30"},
        {"q": "A train travels 120 km in 2 hours. What is its speed?", 
         "options": ["60 km/h", "50 km/h", "70 km/h", "80 km/h"], 
         "answer": "60 km/h"},
        {"q": "If a:b = 2:3 and b:c = 4:5, what is a:c?", 
         "options": ["8:15", "2:5", "3:5", "4:15"], 
         "answer": "8:15"},
        {"q": "What is the compound interest on Rs.1000 at 10% for 2 years?", 
         "options": ["Rs.210", "Rs.200", "Rs.220", "Rs.190"], 
         "answer": "Rs.210"}
    ],
    
    'Logical Reasoning': [
        {"q": "If all roses are flowers and some flowers are red, can we conclude all roses are red?", 
         "options": ["No", "Yes", "Maybe", "Insufficient data"], 
         "answer": "No"},
        {"q": "Complete the series: 2, 6, 12, 20, 30, ?", 
         "options": ["42", "40", "38", "44"], 
         "answer": "42"},
        {"q": "If CODING is written as DPEJOH, how is BEST written?", 
         "options": ["CFTU", "CFST", "CGTU", "BFTU"], 
         "answer": "CFTU"},
        {"q": "A is taller than B. C is shorter than B. Who is tallest?", 
         "options": ["A", "B", "C", "Cannot determine"], 
         "answer": "A"},
        {"q": "Find the odd one: 3, 7, 11, 14, 17", 
         "options": ["14", "3", "7", "17"], 
         "answer": "14"}
    ],
    
    # ENGLISH
    'Grammar': [
        {"q": "Which is correct: 'He don't know' or 'He doesn't know'?", 
         "options": ["He doesn't know", "He don't know", "Both", "Neither"], 
         "answer": "He doesn't know"},
        {"q": "Choose the correct form: 'I have ___ apple.'", 
         "options": ["an", "a", "the", "no article"], 
         "answer": "an"},
        {"q": "What is the past tense of 'go'?", 
         "options": ["went", "goed", "gone", "going"], 
         "answer": "went"},
        {"q": "Which is a preposition?", 
         "options": ["on", "run", "quickly", "happy"], 
         "answer": "on"},
        {"q": "Identify the noun: 'The cat runs quickly.'", 
         "options": ["cat", "runs", "quickly", "the"], 
         "answer": "cat"}
    ],
    
    'Reading Comprehension': [
        {"q": "What does 'comprehension' mean?", 
         "options": ["Understanding", "Reading", "Writing", "Speaking"], 
         "answer": "Understanding"},
        {"q": "What is the main idea in a paragraph?", 
         "options": ["Central message", "First sentence", "Last sentence", "Title"], 
         "answer": "Central message"},
        {"q": "What are supporting details?", 
         "options": ["Evidence for main idea", "Introduction", "Conclusion", "Title"], 
         "answer": "Evidence for main idea"},
        {"q": "What is inference?", 
         "options": ["Logical conclusion from text", "Direct statement", "Quote", "Title"], 
         "answer": "Logical conclusion from text"},
        {"q": "What is the purpose of a summary?", 
         "options": ["Brief overview of text", "Detailed analysis", "Personal opinion", "Word-by-word copy"], 
         "answer": "Brief overview of text"}
    ]
}



# ==================== HELPER FUNCTIONS ====================

def get_fallback_questions(topic, subtopic, num_questions=5):
    """Get randomized fallback questions - NEVER repeat same questions"""
    questions = []
    
    # Try topic-subtopic
    if topic in FALLBACK_QUESTIONS:
        if isinstance(FALLBACK_QUESTIONS[topic], dict) and subtopic in FALLBACK_QUESTIONS[topic]:
            pool = FALLBACK_QUESTIONS[topic][subtopic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
        elif isinstance(FALLBACK_QUESTIONS[topic], list):
            pool = FALLBACK_QUESTIONS[topic][:]
            random.shuffle(pool)
            questions = pool[:num_questions]
    
    # If not enough, add from GENERIC pool
    if len(questions) < num_questions:
        default_pool = GENERIC_FALLBACK[:]  # <-- CHANGE THIS LINE
        random.shuffle(default_pool)
        questions.extend(default_pool[:num_questions - len(questions)])
    
    # Shuffle options
    for q in questions:
        opts = q['options'][:]
        random.shuffle(opts)
        q['options'] = opts
    
    return questions[:num_questions]
def determine_difficulty_level(user_scores, topic, subtopic):
    """Determine difficulty level based on past performance"""
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

# ==================== MAIN FUNCTIONS ====================

# ============================================================================
# FIX #2: IMPROVED AI GENERATION WITH BETTER ERROR HANDLING
# ============================================================================
def generate_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Generate adaptive quiz questions with GUARANTEED fallback
    Returns: questions (list), difficulty (str)
    """
    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""
    
    # Determine difficulty
    difficulty = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 GENERATING QUESTIONS")
    print(f"Topic: {topic} | Subtopic: {subtopic} | Difficulty: {difficulty}")
    print(f"API Keys Available: {len(API_KEYS)}")
    print(f"GenAI Available: {GENAI_AVAILABLE}")
    print(f"Client Initialized: {client is not None}")
    print(f"{'='*80}")
    
    # Try AI generation ONLY if client exists
    if client and GENAI_AVAILABLE and API_KEYS:
        try:
            print("🤖 Attempting AI question generation...")
            
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

            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    max_output_tokens=2048,
                    temperature=0.7
                )
            )

            raw = response.text.strip()
            print(f"✓ Received AI response ({len(raw)} chars)")
            
            # Clean response
            if '```json' in raw:
                raw = raw.split('```json')[1].split('```')[0].strip()
            elif '```' in raw:
                raw = raw.split('```')[1].split('```')[0].strip()
            
            data = json.loads(raw)
            
            # Validate structure
            if isinstance(data, list) and len(data) > 0:
                for item in data:
                    if 'q' not in item or 'options' not in item or 'answer' not in item:
                        raise ValueError("Invalid question structure")
                    if len(item['options']) != 4:
                        raise ValueError("Each question must have 4 options")
                
                print(f"✅ Generated {len(data)} AI questions at {difficulty} level")
                return data[:num_questions], difficulty
            else:
                raise ValueError("Invalid response format")
        
        except Exception as e:
            print(f"⚠️  AI generation failed: {str(e)[:200]}")
            print(f"Error type: {type(e).__name__}")
    else:
        print(f"⚠️  Skipping AI generation:")
        print(f"   - Client exists: {client is not None}")
        print(f"   - GenAI available: {GENAI_AVAILABLE}")
        print(f"   - API keys: {len(API_KEYS)}")
    
    # ALWAYS use fallback if AI fails or unavailable
    print(f"📚 Using high-quality fallback questions for {topic} {subtopic}")
    fallback_questions = get_fallback_questions(topic, subtopic, num_questions)
    print(f"✅ Loaded {len(fallback_questions)} fallback questions at {difficulty} level")
    
    return fallback_questions, difficulty


def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Wrapper function that returns questions in app.py expected format
    Returns: dict with 'questions' and 'difficulty'
    """
    questions, difficulty = generate_questions(user_email, topic, subtopic, user_scores, num_questions)
    
    return {
        'questions': questions,
        'difficulty': difficulty
    }


def generate_quiz_questions(topic, context, difficulty, num_questions=5):
    """
    Generate quiz questions for Grand Test with GUARANTEED fallback
    """
    print(f"\n🎯 Grand Test: {topic} ({difficulty})")
    
    # Try AI if available
    if client and GENAI_AVAILABLE:
        try:
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
            
            if isinstance(data, list) and len(data) > 0:
                print(f"✅ AI questions generated")
                return data[:num_questions]
        
        except Exception as e:
            print(f"⚠️  AI failed: {str(e)[:50]}")
    
    # Use fallback
    return get_fallback_questions(topic, '', num_questions)


# ==================== STARTUP MESSAGE ====================
print("\n" + "="*80)
print("🎓 CAREERLENS QUESTION GENERATOR INITIALIZED")
print("="*80)
if client and GENAI_AVAILABLE:
    print(f"✅ AI Mode: ACTIVE ({len(API_KEYS)} keys available)")
    print(f"   Keys configured: {', '.join([f'KEY_{i+1}' for i in range(len(API_KEYS))])}")
else:
    print("📚 Fallback Mode: ACTIVE (High-quality question bank)")
    if not GENAI_AVAILABLE:
        print("   Reason: google-genai package not installed")
    elif not API_KEYS:
        print("   Reason: No API keys found in environment")
print("="*80 + "\n")