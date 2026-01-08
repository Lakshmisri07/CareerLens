# ai_question_generator.py

import os
import json
import google.genai as genai     # Supported import
from google.genai.types import TextGenerationInput
from dotenv import load_dotenv

load_dotenv()

# No configure() here — instead, use env key directly
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GENAI_API_KEY") or os.getenv("OPENAI_API_KEY")

def generate_questions(user_email, topic, subtopic, user_scores, num_questions=5):
    """
    Generate adaptive quiz questions for ANY topic or subtopic.
    Returns:
        questions (list), difficulty (str)
    """

    topic = topic.strip()
    subtopic = subtopic.strip() if subtopic else ""

    # Determine approximate difficulty
    difficulty = "medium"
    for r in user_scores:
        if r["topic"] == topic and r["subtopic"] == subtopic:
            percent = (r["score"] / max(1, r["total_questions"])) * 100
            if percent < 40:
                difficulty = "easy"
            elif percent >= 80:
                difficulty = "hard"
            else:
                difficulty = "medium"
            break

    # Build prompt
    prompt_text = f"""
    Generate {num_questions} multiple choice questions.

    Topic: {topic}
    Subtopic: {subtopic}
    Difficulty: {difficulty}

    Return ONLY a JSON array of objects like:
    [
      {{
        "question": "Question text",
        "options": ["A","B","C","D"],
        "answer": "Correct option text"
      }}
    ]
    """

    try:
        model = genai.genai.create_model("gemini-pro")  # Use available model
        response = model.generate_text(
            TextGenerationInput(
                content=prompt_text,
                max_output_tokens=1024
            ),
            api_key=API_KEY
        )

        raw = response.output_text.strip()

        # Remove markdown code fences if present
        if raw.startswith("```"):
            raw = raw.replace("```json", "").replace("```", "").strip()

        data = json.loads(raw)
        if isinstance(data, list):
            return data, difficulty

    except Exception as e:
        print(f"[AI ERROR] Generation failed: {e}")

    # Fallback questions
    fallback = [{
        "question": f"Basic concept of {topic} {subtopic}?",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "answer": "Option A"
    } for _ in range(num_questions)]

    return fallback, difficulty
