import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API with the UPDATED model
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# CRITICAL FIX: Use the latest stable model instead of deprecated 1.5 Flash
# Options: 'gemini-2.5-flash' or 'gemini-2.0-flash-exp'
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Configure generation settings for better JSON output
generation_config = {
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
}


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
        'beginner': 'Focus on basic concepts, simple syntax, and fundamental understanding. Questions should test foundational knowledge with clear, straightforward options.',
        'intermediate': 'Include practical applications, problem-solving scenarios, and deeper conceptual understanding. Mix theory with application.',
        'advanced': 'Challenge with complex scenarios, optimization problems, edge cases, and expert-level knowledge. Include tricky situations and require deep understanding.'
    }
    
    # Topic-specific context
    topic_contexts = {
        'C': f'{subtopic} in C programming language',
        'Java': f'{subtopic} in Java programming language',
        'Python': f'{subtopic} in Python programming language',
        'DBMS': f'{subtopic} in Database Management Systems',
        'OS': f'{subtopic} in Operating Systems',
        'Data Structures': f'{subtopic} data structure',
        'Quantitative Aptitude': 'Quantitative aptitude and numerical reasoning for placement exams',
        'Logical Reasoning': 'Logical reasoning and analytical thinking for competitive exams',
        'Data Interpretation': 'Data interpretation from tables, charts, and graphs',
        'Grammar': 'English grammar rules, sentence correction, and usage',
        'Reading Comprehension': 'Reading comprehension and understanding of passages',
        'Synonyms & Antonyms': 'Synonyms and antonyms in English vocabulary',
        'Technical': 'Programming, Data Structures, Algorithms, DBMS, and Operating Systems concepts for technical interviews',
        'Aptitude': 'Quantitative aptitude, logical reasoning, and problem-solving for placement tests',
        'English': 'English grammar, vocabulary, and communication skills for placement exams'
    }
    
    context = topic_contexts.get(topic, f'{topic} - {subtopic}')
    
    # IMPROVED PROMPT - More explicit and structured
    prompt = f"""You are an expert quiz creator for placement exams. Generate {num_questions} multiple-choice questions.

TOPIC: {context}
DIFFICULTY: {difficulty_level.upper()}
INSTRUCTIONS: {difficulty_descriptions[difficulty_level]}

CRITICAL REQUIREMENTS (FOLLOW EXACTLY):
1. Generate EXACTLY {num_questions} questions
2. Each question MUST have EXACTLY 4 options (A, B, C, D)
3. Answer MUST be one of the 4 options (word-for-word match)
4. Questions must be at {difficulty_level} level
5. Make questions practical and relevant to placement exams
6. Output ONLY valid JSON - no explanations, no markdown, no code blocks

STRICT JSON FORMAT (output this exact structure):
{{
    "questions": [
        {{
            "q": "What is the time complexity of binary search?",
            "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
            "answer": "O(log n)"
        }}
    ]
}}

IMPORTANT: The "answer" field must EXACTLY match one of the strings in "options" array.

Generate {num_questions} questions NOW in this exact JSON format:"""

    try:
        print(f"\n🤖 Generating {num_questions} AI questions...")
        print(f"   Topic: {context}")
        print(f"   Difficulty: {difficulty_level}")
        
        # Generate content with improved configuration
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        response_text = response.text.strip()
        
        # Debug: Print raw response
        print(f"\n📥 Raw Response (first 500 chars):")
        print(response_text[:500])
        
        # Clean response - remove markdown formatting
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Remove any leading/trailing whitespace and non-JSON content
        response_text = response_text.strip()
        
        # Find JSON object boundaries
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx > start_idx:
            response_text = response_text[start_idx:end_idx]
        
        print(f"\n🧹 Cleaned Response (first 500 chars):")
        print(response_text[:500])
        
        # Parse JSON
        data = json.loads(response_text)
        questions = data.get('questions', [])
        
        print(f"\n✅ Parsed {len(questions)} questions from JSON")
        
        # Validate and format questions
        validated_questions = []
        for idx, q in enumerate(questions):
            print(f"\n🔍 Validating Q{idx+1}...")
            
            # Check required fields
            if not all(key in q for key in ['q', 'options', 'answer']):
                print(f"   ❌ Missing required fields: {list(q.keys())}")
                continue

            # Check options count
            if len(q['options']) != 4:
                print(f"   ❌ Wrong option count: {len(q['options'])} (need 4)")
                continue

            # Normalize answer and options
            normalized_options = [str(opt).strip() for opt in q['options']]
            normalized_answer = str(q['answer']).strip()

            # Check if answer exists in options (exact match, case-insensitive)
            answer_in_options = False
            matched_option = normalized_answer

            for opt in normalized_options:
                if opt.lower() == normalized_answer.lower():
                    answer_in_options = True
                    matched_option = opt  # Use the exact option text
                    break

            if not answer_in_options:
                print(f"   ❌ Answer '{normalized_answer}' not in options: {normalized_options}")
                # Try partial match
                for opt in normalized_options:
                    if normalized_answer.lower() in opt.lower() or opt.lower() in normalized_answer.lower():
                        matched_option = opt
                        answer_in_options = True
                        print(f"   ✓ Fixed: Using '{matched_option}' as answer")
                        break

                if not answer_in_options:
                    print(f"   ✗ Skipping question - cannot match answer")
                    continue

            validated_questions.append({
                'q': q['q'],
                'options': normalized_options,
                'answer': matched_option,
                'difficulty': difficulty_level,
                'ai_generated': True
            })

            print(f"   ✅ Valid: answer='{matched_option}' in {normalized_options}")
        
        # If we got at least 3 valid questions, return them
        if len(validated_questions) >= 3:
            print(f"\n🎉 SUCCESS: Generated {len(validated_questions)} valid AI questions")
            return validated_questions[:num_questions]
        else:
            print(f"\n⚠️  Not enough valid questions ({len(validated_questions)}). Using fallback.")
            return get_fallback_questions(topic, subtopic, difficulty_level, num_questions)
    
    except json.JSONDecodeError as e:
        print(f"\n❌ JSON Parse Error: {e}")
        print(f"   Response text: {response_text[:200]}")
        return get_fallback_questions(topic, subtopic, difficulty_level, num_questions)
    except Exception as e:
        print(f"\n❌ Error generating AI questions: {e}")
        import traceback
        traceback.print_exc()
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
            }
        }
    }
    
    # Get questions for topic/subtopic/difficulty
    try:
        questions = fallback_db.get(topic, {}).get(subtopic, {}).get(difficulty_level, [])
        if questions:
            return questions[:num_questions]
    except:
        pass
    
    # Ultimate fallback - generic questions
    return [
        {
            "q": f"Which of the following is a key concept in {topic} - {subtopic}?",
            "options": ["Concept A", "Concept B", "Concept C", "All of the above"],
            "answer": "All of the above",
            "difficulty": difficulty_level
        }
    ] * min(num_questions, 3)


def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Main function to get adaptive AI-generated questions
    
    Returns: Dictionary with questions and metadata
    """
    # Determine difficulty based on past performance
    difficulty_level = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"\n{'='*80}")
    print(f"🎯 AI QUIZ GENERATOR")
    print(f"{'='*80}")
    print(f"👤 User: {user_email}")
    print(f"📚 Topic: {topic} - {subtopic}")
    print(f"📊 Difficulty: {difficulty_level.upper()}")
    print(f"🔢 Questions: {num_questions}")
    print(f"{'='*80}")
    
    # Generate AI questions
    questions = generate_quiz_questions(topic, subtopic, difficulty_level, num_questions)
    
    return {
        'questions': questions,
        'difficulty': difficulty_level,
        'topic': topic,
        'subtopic': subtopic,
        'ai_generated': True
    }