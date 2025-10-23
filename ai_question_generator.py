import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API with the latest model
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Using Gemini 2.5 Flash (fast and efficient)
model = genai.GenerativeModel('models/gemini-2.5-flash')


def determine_difficulty_level(user_scores, topic, subtopic=None):
    """
    Determine difficulty level based on user's past performance
    Returns: 'beginner', 'intermediate', or 'advanced'
    """
    if not user_scores:
        return 'beginner'
    
    # Filter scores for the specific topic/subtopic
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
    
    # Calculate average performance
    total_score = sum(s['score'] for s in relevant_scores)
    total_questions = sum(s['total_questions'] for s in relevant_scores)
    
    if total_questions == 0:
        return 'beginner'
    
    avg_percentage = (total_score / total_questions) * 100
    
    # Determine level based on performance
    if avg_percentage < 50:
        return 'beginner'
    elif avg_percentage < 75:
        return 'intermediate'
    else:
        return 'advanced'


def generate_quiz_questions(topic, subtopic, difficulty_level, num_questions=5):
    """
    Generate quiz questions using Gemini AI based on difficulty level
    
    Args:
        topic: Main topic (e.g., 'C', 'Java', 'Python')
        subtopic: Subtopic (e.g., 'Arrays', 'Loops')
        difficulty_level: 'beginner', 'intermediate', or 'advanced'
        num_questions: Number of questions to generate
    
    Returns:
        List of question dictionaries
    """
    
    # Create difficulty-specific prompts
    difficulty_descriptions = {
        'beginner': 'Focus on basic concepts, simple syntax, and fundamental understanding. Questions should test foundational knowledge.',
        'intermediate': 'Include practical applications, problem-solving scenarios, and deeper conceptual understanding. Mix theory with application.',
        'advanced': 'Challenge with complex scenarios, optimization problems, edge cases, and expert-level knowledge. Include tricky situations.'
    }
    
    # Topic-specific context
    topic_contexts = {
        'C': f'{subtopic} in C programming language',
        'Java': f'{subtopic} in Java programming language',
        'Python': f'{subtopic} in Python programming language',
        'DBMS': f'{subtopic} in Database Management Systems',
        'OS': f'{subtopic} in Operating Systems',
        'Data Structures': f'{subtopic} data structure',
        'Quantitative Aptitude': 'Quantitative aptitude and numerical reasoning',
        'Logical Reasoning': 'Logical reasoning and analytical thinking',
        'Data Interpretation': 'Data interpretation from tables, charts, and graphs',
        'Grammar': 'English grammar rules and usage',
        'Reading Comprehension': 'Reading comprehension and understanding',
        'Synonyms & Antonyms': 'Synonyms and antonyms in English vocabulary'
    }
    
    context = topic_contexts.get(topic, f'{topic} - {subtopic}')
    
    prompt = f"""You are an expert quiz creator for placement preparation. Generate {num_questions} multiple-choice questions about: {context}

Difficulty Level: {difficulty_level.upper()}
Instructions: {difficulty_descriptions[difficulty_level]}

CRITICAL REQUIREMENTS:
1. Each question MUST have EXACTLY 4 options
2. Questions must be at {difficulty_level} difficulty level
3. The answer must be one of the 4 options (exact match)
4. Make questions practical and relevant to placement exams
5. Return ONLY valid JSON - no markdown, no code blocks, no extra text

JSON Format (return ONLY this):
{{
    "questions": [
        {{
            "q": "What is the time complexity of binary search?",
            "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
            "answer": "O(log n)"
        }}
    ]
}}

Generate exactly {num_questions} questions now."""

    try:
        # Generate content with Gemini
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response - remove markdown formatting
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Parse JSON
        data = json.loads(response_text)
        questions = data.get('questions', [])
        
        # Validate and format questions
        validated_questions = []
        for q in questions:
            # Check required fields
            if not all(key in q for key in ['q', 'options', 'answer']):
                continue
            
            # Check options count
            if len(q['options']) != 4:
                continue
            
            # Check answer is in options
            if q['answer'] not in q['options']:
                continue
            
            validated_questions.append({
                'q': q['q'],
                'options': q['options'],
                'answer': q['answer'],
                'difficulty': difficulty_level,
                'ai_generated': True
            })
        
        # If we got at least 3 valid questions, return them
        if len(validated_questions) >= 3:
            print(f"✅ Generated {len(validated_questions)} AI questions at {difficulty_level} level")
            return validated_questions[:num_questions]
        else:
            print(f"⚠️ Not enough valid AI questions. Using fallback.")
            return get_fallback_questions(topic, subtopic, difficulty_level, num_questions)
    
    except Exception as e:
        print(f"❌ Error generating AI questions: {e}")
        return get_fallback_questions(topic, subtopic, difficulty_level, num_questions)


