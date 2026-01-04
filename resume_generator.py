"""
Resume Generator for CareerLens
Generates professional resumes based on user profile, quiz performance, and certificates
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

class ResumeGenerator:
    """Generate professional resume content"""
    
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def generate_summary(self, user_data, strengths, certificates):
        """Generate professional summary based on profile"""
        cert_context = f"Certified in: {', '.join([c['name'] for c in certificates[:3]])}" if certificates else ""
        
        prompt = f"""Create a concise 3-sentence professional summary for a {user_data['branch']} student resume:
        
Profile:
- CGPA: {user_data['cgpa']}
- Branch: {user_data['branch']}
- Internships: {user_data['internships']}
- Strong skills: {', '.join(strengths[:3])}
- {cert_context}

IMPORTANT: Write ONLY the professional summary text. Do NOT mention:
- "AI-powered" or "AI-generated"
- "Quiz performance" or "assessments"
- Any meta-commentary about the text itself

Write in first person, be professional and achievement-focused."""

        try:
            response = self.model.generate_content(prompt)
            summary = response.text.strip()
            # Remove any AI/assessment mentions if they slip through
            summary = summary.replace('AI-powered', '').replace('AI-generated', '')
            summary = summary.replace('quiz', '').replace('assessment', 'evaluation')
            return summary
        except:
            return f"Dedicated {user_data['branch']} student with {user_data['cgpa']} CGPA and strong technical foundation in {', '.join(strengths[:2])}. Experienced through {user_data['internships']} with proven ability to apply theoretical knowledge to practical solutions. Passionate about leveraging technology to solve real-world problems."
    
    def generate_project_ideas(self, branch, strengths, count=3):
        """Generate relevant project ideas"""
        prompt = f"""Suggest {count} realistic technical projects for a {branch} student skilled in: {', '.join(strengths[:3])}.

For each project provide:
- Project name (professional, no "AI-powered" prefix)
- 2-line description focusing on what was built and impact
- Technologies used (3-4 items)

IMPORTANT: Do NOT mention AI, ML, or quiz performance in descriptions.

