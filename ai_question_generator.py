import google.generativeai as genai
import json
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# CRITICAL FIX: Use FREE TIER models only
# gemini-2.0-flash-exp has limit:0 (not available on free tier)
# Use gemini-1.5-flash which is FREE and STABLE
MODEL_NAME = 'gemini-1.5-flash'  # FREE TIER MODEL

generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 2048,  # Reduced to stay within limits
}


def determine_difficulty_level(user_scores, topic, subtopic=None):
    """Determine difficulty level based on user's past performance"""
    if not user_scores:
        return 'beginner'
    
    relevant_scores = []
    for score in user_scores:
        if subtopic:
            if score['topic'] == topic and score['subtopic'] == subtopic:
                relevant_scores.append(score)
        else:
            if score['topic'] == topic:
                relevant_scores.append(score)
    
    if not relevant_scores:
        return 'beginner'
    
    total_score = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    
    if total_questions == 0:
        return 'beginner'
    
    avg_percentage = (total_score / total_questions) * 100
    
    if avg_percentage < 50:
        return 'beginner'
    elif avg_percentage < 75:
        return 'intermediate'
    else:
        return 'advanced'


def generate_quiz_questions(topic, subtopic, difficulty_level, num_questions=5, retry_count=0):
    """
    Generate quiz questions using Gemini AI FREE TIER
    """
    
    # Max 2 retries to avoid hitting quota limits
    if retry_count > 1:
        print(f"❌ Max retries reached. Using fallback questions.")
        return get_fallback_questions(topic, subtopic, difficulty_level, num_questions)
    
    # Difficulty descriptions
    difficulty_descriptions = {
        'beginner': 'Basic concepts and fundamental understanding',
        'intermediate': 'Practical applications and problem-solving',
        'advanced': 'Complex scenarios and expert-level knowledge'
    }
    
    # Comprehensive topic contexts
    topic_contexts = {
        'C': {
            'Arrays': 'Arrays in C programming',
            'Pointers': 'Pointers in C',
            'Loops': 'Loops in C',
            'Functions': 'Functions in C'
        },
        'Java': {
            'OOPs': 'Object-Oriented Programming in Java',
            'Inheritance': 'Inheritance in Java',
            'Exceptions': 'Exception Handling in Java'
        },
        'Python': {
            'Lists': 'Python Lists',
            'Dictionaries': 'Python Dictionaries',
            'File Handling': 'File Handling in Python'
        },
        'DBMS': {
            'SQL': 'SQL queries and database operations',
            'Normalization': 'Database Normalization',
            'Transactions': 'Database Transactions'
        },
        'OS': {
            'Processes': 'Operating System Processes',
            'Threads': 'Threads in OS',
            'Memory Management': 'Memory Management in OS'
        },
        'Data Structures': {
            'Linked List': 'Linked Lists',
            'Stacks': 'Stack Data Structure',
            'Queues': 'Queue Data Structure',
            'Trees': 'Tree Data Structures'
        },
        'Algorithms': {
            'Sorting': 'Sorting Algorithms',
            'Searching': 'Searching Algorithms',
            'Dynamic Programming': 'Dynamic Programming'
        },
        'Computer Networks': {
            'OSI Model': 'OSI Reference Model',
            'TCP/IP': 'TCP/IP Protocol Suite',
            'Routing': 'Network Routing'
        },
        'OOP': {
            'Classes': 'Classes and Objects',
            'Inheritance': 'Inheritance concepts',
            'Polymorphism': 'Polymorphism'
        },
        'Quantitative Aptitude': 'Quantitative aptitude problems',
        'Logical Reasoning': 'Logical reasoning puzzles',
        'Data Interpretation': 'Data interpretation from charts',
        'Grammar': 'English grammar rules',
        'Reading Comprehension': 'Reading comprehension',
        'Synonyms & Antonyms': 'English vocabulary'
    }
    
    # Get context
    if topic in topic_contexts:
        if isinstance(topic_contexts[topic], dict) and subtopic in topic_contexts[topic]:
            context = topic_contexts[topic][subtopic]
        elif isinstance(topic_contexts[topic], str):
            context = topic_contexts[topic]
        else:
            context = f'{topic} - {subtopic}'
    else:
        context = f'{topic} - {subtopic}'
    
    # Shorter, more efficient prompt to reduce token usage
    prompt = f"""Create {num_questions} MCQ questions for {context} at {difficulty_level} level.

Rules:
- Exactly {num_questions} questions
- Each has 4 options
- Answer must match one option exactly
- JSON format only

{{
  "questions": [
    {{
      "q": "Question?",
      "options": ["A", "B", "C", "D"],
      "answer": "B"
    }}
  ]
}}

Generate now:"""

    try:
        print(f"\n🤖 Generating questions (attempt {retry_count + 1})...")
        print(f"   Topic: {context}")
        print(f"   Model: {MODEL_NAME}")
        
        # Create model
        model = genai.GenerativeModel(MODEL_NAME)
        
        # Generate with rate limiting
        if retry_count > 0:
            print(f"   ⏳ Waiting 2 seconds before retry...")
            time.sleep(2)
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        response_text = response.text.strip()
        
        # Clean response
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Extract JSON
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx]
        
        # Parse JSON
        data = json.loads(response_text)
        questions = data.get('questions', [])
        
        print(f"   ✅ Parsed {len(questions)} questions")
        
        # Validate questions
        validated_questions = []
        for idx, q in enumerate(questions):
            if not all(key in q for key in ['q', 'options', 'answer']):
                continue

            if len(q['options']) != 4:
                continue

            normalized_options = [str(opt).strip() for opt in q['options']]
            normalized_answer = str(q['answer']).strip()

            # Find matching answer
            matched_option = None
            for opt in normalized_options:
                if opt.lower() == normalized_answer.lower():
                    matched_option = opt
                    break

            if not matched_option:
                for opt in normalized_options:
                    if normalized_answer.lower() in opt.lower() or opt.lower() in normalized_answer.lower():
                        matched_option = opt
                        break

            if matched_option:
                validated_questions.append({
                    'q': q['q'],
                    'options': normalized_options,
                    'answer': matched_option,
                    'difficulty': difficulty_level,
                    'ai_generated': True
                })

        if len(validated_questions) >= 3:
            print(f"   🎉 SUCCESS: {len(validated_questions)} valid questions")
            return validated_questions[:num_questions]
        else:
            print(f"   ⚠️  Only {len(validated_questions)} valid. Retrying...")
            return generate_quiz_questions(topic, subtopic, difficulty_level, num_questions, retry_count + 1)
    
    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Error: {error_msg[:150]}")
        
        # Check if quota exceeded
        if '429' in error_msg or 'quota' in error_msg.lower():
            print(f"   ⏳ Quota exceeded. Using fallback questions.")
            return get_fallback_questions(topic, subtopic, difficulty_level, num_questions)
        
        # Other errors - retry once
        if retry_count < 1:
            return generate_quiz_questions(topic, subtopic, difficulty_level, num_questions, retry_count + 1)
        else:
            return get_fallback_questions(topic, subtopic, difficulty_level, num_questions)