def get_fallback_questions(topic, subtopic, difficulty_level='beginner', num_questions=5):
    """
    Fallback questions if AI generation fails
    """
    fallback_db = {
        'C': {
            'Arrays': {
                'beginner': [
                    {"q": "What is the index of the first element in an array?", "options": ["0","1","-1","Depends"], "answer": "0"},
                    {"q": "How do you declare an integer array of size 10?", "options": ["int arr[10];","array int[10];","int[10] arr;","arr int[10];"], "answer": "int arr[10];"},
                    {"q": "Which operator accesses array elements?", "options": ["[]","()","{}","<>"], "answer": "[]"},
                    {"q": "What is the size of int array[5]?", "options": ["20 bytes","5 bytes","Depends on system","10 bytes"], "answer": "Depends on system"},
                    {"q": "Can array size be changed after declaration?", "options": ["No","Yes","Sometimes","Depends"], "answer": "No"}
                ],
                'intermediate': [
                    {"q": "What happens when you access array[10] in int array[10]?", "options": ["Undefined behavior","Compiler error","Returns 0","Returns NULL"], "answer": "Undefined behavior"},
                    {"q": "What is array decay?", "options": ["Array converts to pointer","Array loses data","Array becomes NULL","None"], "answer": "Array converts to pointer"},
                    {"q": "How to find array length in C?", "options": ["sizeof(arr)/sizeof(arr[0])","length(arr)","arr.length","size(arr)"], "answer": "sizeof(arr)/sizeof(arr[0])"},
                    {"q": "What is returned by sizeof(array)?", "options": ["Total bytes","Number of elements","Address","Type"], "answer": "Total bytes"},
                    {"q": "Can you return an array from a function?", "options": ["Only pointer to array","Yes directly","No","Sometimes"], "answer": "Only pointer to array"}
                ],
                'advanced': [
                    {"q": "What is the time complexity of accessing array element?", "options": ["O(1)","O(n)","O(log n)","O(n^2)"], "answer": "O(1)"},
                    {"q": "What happens in int arr[] = {1,2,3};?", "options": ["Compiler determines size","Error","Size must be specified","Creates pointer"], "answer": "Compiler determines size"},
                    {"q": "Which is true about multidimensional arrays?", "options": ["Stored in row-major order","Stored in column-major","Random storage","Stack storage only"], "answer": "Stored in row-major order"},
                    {"q": "What is VLA in C?", "options": ["Variable Length Array","Virtual Linear Array","Vector Length Array","None"], "answer": "Variable Length Array"},
                    {"q": "Can array elements be const?", "options": ["Yes","No","Only first element","Only static arrays"], "answer": "Yes"}
                ]
            },
            'Pointers': {
                'beginner': [
                    {"q": "What does * operator do with pointers?", "options": ["Dereferences pointer","Gets address","Multiplies","Divides"], "answer": "Dereferences pointer"},
                    {"q": "What does & operator do?", "options": ["Gets address","Dereferences","Adds","Compares"], "answer": "Gets address"},
                    {"q": "What is NULL pointer?", "options": ["Pointer with address 0","Invalid pointer","Uninitialized","All of above"], "answer": "Pointer with address 0"},
                    {"q": "How to declare integer pointer?", "options": ["int *ptr;","int ptr*;","*int ptr;","pointer int ptr;"], "answer": "int *ptr;"},
                    {"q": "What is wild pointer?", "options": ["Uninitialized pointer","NULL pointer","Valid pointer","Freed pointer"], "answer": "Uninitialized pointer"}
                ],
                'intermediate': [
                    {"q": "What is dangling pointer?", "options": ["Points to freed memory","NULL pointer","Uninitialized","Valid pointer"], "answer": "Points to freed memory"},
                    {"q": "What is pointer arithmetic?", "options": ["Math with addresses","Adding pointers","Subtracting values","None"], "answer": "Math with addresses"},
                    {"q": "What does ptr++ do?", "options": ["Moves to next element","Increments value","Adds 1 byte","Error"], "answer": "Moves to next element"},
                    {"q": "Can you compare pointers?", "options": ["Yes if same array","Always yes","Never","Only NULL"], "answer": "Yes if same array"},
                    {"q": "What is void pointer?", "options": ["Generic pointer","Empty pointer","NULL pointer","Invalid"], "answer": "Generic pointer"}
                ],
                'advanced': [
                    {"q": "What is double pointer used for?", "options": ["Pointer to pointer","Two pointers","Double precision","2D arrays"], "answer": "Pointer to pointer"},
                    {"q": "What is function pointer?", "options": ["Points to function","Points to code","Special pointer","All of above"], "answer": "All of above"},
                    {"q": "Can you have array of pointers?", "options": ["Yes","No","Only in structures","Only global"], "answer": "Yes"},
                    {"q": "What is const pointer?", "options": ["Pointer address can't change","Pointed value can't change","Both","None"], "answer": "Pointer address can't change"},
                    {"q": "What is pointer to const?", "options": ["Can't modify pointed value","Can't change pointer","Both","None"], "answer": "Can't modify pointed value"}
                ]
            },
            'Loops': {
                'beginner': [
                    {"q": "Which loop executes at least once?", "options": ["do-while","while","for","None"], "answer": "do-while"},
                    {"q": "What does break do?", "options": ["Exits loop","Skips iteration","Pauses","Restarts"], "answer": "Exits loop"},
                    {"q": "What does continue do?", "options": ["Skips to next iteration","Exits loop","Pauses","Restarts"], "answer": "Skips to next iteration"},
                    {"q": "Which loop is best for unknown iterations?", "options": ["while","for","do-while","All same"], "answer": "while"},
                    {"q": "What is infinite loop?", "options": ["Loop that never ends","Very long loop","Nested loop","Error"], "answer": "Loop that never ends"}
                ],
                'intermediate': [
                    {"q": "Can you use break in nested loops?", "options": ["Exits innermost loop","Exits all loops","Error","Exits outer loop"], "answer": "Exits innermost loop"},
                    {"q": "What happens if for loop condition is empty?", "options": ["Infinite loop","Error","Executes once","Never executes"], "answer": "Infinite loop"},
                    {"q": "Can you modify loop variable inside loop?", "options": ["Yes","No","Only in while","Only in for"], "answer": "Yes"},
                    {"q": "What is loop unrolling?", "options": ["Optimization technique","Nested loops","Breaking loops","Error handling"], "answer": "Optimization technique"},
                    {"q": "Can loops be labeled in C?", "options": ["No","Yes","Only switch","Only goto"], "answer": "No"}
                ],
                'advanced': [
                    {"q": "What is the time complexity of nested loop n*m?", "options": ["O(n*m)","O(n+m)","O(n^2)","O(log n)"], "answer": "O(n*m)"},
                    {"q": "What is loop invariant?", "options": ["Condition true each iteration","Loop variable","Loop counter","None"], "answer": "Condition true each iteration"},
                    {"q": "Can you use goto to exit nested loops?", "options": ["Yes","No","Only inner","Only outer"], "answer": "Yes"},
                    {"q": "What is loop fusion?", "options": ["Combining loops","Breaking loops","Nested loops","Error"], "answer": "Combining loops"},
                    {"q": "What optimization does compiler do for loops?", "options": ["All of below","Loop unrolling","Invariant hoisting","Strength reduction"], "answer": "All of below"}
                ]
            },
            'Functions': {
                'beginner': [
                    {"q": "What is return type for no return value?", "options": ["void","null","int","None"], "answer": "void"},
                    {"q": "How are arguments passed by default?", "options": ["By value","By reference","By pointer","By address"], "answer": "By value"},
                    {"q": "What is function prototype?", "options": ["Function declaration","Function definition","Function call","Function pointer"], "answer": "Function declaration"},
                    {"q": "Can function return multiple values?", "options": ["No directly","Yes always","Sometimes","Only arrays"], "answer": "No directly"},
                    {"q": "What is main() return type?", "options": ["int","void","char","float"], "answer": "int"}
                ],
                'intermediate': [
                    {"q": "What is recursion?", "options": ["Function calls itself","Nested functions","Function pointer","Loop"], "answer": "Function calls itself"},
                    {"q": "What is call by reference?", "options": ["Pass address","Pass value","Pass copy","Pass pointer"], "answer": "Pass address"},
                    {"q": "Can functions have default arguments?", "options": ["No in C","Yes always","Only main()","Only void"], "answer": "No in C"},
                    {"q": "What is function overloading?", "options": ["Not in C","Yes in C","Only in C++","Sometimes"], "answer": "Not in C"},
                    {"q": "What is inline function?", "options": ["Suggestion to compiler","Macro","Normal function","Error"], "answer": "Suggestion to compiler"}
                ],
                'advanced': [
                    {"q": "What is tail recursion?", "options": ["Recursive call is last","First call","Middle call","No recursion"], "answer": "Recursive call is last"},
                    {"q": "What is function pointer syntax?", "options": ["returnType (*name)(params)","returnType *name(params)","returnType name(*params)","None"], "answer": "returnType (*name)(params)"},
                    {"q": "What is variadic function?", "options": ["Variable arguments","Variable return","Variable name","None"], "answer": "Variable arguments"},
                    {"q": "What is stack frame?", "options": ["Function call memory","Stack data structure","Error","Heap memory"], "answer": "Function call memory"},
                    {"q": "What is trampolining?", "options": ["Recursion optimization","Function call","Loop technique","Error"], "answer": "Recursion optimization"}
                ]
            }
        }
    }
    
    # Get questions for topic/subtopic/difficulty
    try:
        questions = fallback_db[topic][subtopic][difficulty_level]
        return questions[:num_questions]
    except:
        # Ultimate fallback
        return [
            {"q": f"Sample {difficulty_level} question for {topic} - {subtopic}", 
             "options": ["Option A", "Option B", "Option C", "Option D"], 
             "answer": "Option A",
             "difficulty": difficulty_level}
        ] * num_questions


def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Main function to get adaptive AI-generated questions
    
    Returns: Dictionary with questions and metadata
    """
    # Determine difficulty based on past performance
    difficulty_level = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n🎯 AI Quiz Generator")
    print(f"👤 User: {user_email}")
    print(f"📚 Topic: {topic} - {subtopic}")
    print(f"📊 Difficulty: {difficulty_level.upper()}")
    print(f"🔢 Questions: {num_questions}")
    
    # Generate AI questions
    questions = generate_quiz_questions(topic, subtopic, difficulty_level, num_questions)
    
    return {
        'questions': questions,
        'difficulty': difficulty_level,
        'topic': topic,
        'subtopic': subtopic,
        'ai_generated': True
    }