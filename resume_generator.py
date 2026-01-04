"""
AI-Powered Resume Generator for CareerLens
Generates professional resumes based on user profile and quiz performance
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class ResumeGenerator:
    """Generate professional resume content using AI"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_summary(self, user_data, strengths):
        """Generate professional summary based on profile"""
        prompt = f"""Create a concise 3-sentence professional summary for a {user_data['branch']} student:
        
Profile:
- CGPA: {user_data['cgpa']}
- Branch: {user_data['branch']}
- Internships: {user_data['internships']}
- Strong in: {', '.join(strengths[:3])}

Write in third person, highlight technical skills and readiness for placement. Keep it professional and impressive."""

        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return f"Motivated {user_data['branch']} student with {user_data['cgpa']} CGPA, demonstrating strong proficiency in {', '.join(strengths[:2])}. Experienced in practical applications through {user_data['internships']}. Ready to contribute technical expertise to challenging projects."
    
    def generate_project_ideas(self, branch, strengths, count=3):
        """Generate relevant project ideas based on branch and strengths"""
        prompt = f"""Suggest {count} realistic academic/personal projects for a {branch} student strong in: {', '.join(strengths[:3])}.

For each project provide:
- Project name (concise)
- 2-line description
- Technologies used (3-4 items)

Format as JSON:
{{"projects": [{{"name": "...", "description": "...", "technologies": ["...", "..."]}}]}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean JSON from markdown
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            import json
            data = json.loads(text)
            return data.get('projects', [])
        except Exception as e:
            # Fallback projects
            return [
                {
                    "name": f"{branch} Based Application",
                    "description": f"Developed application using {strengths[0] if strengths else 'modern technologies'}. Implemented core features and optimized performance.",
                    "technologies": strengths[:3] if len(strengths) >= 3 else ["Python", "SQL", "Git"]
                }
            ]
    
    def generate_skills_sections(self, strengths, all_topics):
        """Organize skills into professional categories"""
        # Categorize topics
        programming = []
        databases = []
        tools = []
        concepts = []
        
        for topic in all_topics:
            topic_lower = topic.lower()
            if any(lang in topic_lower for lang in ['python', 'java', 'c++', 'c', 'javascript']):
                programming.append(topic)
            elif any(db in topic_lower for db in ['sql', 'dbms', 'database', 'mysql']):
                databases.append(topic)
            elif any(tool in topic_lower for tool in ['git', 'linux', 'docker', 'aws']):
                tools.append(topic)
            else:
                concepts.append(topic)
        
        skills = {
            'programming': programming[:5],
            'databases': databases[:3],
            'tools': tools[:4],
            'concepts': concepts[:5]
        }
        
        return skills
    
    def generate_achievements(self, scores_data, readiness):
        """Generate achievement bullets from quiz performance"""
        achievements = []
        
        # Calculate stats
        total_quizzes = len(scores_data)
        avg_score = sum(s['score'] for s in scores_data) / sum(s['total_questions'] for s in scores_data) * 100 if scores_data else 0
        
        # Find top performing topics
        topic_performance = {}
        for score in scores_data:
            topic = score['topic']
            if topic not in topic_performance:
                topic_performance[topic] = {'score': 0, 'total': 0}
            topic_performance[topic]['score'] += score['score']
            topic_performance[topic]['total'] += score['total_questions']
        
        top_topics = []
        for topic, perf in topic_performance.items():
            if perf['total'] > 0:
                pct = (perf['score'] / perf['total']) * 100
                if pct >= 75:
                    top_topics.append(topic)
        
        # Generate achievement statements
        if readiness['score'] >= 80:
            achievements.append(f"Achieved {readiness['score']}% overall proficiency in technical assessments")
        
        if total_quizzes >= 10:
            achievements.append(f"Completed {total_quizzes}+ practice assessments demonstrating continuous learning")
        
        if top_topics:
            achievements.append(f"Demonstrated expertise in {', '.join(top_topics[:3])}")
        
        if avg_score >= 70:
            achievements.append(f"Maintained {avg_score:.0f}% average in technical evaluations")
        
        return achievements[:4]  # Limit to 4 achievements


def analyze_user_for_resume(user_data, scores_data):
    """Analyze user profile and performance for resume generation"""
    
    # Calculate strengths from scores
    topic_performance = {}
    for score in scores_data:
        key = score['topic']
        if score['subtopic']:
            key = f"{score['topic']} - {score['subtopic']}"
        
        if key not in topic_performance:
            topic_performance[key] = {'score': 0, 'total': 0}
        topic_performance[key]['score'] += score['score']
        topic_performance[key]['total'] += score['total_questions']
    
    # Sort by performance
    strengths = []
    all_topics = []
    
    for topic, perf in topic_performance.items():
        all_topics.append(topic)
        if perf['total'] > 0:
            pct = (perf['score'] / perf['total']) * 100
            if pct >= 60:  # Consider 60%+ as strength
                strengths.append((topic, pct))
    
    # Sort by percentage
    strengths.sort(key=lambda x: x[1], reverse=True)
    strength_topics = [s[0] for s in strengths]
    
    # Calculate overall readiness
    if scores_data:
        total_score = sum(s['score'] for s in scores_data)
        total_questions = sum(s['total_questions'] for s in scores_data)
        readiness_score = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        if readiness_score >= 80:
            readiness_status = 'Excellent'
        elif readiness_score >= 65:
            readiness_status = 'Good'
        elif readiness_score >= 50:
            readiness_status = 'Average'
        else:
            readiness_status = 'Developing'
    else:
        readiness_score = 0
        readiness_status = 'Not Assessed'
    
    return {
        'strengths': strength_topics,
        'all_topics': all_topics,
        'readiness': {
            'score': round(readiness_score, 1),
            'status': readiness_status
        }
    }


def generate_complete_resume(user_data, scores_data):
    """Generate complete resume data structure"""
    
    generator = ResumeGenerator()
    analysis = analyze_user_for_resume(user_data, scores_data)
    
    # Generate AI content
    professional_summary = generator.generate_summary(user_data, analysis['strengths'])
    projects = generator.generate_project_ideas(user_data['branch'], analysis['strengths'], 3)
    skills = generator.generate_skills_sections(analysis['strengths'], analysis['all_topics'])
    achievements = generator.generate_achievements(scores_data, analysis['readiness'])
    
    resume_data = {
        'personal_info': {
            'name': user_data['name'],
            'email': user_data['email'],
            'branch': user_data['branch'],
            'cgpa': user_data['cgpa'],
            'phone': '',  # To be added by user
            'linkedin': '',  # To be added by user
            'github': ''  # To be added by user
        },
        'summary': professional_summary,
        'education': {
            'degree': f"Bachelor of Technology in {user_data['branch']}",
            'cgpa': user_data['cgpa'],
            'backlogs': user_data['backlogs'],
            'year': datetime.now().year  # Expected graduation year
        },
        'skills': skills,
        'projects': projects,
        'internships': user_data['internships'],
        'achievements': achievements,
        'readiness': analysis['readiness']
    }
    
    return resume_data