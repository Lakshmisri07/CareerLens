import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

# Use the latest available model
try:
    model = genai.GenerativeModel('gemini-1.5-flash')
except:
    try:
        model = genai.GenerativeModel('gemini-1.5-pro')
    except:
        model = genai.GenerativeModel('models/gemini-pro')


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
    
    # Determine level
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
    
    # Create difficulty-specific prompt
    difficulty_descriptions = {
        'beginner': 'basic concepts, simple syntax, and fundamental understanding. Questions should be straightforward.',
        'intermediate': 'practical applications, problem-solving, and deeper understanding. Include scenario-based questions.',
        'advanced': 'complex scenarios, optimization, edge cases, and expert-level knowledge. Include challenging problems.'
    }
    
    prompt = f"""Generate {num_questions} multiple choice questions for {topic} - {subtopic if subtopic else ''} at {difficulty_level} level.

Difficulty Level Description: {difficulty_descriptions[difficulty_level]}

Requirements:
1. Each question must have exactly 4 options
2. Mark the correct answer clearly
3. Questions should be at {difficulty_level} difficulty level
4. Return ONLY valid JSON format, no extra text
5. Format:
{{
    "questions": [
        {{
            "q": "Question text here?",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "answer": "Correct option text exactly as written",
            "difficulty": "{difficulty_level}"
        }}
    ]
}}

Generate {num_questions} questions now."""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response - remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text.replace('```json', '').replace('```', '').strip()
        elif response_text.startswith('```'):
            response_text = response_text.replace('```', '').strip()
        
        # Parse JSON
        data = json.loads(response_text)
        questions = data.get('questions', [])
        
        # Validate questions
        validated_questions = []
        for q in questions:
            if all(key in q for key in ['q', 'options', 'answer']) and len(q['options']) == 4:
                validated_questions.append({
                    'q': q['q'],
                    'options': q['options'],
                    'answer': q['answer'],
                    'difficulty': difficulty_level,
                    'ai_generated': True
                })
        
        return validated_questions if validated_questions else get_fallback_questions(topic, subtopic)
    
    except Exception as e:
        print(f"Error generating questions: {e}")
        return get_fallback_questions(topic, subtopic)


def get_fallback_questions(topic, subtopic):
    """
    Fallback questions if AI generation fails
    """
    fallback = {
        'C': {
            'Arrays': [
                {"q": "What is an array?", "options": ["Collection of elements", "Single variable", "Function", "Loop"], "answer": "Collection of elements", "difficulty": "beginner"}
            ],
            'Pointers': [
                {"q": "What does * operator do with pointers?", "options": ["Dereference", "Address", "Multiply", "Divide"], "answer": "Dereference", "difficulty": "beginner"}
            ]
        }
    }
    
    return fallback.get(topic, {}).get(subtopic, [
        {"q": "Sample question", "options": ["A", "B", "C", "D"], "answer": "A", "difficulty": "beginner"}
    ])


def get_adaptive_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Main function to get adaptive questions based on user performance
    
    Args:
        user_email: User identifier
        topic: Quiz topic
        subtopic: Quiz subtopic
        user_scores: List of user's past scores
        num_questions: Number of questions to generate
    
    Returns:
        List of questions and difficulty level
    """
    # Determine user's current level
    difficulty_level = determine_difficulty_level(user_scores, topic, subtopic)
    
    print(f"Generating {difficulty_level} questions for {user_email} - {topic}/{subtopic}")
    
    # Generate questions using AI
    questions = generate_quiz_questions(topic, subtopic, difficulty_level, num_questions)
    
    return {
        'questions': questions,
        'difficulty': difficulty_level,
        'topic': topic,
        'subtopic': subtopic
    }