Format as JSON:
{{"projects": [{{"name": "...", "description": "...", "technologies": ["...", "..."]}}]}}"""

        try:
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            
            import json
            data = json.loads(text)
            return data.get('projects', [])
        except:
            return [
                {
                    "name": f"{branch} Management System",
                    "description": f"Developed comprehensive system using {strengths[0] if strengths else 'modern technologies'}. Implemented user authentication, data management, and reporting features with responsive design.",
                    "technologies": strengths[:3] if len(strengths) >= 3 else ["Python", "SQL", "HTML/CSS"]
                }
            ]
    
    def recommend_skills(self, strengths, certificates, all_topics):
        """Recommend additional skills user should mention based on their knowledge"""
        # Extract certificate skills
        cert_skills = []
        for cert in certificates:
            cert_name_lower = cert['name'].lower()
            # Extract technology names from certificates
            if 'python' in cert_name_lower:
                cert_skills.extend(['Python', 'Data Analysis', 'Automation'])
            if 'java' in cert_name_lower:
                cert_skills.extend(['Java', 'OOP', 'Spring Framework'])
            if 'web' in cert_name_lower or 'html' in cert_name_lower:
                cert_skills.extend(['HTML', 'CSS', 'JavaScript', 'Responsive Design'])
            if 'sql' in cert_name_lower or 'database' in cert_name_lower:
                cert_skills.extend(['SQL', 'Database Design', 'Query Optimization'])
            if 'aws' in cert_name_lower or 'cloud' in cert_name_lower:
                cert_skills.extend(['Cloud Computing', 'AWS', 'DevOps'])
            if 'data' in cert_name_lower:
                cert_skills.extend(['Data Analysis', 'Data Visualization', 'Statistics'])
        
        # Map quiz topics to resume-friendly skills
        skill_mapping = {
            'C': ['C Programming', 'Memory Management', 'Data Structures'],
            'Java': ['Java', 'Object-Oriented Programming', 'Spring Boot'],
            'Python': ['Python', 'Django', 'Flask', 'Pandas', 'NumPy'],
            'DBMS': ['Database Management', 'SQL', 'MySQL', 'PostgreSQL'],
            'OS': ['Operating Systems', 'Linux', 'System Programming'],
            'Data Structures': ['Data Structures', 'Algorithms', 'Problem Solving'],
            'Algorithms': ['Algorithm Design', 'Complexity Analysis', 'Optimization'],
            'OOP': ['Object-Oriented Design', 'Design Patterns', 'SOLID Principles'],
            'Networking': ['Computer Networks', 'TCP/IP', 'Network Security'],
            'Web Development': ['Full Stack Development', 'REST APIs', 'Frontend Development']
        }
        
        recommended = set()
        
        # Add skills from strong topics
        for topic in strengths:
            base_topic = topic.split(' - ')[0] if ' - ' in topic else topic
            if base_topic in skill_mapping:
                recommended.update(skill_mapping[base_topic])
        
        # Add certificate-derived skills
        recommended.update(cert_skills)
        
        # Add complementary skills based on what they know
        if any('Python' in s for s in recommended):
            recommended.update(['API Development', 'Scripting'])
        if any('Java' in s for s in recommended):
            recommended.update(['Maven', 'JUnit'])
        if any('Web' in s or 'HTML' in s for s in recommended):
            recommended.update(['Bootstrap', 'jQuery'])
        if any('Database' in s or 'SQL' in s for s in recommended):
            recommended.update(['Database Normalization', 'Indexing'])
        
        # General skills to add
        recommended.update(['Git', 'GitHub', 'Problem Solving', 'Team Collaboration'])
        
        return list(recommended)
    
    def organize_skills(self, strengths, certificates, all_topics):
        """Organize skills into professional categories"""
        all_skills = self.recommend_skills(strengths, certificates, all_topics)
        
        programming = []
        technologies = []
        tools = []
        soft_skills = []
        
        prog_keywords = ['python', 'java', 'c++', 'c', 'javascript', 'programming']
        tech_keywords = ['database', 'sql', 'web', 'api', 'framework', 'spring', 'django', 'flask', 'data']
        tool_keywords = ['git', 'github', 'linux', 'docker', 'aws', 'cloud', 'maven', 'junit']
        soft_keywords = ['problem', 'team', 'collaboration', 'communication', 'leadership']
        
        for skill in all_skills:
            skill_lower = skill.lower()
            if any(kw in skill_lower for kw in prog_keywords):
                programming.append(skill)
            elif any(kw in skill_lower for kw in tech_keywords):
                technologies.append(skill)
            elif any(kw in skill_lower for kw in tool_keywords):
                tools.append(skill)
            elif any(kw in skill_lower for kw in soft_keywords):
                soft_skills.append(skill)
            else:
                technologies.append(skill)
        
        return {
            'programming': list(set(programming))[:8],
            'technologies': list(set(technologies))[:8],
            'tools': list(set(tools))[:6],
            'soft_skills': list(set(soft_skills))[:4]
        }
    
    def generate_achievements(self, scores_data, readiness, certificates):
        """Generate achievement bullets from performance and certificates"""
        achievements = []
        
        total_quizzes = len(scores_data)
        avg_score = sum(s['score'] for s in scores_data) / sum(s['total_questions'] for s in scores_data) * 100 if scores_data else 0
        
        # Certificates as achievements
        for cert in certificates[:2]:  # Top 2 certificates
            achievements.append(f"Earned {cert['name']} certification from {cert['issuer']}")
        
        # Find top performing areas (but don't mention "quiz")
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
        
        if top_topics:
            achievements.append(f"Demonstrated strong proficiency in {', '.join(top_topics[:2])}")
        
        if readiness['score'] >= 75:
            achievements.append(f"Maintained consistent technical skill development with {readiness['score']:.0f}% competency level")
        
        # Generic strong achievements
        achievements.extend([
            "Completed multiple technical projects showcasing practical application of concepts",
            "Actively engaged in continuous learning and skill enhancement"
        ])
        
        return achievements[:5]


def analyze_user_for_resume(user_data, scores_data, certificates):
    """Analyze user profile and performance"""
    
    topic_performance = {}
    for score in scores_data:
        key = score['topic']
        if score['subtopic']:
            key = f"{score['topic']} - {score['subtopic']}"
        
        if key not in topic_performance:
            topic_performance[key] = {'score': 0, 'total': 0}
        topic_performance[key]['score'] += score['score']
        topic_performance[key]['total'] += score['total_questions']
    
    strengths = []
    all_topics = []
    
    for topic, perf in topic_performance.items():
        all_topics.append(topic)
        if perf['total'] > 0:
            pct = (perf['score'] / perf['total']) * 100
            if pct >= 60:
                strengths.append((topic, pct))
    
    strengths.sort(key=lambda x: x[1], reverse=True)
    strength_topics = [s[0] for s in strengths]
    
    if scores_data:
        total_score = sum(s['score'] for s in scores_data)
        total_questions = sum(s['total_questions'] for s in scores_data)
        readiness_score = (total_score / total_questions * 100) if total_questions > 0 else 0
        
        if readiness_score >= 80:
            readiness_status = 'Excellent'
        elif readiness_score >= 65:
            readiness_status = 'Good'
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


def generate_complete_resume(user_data, scores_data, certificates=[]):
    """Generate complete resume data structure"""
    
    generator = ResumeGenerator()
    analysis = analyze_user_for_resume(user_data, scores_data, certificates)
    
    # Generate content
    professional_summary = generator.generate_summary(user_data, analysis['strengths'], certificates)
    projects = generator.generate_project_ideas(user_data['branch'], analysis['strengths'], 3)
    skills = generator.organize_skills(analysis['strengths'], certificates, analysis['all_topics'])
    achievements = generator.generate_achievements(scores_data, analysis['readiness'], certificates)
    
    resume_data = {
        'personal_info': {
            'name': user_data['name'],
            'email': user_data['email'],
            'branch': user_data['branch'],
            'cgpa': user_data['cgpa'],
            'phone': '',
            'linkedin': '',
            'github': ''
        },
        'summary': professional_summary,
        'education': {
            'degree': f"Bachelor of Technology in {user_data['branch']}",
            'cgpa': user_data['cgpa'],
            'backlogs': user_data['backlogs'],
            'year': datetime.now().year
        },
        'skills': skills,
        'projects': projects,
        'internships': user_data['internships'],
        'certificates': certificates,
        'achievements': achievements,
        'readiness': analysis['readiness']
    }
    
    return resume_data