def get_fallback_questions(topic, subtopic, difficulty_level, num_questions):
    """High-quality fallback questions organized by topic"""
    
    fallback_db = {
        'C': {
            'Arrays': [
                {"q": "What is the index of the first element in a C array?", "options": ["0", "1", "-1", "Depends on compiler"], "answer": "0"},
                {"q": "How do you declare an integer array of size 10 in C?", "options": ["int arr[10];", "array int[10];", "int[10] arr;", "arr int[10];"], "answer": "int arr[10];"},
                {"q": "Which operator is used to access array elements in C?", "options": ["[]", "()", "{}", "->"], "answer": "[]"},
                {"q": "Can the size of a C array be changed after declaration?", "options": ["No", "Yes", "Sometimes", "Only in C99"], "answer": "No"},
                {"q": "What does sizeof(array) return for an array in C?", "options": ["Total bytes", "Number of elements", "Address", "Element size"], "answer": "Total bytes"}
            ],
            'Pointers': [
                {"q": "What operator is used to get the address of a variable?", "options": ["&", "*", "->", "@"], "answer": "&"},
                {"q": "What operator is used to dereference a pointer?", "options": ["*", "&", "->", "."], "answer": "*"},
                {"q": "What is a NULL pointer in C?", "options": ["Pointer with value 0", "Uninitialized pointer", "Void pointer", "Pointer to void"], "answer": "Pointer with value 0"},
                {"q": "How do you declare a pointer to an integer in C?", "options": ["int *ptr;", "int ptr*;", "*int ptr;", "pointer int ptr;"], "answer": "int *ptr;"},
                {"q": "What is a dangling pointer?", "options": ["Points to freed memory", "NULL pointer", "Uninitialized pointer", "Void pointer"], "answer": "Points to freed memory"}
            ],
            'Loops': [
                {"q": "Which loop in C always executes at least once?", "options": ["do-while", "while", "for", "foreach"], "answer": "do-while"},
                {"q": "What does the 'break' statement do in a loop?", "options": ["Exits the loop", "Skips iteration", "Continues loop", "Pauses loop"], "answer": "Exits the loop"},
                {"q": "What does 'continue' do in a loop?", "options": ["Skips to next iteration", "Exits loop", "Restarts loop", "Pauses loop"], "answer": "Skips to next iteration"},
                {"q": "Which loop is best for known number of iterations?", "options": ["for", "while", "do-while", "goto"], "answer": "for"},
                {"q": "What is an infinite loop in C?", "options": ["Loop that never terminates", "Loop with error", "Nested loop", "Loop without condition"], "answer": "Loop that never terminates"}
            ],
            'Functions': [
                {"q": "What is the return type of main() function in C?", "options": ["int", "void", "float", "char"], "answer": "int"},
                {"q": "What are parameters passed to a function called?", "options": ["Arguments", "Variables", "Constants", "Operators"], "answer": "Arguments"},
                {"q": "What is recursion in C?", "options": ["Function calling itself", "Nested functions", "Loop in function", "Function pointer"], "answer": "Function calling itself"},
                {"q": "What keyword is used to return a value from a function?", "options": ["return", "exit", "break", "continue"], "answer": "return"},
                {"q": "Can a function return multiple values in C?", "options": ["No, directly", "Yes, always", "Yes, using comma", "Yes, using semicolon"], "answer": "No, directly"}
            ]
        },
        'Python': {
            'Lists': [
                {"q": "Which method adds an element to end of Python list?", "options": ["append()", "add()", "insert()", "push()"], "answer": "append()"},
                {"q": "What does list[1:3] return?", "options": ["Elements at index 1,2", "Elements at 1,2,3", "Element at 1", "Error"], "answer": "Elements at index 1,2"},
                {"q": "How do you remove last element from a list?", "options": ["pop()", "remove()", "delete()", "clear()"], "answer": "pop()"},
                {"q": "What is len([1,2,3])?", "options": ["3", "2", "1", "4"], "answer": "3"},
                {"q": "Are Python lists mutable?", "options": ["Yes", "No", "Sometimes", "Depends"], "answer": "Yes"}
            ],
            'Dictionaries': [
                {"q": "How do you access value in dictionary?", "options": ["dict[key]", "dict.key", "dict(key)", "dict->key"], "answer": "dict[key]"},
                {"q": "What method returns all keys in dictionary?", "options": ["keys()", "values()", "items()", "get()"], "answer": "keys()"},
                {"q": "How to add new key-value pair?", "options": ["dict[key]=value", "dict.add(key,value)", "dict.insert(key,value)", "dict.append(key,value)"], "answer": "dict[key]=value"},
                {"q": "What does dict.get(key) return if key not found?", "options": ["None", "Error", "False", "Empty string"], "answer": "None"},
                {"q": "Are dictionary keys ordered in Python 3.7+?", "options": ["Yes", "No", "Sometimes", "Depends"], "answer": "Yes"}
            ],
            'File Handling': [
                {"q": "Which mode opens file for reading?", "options": ["'r'", "'w'", "'a'", "'x'"], "answer": "'r'"},
                {"q": "Which mode creates new file for writing?", "options": ["'w'", "'r'", "'a'", "'x'"], "answer": "'w'"},
                {"q": "What does 'with' statement do?", "options": ["Auto closes file", "Opens file", "Reads file", "Writes file"], "answer": "Auto closes file"},
                {"q": "Which method reads entire file content?", "options": ["read()", "readline()", "readlines()", "scan()"], "answer": "read()"},
                {"q": "What mode appends to existing file?", "options": ["'a'", "'w'", "'r'", "'x'"], "answer": "'a'"}
            ]
        },
        'Java': {
            'OOPs': [
                {"q": "What is encapsulation in Java?", "options": ["Data hiding", "Inheritance", "Polymorphism", "Abstraction"], "answer": "Data hiding"},
                {"q": "What keyword creates an object?", "options": ["new", "create", "object", "make"], "answer": "new"},
                {"q": "What is a constructor?", "options": ["Special method for initialization", "Destructor", "Member function", "Static method"], "answer": "Special method for initialization"},
                {"q": "What is 'this' keyword used for?", "options": ["Current object reference", "Parent class", "Static member", "Package"], "answer": "Current object reference"},
                {"q": "Can a class have multiple constructors?", "options": ["Yes", "No", "Sometimes", "Only with inheritance"], "answer": "Yes"}
            ]
        },
        'DBMS': {
            'SQL': [
                {"q": "Which SQL statement retrieves data?", "options": ["SELECT", "INSERT", "UPDATE", "DELETE"], "answer": "SELECT"},
                {"q": "Which clause filters rows in SQL?", "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"], "answer": "WHERE"},
                {"q": "Which JOIN returns matching rows from both tables?", "options": ["INNER JOIN", "LEFT JOIN", "RIGHT JOIN", "FULL JOIN"], "answer": "INNER JOIN"},
                {"q": "What does COUNT() function do?", "options": ["Counts rows", "Sums values", "Finds average", "Gets maximum"], "answer": "Counts rows"},
                {"q": "Which statement adds new row to table?", "options": ["INSERT", "UPDATE", "SELECT", "CREATE"], "answer": "INSERT"}
            ]
        },
        'OS': {
            'Processes': [
                {"q": "What is a process in OS?", "options": ["Program in execution", "Compiled code", "Source file", "Binary file"], "answer": "Program in execution"},
                {"q": "What is process scheduling?", "options": ["Allocating CPU time", "Memory allocation", "Disk management", "File handling"], "answer": "Allocating CPU time"},
                {"q": "What is PCB?", "options": ["Process Control Block", "Program Control Block", "Process Code Block", "Processor Control Base"], "answer": "Process Control Block"},
                {"q": "What is context switching?", "options": ["Switching between processes", "Memory allocation", "CPU upgrade", "Disk operation"], "answer": "Switching between processes"},
                {"q": "What state follows the ready state?", "options": ["Running", "Waiting", "Terminated", "New"], "answer": "Running"}
            ]
        }
    }
    
    # Try to get from database
    if topic in fallback_db:
        if isinstance(fallback_db[topic], dict) and subtopic in fallback_db[topic]:
            questions = fallback_db[topic][subtopic][:num_questions]
            for q in questions:
                q['difficulty'] = difficulty_level
                q['ai_generated'] = False
            return questions
    
    # Ultimate fallback
    return [
        {
            "q": f"Which is a key concept in {topic} - {subtopic}?",
            "options": ["Fundamental principles", "Advanced techniques", "Basic operations", "All of the above"],
            "answer": "All of the above",
            "difficulty": difficulty_level,
            "ai_generated": False
        }
    ] * min(num_questions, 3)


def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """Main function to get adaptive questions"""
    
    difficulty_level = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 AI QUIZ GENERATOR (Free Tier)")
    print(f"{'='*80}")
    print(f"👤 User: {user_email}")
    print(f"📚 Topic: {topic} - {subtopic}")
    print(f"📊 Difficulty: {difficulty_level.upper()}")
    print(f"🔢 Questions: {num_questions}")
    print(f"🤖 Model: {MODEL_NAME}")
    print(f"{'='*80}")
    
    questions = generate_quiz_questions(topic, subtopic, difficulty_level, num_questions)
    
    return {
        'questions': questions,
        'difficulty': difficulty_level,
        'topic': topic,
        'subtopic': subtopic,
        'ai_generated': any(q.get('ai_generated', False) for q in questions)
    }