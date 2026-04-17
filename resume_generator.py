"""
Resume Generator for CareerLens
Generates professional resumes based on user profile, quiz performance, and certificates
"""

from google import genai
from google.genai import types
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Initialize GenAI client
API_KEY = os.getenv('GEMINI_API_KEY_1') or os.getenv('GOOGLE_API_KEY')
try:
    client = genai.Client(api_key=API_KEY)
except Exception as e:
    print(f"Warning: GenAI client initialization failed: {e}")
    client = None


# ============================================================================
# BRANCH → SKILLS MAPPING
# Skills shown must be relevant to the student's branch
# ============================================================================

BRANCH_SKILL_MAPPING = {
    'CSE': {
        'programming': ['C Programming', 'Java', 'Python', 'C++'],
        'technologies': ['Data Structures', 'Algorithms', 'SQL', 'Git'],
        'tools': ['VS Code', 'GitHub', 'Linux', 'MySQL'],
        'soft_skills': ['Problem Solving', 'Team Collaboration', 'Communication'],
    },
    'COMPUTER SCIENCE': {
        'programming': ['C Programming', 'Java', 'Python', 'C++'],
        'technologies': ['Data Structures', 'Algorithms', 'SQL', 'Git'],
        'tools': ['VS Code', 'GitHub', 'Linux', 'MySQL'],
        'soft_skills': ['Problem Solving', 'Team Collaboration', 'Communication'],
    },
    'IT': {
        'programming': ['Python', 'Java', 'JavaScript', 'C'],
        'technologies': ['Web Development', 'SQL', 'REST APIs', 'Git'],
        'tools': ['VS Code', 'GitHub', 'Postman', 'MySQL'],
        'soft_skills': ['Problem Solving', 'Team Collaboration', 'Communication'],
    },
    'INFORMATION TECHNOLOGY': {
        'programming': ['Python', 'Java', 'JavaScript', 'C'],
        'technologies': ['Web Development', 'SQL', 'REST APIs', 'Git'],
        'tools': ['VS Code', 'GitHub', 'Postman', 'MySQL'],
        'soft_skills': ['Problem Solving', 'Team Collaboration', 'Communication'],
    },
    'ECE': {
        'programming': ['C Programming', 'Python', 'MATLAB', 'Verilog'],
        'technologies': ['Embedded Systems', 'Digital Electronics', 'Signal Processing', 'PCB Design'],
        'tools': ['Keil', 'Proteus', 'MATLAB/Simulink', 'Arduino IDE'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Communication'],
    },
    'ELECTRONICS': {
        'programming': ['C Programming', 'Python', 'MATLAB', 'Verilog'],
        'technologies': ['Embedded Systems', 'Digital Electronics', 'Signal Processing', 'PCB Design'],
        'tools': ['Keil', 'Proteus', 'MATLAB/Simulink', 'Arduino IDE'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Communication'],
    },
    'ELECTRONICS AND COMMUNICATION': {
        'programming': ['C Programming', 'Python', 'MATLAB', 'Verilog'],
        'technologies': ['Embedded Systems', 'Digital Electronics', 'Signal Processing', 'PCB Design'],
        'tools': ['Keil', 'Proteus', 'MATLAB/Simulink', 'Arduino IDE'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Communication'],
    },
    'EEE': {
        'programming': ['C Programming', 'Python', 'MATLAB'],
        'technologies': ['Circuit Design', 'Power Systems', 'Electrical Machines', 'Control Systems'],
        'tools': ['MATLAB/Simulink', 'AutoCAD Electrical', 'Multisim', 'ETAP'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Communication'],
    },
    'ELECTRICAL': {
        'programming': ['C Programming', 'Python', 'MATLAB'],
        'technologies': ['Circuit Design', 'Power Systems', 'Electrical Machines', 'Control Systems'],
        'tools': ['MATLAB/Simulink', 'AutoCAD Electrical', 'Multisim', 'ETAP'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Communication'],
    },
    'ELECTRICAL AND ELECTRONICS': {
        'programming': ['C Programming', 'Python', 'MATLAB'],
        'technologies': ['Circuit Design', 'Power Systems', 'Electrical Machines', 'Control Systems'],
        'tools': ['MATLAB/Simulink', 'AutoCAD Electrical', 'Multisim', 'ETAP'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Communication'],
    },
    'MECH': {
        'programming': ['C Programming', 'Python', 'MATLAB'],
        'technologies': ['CAD/CAM', 'Thermodynamics', 'Fluid Mechanics', 'Finite Element Analysis'],
        'tools': ['AutoCAD', 'SolidWorks', 'CATIA', 'ANSYS'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Problem Solving'],
    },
    'MECHANICAL': {
        'programming': ['C Programming', 'Python', 'MATLAB'],
        'technologies': ['CAD/CAM', 'Thermodynamics', 'Fluid Mechanics', 'Finite Element Analysis'],
        'tools': ['AutoCAD', 'SolidWorks', 'CATIA', 'ANSYS'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Problem Solving'],
    },
    'CIVIL': {
        'programming': ['C Programming', 'Python', 'AutoCAD'],
        'technologies': ['Structural Analysis', 'Surveying', 'Geotechnical Engineering', 'RCC Design'],
        'tools': ['AutoCAD', 'STAAD.Pro', 'ETABS', 'Primavera'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Project Management'],
    },
    'CHEM': {
        'programming': ['C Programming', 'Python', 'MATLAB'],
        'technologies': ['Process Control', 'Reaction Engineering', 'Mass Transfer', 'Heat Transfer'],
        'tools': ['ASPEN Plus', 'HYSYS', 'MATLAB', 'AutoCAD'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Problem Solving'],
    },
    'CHEMICAL': {
        'programming': ['C Programming', 'Python', 'MATLAB'],
        'technologies': ['Process Control', 'Reaction Engineering', 'Mass Transfer', 'Heat Transfer'],
        'tools': ['ASPEN Plus', 'HYSYS', 'MATLAB', 'AutoCAD'],
        'soft_skills': ['Analytical Thinking', 'Team Collaboration', 'Problem Solving'],
    },
    'DEFAULT': {
        'programming': ['C Programming', 'Python'],
        'technologies': ['Problem Solving', 'Data Analysis'],
        'tools': ['MS Office', 'Git'],
        'soft_skills': ['Team Collaboration', 'Communication', 'Analytical Thinking'],
    },
}


def _get_branch_skills(branch: str) -> dict:
    """Return branch-appropriate default skills."""
    branch_upper = (branch or '').upper().strip()
    # Try exact match first
    if branch_upper in BRANCH_SKILL_MAPPING:
        return BRANCH_SKILL_MAPPING[branch_upper]
    # Try substring match
    for key in BRANCH_SKILL_MAPPING:
        if key in branch_upper or branch_upper in key:
            return BRANCH_SKILL_MAPPING[key]
    return BRANCH_SKILL_MAPPING['DEFAULT']


def _format_internship_text(internships_raw) -> str:
    """
    Convert raw internship value to a clean, resume-appropriate description.
    Handles: None, '', '0', 0, 'None', actual text descriptions, company names.
    """
    if internships_raw is None:
        return None
    
    raw = str(internships_raw).strip()
    
    # Explicitly empty / zero / null-like values → no internship
    if raw in ('', '0', 'None', 'none', 'N/A', 'n/a', 'NA', 'na', 'nil', 'Nil', '-', '--'):
        return None
    
    # If it's just a number > 0, return generic text
    try:
        count = int(raw)
        if count <= 0:
            return None
        # Don't say "2 internships" — just say gained experience
        return "Gained practical industry exposure through internship experience"
    except ValueError:
        pass
    
    # If it already contains descriptive text, clean it up
    lower = raw.lower()
    
    # Looks like a company name or role description
    if len(raw) > 2:
        # If it mentions "intern" already, just return as-is (trimmed)
        if 'intern' in lower:
            return raw.rstrip('.')
        # If it looks like a company name, frame it nicely
        return f"Completed internship at {raw}"
    
    return None


class ResumeGenerator:
    """Generate professional resume content."""

    def __init__(self):
        self.client = client

    # ------------------------------------------------------------------
    # PROFESSIONAL SUMMARY
    # ------------------------------------------------------------------
    def generate_summary(self, user_data, strengths, certificates):
        """Generate a clean professional summary — no AI/quiz/assessment mentions."""
        branch = user_data.get('branch', 'Engineering')
        cgpa   = user_data.get('cgpa', '')
        internship_text = _format_internship_text(user_data.get('internships', ''))

        # Build experience clause
        if internship_text:
            experience_clause = f"Gained practical industry exposure through hands-on internship experience."
        else:
            experience_clause = "Passionate about applying theoretical knowledge to practical engineering challenges."

        # Skills clause — use top 2–3 branch-relevant strengths
        if strengths and len(strengths) >= 2:
            skills_clause = f"Demonstrates strong proficiency in {strengths[0]} and {strengths[1]}"
            if len(strengths) >= 3:
                skills_clause += f", with working knowledge of {strengths[2]}"
            skills_clause += "."
        elif strengths:
            skills_clause = f"Demonstrates foundational knowledge in {strengths[0]}."
        else:
            # Fall back to branch-level default skills
            branch_skills = _get_branch_skills(branch)
            default_skills = branch_skills.get('technologies', [])[:2]
            if default_skills:
                skills_clause = f"Building expertise in core {branch} subjects including {' and '.join(default_skills)}."
            else:
                skills_clause = f"Committed to developing technical expertise relevant to the {branch} domain."

        cgpa_clause = f" with a CGPA of {cgpa}" if cgpa else ""

        summary = (
            f"Dedicated {branch} student{cgpa_clause}, equipped with a strong technical foundation "
            f"and a problem-solving mindset. {skills_clause} "
            f"{experience_clause} "
            f"Eager to contribute meaningfully to a dynamic organization and grow as an engineer."
        )

        # Try AI enhancement
        if self.client:
            try:
                prompt = f"""Rewrite this professional resume summary for a {branch} student.
Keep it to 3 sentences. Be professional and specific to {branch} engineering.
Do NOT mention AI, quizzes, assessments, or performance data.
Do NOT mention number of internships.
{"Mention some practical experience gained through an internship." if internship_text else "Do not mention internships at all."}
Only output the summary text, nothing else.

Base summary: {summary}"""
                response = self.client.models.generate_content(
                    model='gemini-2.0-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(max_output_tokens=300, temperature=0.6)
                )
                ai_text = response.text.strip()
                # Safety: remove any AI/quiz mentions that slipped through
                for bad in ['AI-powered', 'AI-generated', 'quiz', 'assessment', 'internships']:
                    ai_text = ai_text.replace(bad, '')
                # Remove double spaces left behind
                import re
                ai_text = re.sub(r'  +', ' ', ai_text).strip()
                if len(ai_text) > 80:
                    return ai_text
            except Exception as e:
                print(f"AI summary generation failed: {e}")

        return summary

    # ------------------------------------------------------------------
    # PROJECTS
    # ------------------------------------------------------------------
    def generate_project_ideas(self, branch, strengths, count=3):
        """Generate branch-appropriate project ideas."""
        prompt = f"""Suggest {count} realistic technical projects for a {branch} engineering student 
skilled in: {', '.join(strengths[:3]) if strengths else branch + ' fundamentals'}.

Each project should be clearly relevant to {branch} engineering — NOT generic software projects 
unless the branch is CSE/IT.

For each project:
- Name: specific and professional (no "AI-powered" prefix)
- Description: 2 sentences — what was built and its practical impact
- Technologies: 3-4 relevant tools/languages/software

IMPORTANT: Return ONLY valid JSON, no markdown backticks, no explanation.
{{"projects": [{{"name": "...", "description": "...", "technologies": ["...", "..."]}}]}}"""

        try:
            if not self.client:
                raise Exception("Client not initialized")
            response = self.client.models.generate_content(
                model='gemini-2.0-flash',
                contents=prompt,
                config=types.GenerateContentConfig(max_output_tokens=1024, temperature=0.8)
            )
            text = response.text.strip()
            if '```json' in text:
                text = text.split('```json')[1].split('```')[0].strip()
            elif '```' in text:
                text = text.split('```')[1].split('```')[0].strip()
            import json
            data = json.loads(text)
            return data.get('projects', [])
        except Exception as e:
            print(f"Error generating projects: {e}")
            return self._fallback_projects(branch, strengths)

    def _fallback_projects(self, branch, strengths):
        """Branch-appropriate fallback projects when AI is unavailable."""
        branch_upper = (branch or '').upper()
        
        if any(b in branch_upper for b in ['CSE', 'COMPUTER', 'IT', 'INFORMATION']):
            return [
                {
                    "name": "Student Management System",
                    "description": "Developed a web-based system for managing student records with CRUD operations. Implemented user authentication, role-based access, and report generation.",
                    "technologies": strengths[:3] if len(strengths) >= 3 else ["Python", "Flask", "MySQL"]
                },
                {
                    "name": "Inventory Tracking Application",
                    "description": "Built a desktop application to track inventory levels and generate alerts for low stock. Reduced manual tracking effort by automating restocking notifications.",
                    "technologies": ["Java", "MySQL", "JavaFX"]
                }
            ]
        elif any(b in branch_upper for b in ['ECE', 'ELECTRONICS']):
            return [
                {
                    "name": "Smart Home Automation System",
                    "description": "Designed an IoT-based home automation system using Arduino and wireless sensors. Enabled remote control of appliances via mobile application.",
                    "technologies": ["Arduino", "ESP8266", "C Programming", "Proteus"]
                },
                {
                    "name": "Digital Signal Processing Filter",
                    "description": "Implemented FIR and IIR filters in MATLAB to remove noise from audio signals. Validated filter performance through frequency response analysis.",
                    "technologies": ["MATLAB", "Simulink", "Signal Processing Toolbox"]
                }
            ]
        elif any(b in branch_upper for b in ['MECH', 'MECHANICAL']):
            return [
                {
                    "name": "Design and Analysis of Connecting Rod",
                    "description": "Performed structural analysis of an IC engine connecting rod under cyclic loading. Optimized material selection to achieve a 15% weight reduction while maintaining safety factor.",
                    "technologies": ["SolidWorks", "ANSYS", "AutoCAD"]
                },
                {
                    "name": "Heat Exchanger Design",
                    "description": "Designed a shell-and-tube heat exchanger for an industrial cooling application. Used LMTD method to size the exchanger and validated results with MATLAB simulation.",
                    "technologies": ["MATLAB", "AutoCAD", "MS Excel"]
                }
            ]
        elif any(b in branch_upper for b in ['EEE', 'ELECTRICAL']):
            return [
                {
                    "name": "Solar-Powered LED Street Light",
                    "description": "Designed an automatic solar-powered street light system with daylight sensing. Integrated a charge controller and battery backup for uninterrupted operation.",
                    "technologies": ["Multisim", "AutoCAD Electrical", "MATLAB"]
                },
                {
                    "name": "DC Motor Speed Control",
                    "description": "Implemented PWM-based speed control for a DC motor using a microcontroller. Achieved precise RPM regulation through closed-loop PID feedback.",
                    "technologies": ["Arduino", "MATLAB/Simulink", "Proteus"]
                }
            ]
        elif 'CIVIL' in branch_upper:
            return [
                {
                    "name": "Residential Building Structural Design",
                    "description": "Designed the RCC structural framework for a G+2 residential building. Performed load calculations, beam-column design, and footing design as per IS 456 standards.",
                    "technologies": ["STAAD.Pro", "AutoCAD", "MS Excel"]
                },
                {
                    "name": "Road Alignment and Profile Design",
                    "description": "Prepared horizontal and vertical alignment of a 2 km rural road stretch. Designed drainage structures and estimated material quantities using survey data.",
                    "technologies": ["AutoCAD Civil 3D", "Primavera"]
                }
            ]
        else:
            return [
                {
                    "name": f"{branch} Process Optimization Study",
                    "description": f"Conducted a detailed study to identify inefficiencies in a standard {branch.lower()} process. Proposed and validated improvement measures that reduced operational time by 20%.",
                    "technologies": ["Python", "MS Excel", "AutoCAD"]
                }
            ]

    # ------------------------------------------------------------------
    # SKILLS ORGANISATION
    # ------------------------------------------------------------------
    def organize_skills(self, strengths, certificates, all_topics, branch=''):
        """
        Build skills sections using:
        1. Branch-appropriate defaults
        2. Topics the student has actually quizzed on (filtered to branch relevance)
        3. Certificate-derived skills
        """
        branch_defaults = _get_branch_skills(branch)
        
        programming  = list(branch_defaults.get('programming',  []))
        technologies = list(branch_defaults.get('technologies', []))
        tools        = list(branch_defaults.get('tools',        []))
        soft_skills  = list(branch_defaults.get('soft_skills',  []))

        # Skill mapping from quiz topics → resume skills
        TOPIC_SKILL_MAP = {
            'C': ['C Programming'],
            'C++': ['C++ Programming', 'Object-Oriented Programming'],
            'Java': ['Java', 'Object-Oriented Programming'],
            'Python': ['Python'],
            'DBMS': ['SQL', 'Database Management'],
            'OS': ['Operating Systems'],
            'Data Structures': ['Data Structures', 'Algorithms'],
            'Algorithms': ['Algorithms', 'Complexity Analysis'],
            'OOP': ['Object-Oriented Programming', 'Design Patterns'],
            'Web Development': ['HTML/CSS', 'JavaScript', 'REST APIs'],
            'Computer Networks': ['Computer Networks', 'TCP/IP'],
            'Machine Learning': ['Machine Learning', 'Scikit-learn'],
            'Python': ['Python', 'NumPy', 'Pandas'],
            'Digital Electronics': ['Digital Electronics', 'Logic Design'],
            'Embedded Systems': ['Embedded C', 'Arduino', 'Microcontrollers'],
            'VLSI': ['Verilog', 'VLSI Design'],
            'MATLAB': ['MATLAB', 'Simulink'],
            'AutoCAD': ['AutoCAD 2D/3D'],
            'CAD/CAM': ['SolidWorks', 'AutoCAD', 'CATIA'],
            'Thermodynamics': ['Thermodynamics', 'Heat Transfer'],
            'Fluid Mechanics': ['Fluid Mechanics', 'CFD Basics'],
            'Circuit Theory': ['Circuit Analysis', 'Network Theory'],
            'Power Systems': ['Power Systems', 'Electrical Machines'],
            'Structural Analysis': ['Structural Analysis', 'STAAD.Pro'],
            'Concrete Technology': ['RCC Design', 'IS Code Standards'],
        }

        # Add quiz-derived skills for topics student performed well in
        for topic in (strengths or []):
            base_topic = topic.split(' - ')[0].strip() if ' - ' in topic else topic.strip()
            mapped = TOPIC_SKILL_MAP.get(base_topic, [])
            for skill in mapped:
                if skill not in programming and skill not in technologies:
                    technologies.append(skill)

        # Certificate-derived skills (safe extraction)
        for cert in (certificates or []):
            cert_name = (cert.get('name', '') or '').lower()
            if 'python' in cert_name and 'Python' not in programming:
                programming.append('Python')
            if any(x in cert_name for x in ['web', 'html', 'css']) and 'HTML/CSS' not in technologies:
                technologies.append('HTML/CSS')
            if 'sql' in cert_name or 'database' in cert_name:
                if 'SQL' not in technologies:
                    technologies.append('SQL')
            if 'aws' in cert_name or 'cloud' in cert_name:
                if 'Cloud Computing' not in technologies:
                    technologies.append('Cloud Computing')

        # Deduplicate while preserving order
        def dedup(lst):
            seen = set()
            result = []
            for x in lst:
                if x not in seen:
                    seen.add(x)
                    result.append(x)
            return result

        return {
            'programming':  dedup(programming)[:8],
            'technologies': dedup(technologies)[:8],
            'tools':        dedup(tools)[:6],
            'soft_skills':  dedup(soft_skills)[:4],
        }

    # ------------------------------------------------------------------
    # ACHIEVEMENTS
    # ------------------------------------------------------------------
    def generate_achievements(self, scores_data, readiness, certificates, user_data):
        """
        Generate realistic achievements:
        - No mention of quizzes/assessments/AI
        - No revealing raw internship counts
        - Relevant to the student's actual profile
        """
        achievements = []
        branch = user_data.get('branch', 'Engineering')
        cgpa   = float(user_data.get('cgpa', 0) or 0)
        internship_text = _format_internship_text(user_data.get('internships', ''))

        # CGPA-based achievement
        if cgpa >= 8.5:
            achievements.append(
                f"Maintained a CGPA of {cgpa}, ranking among the top performers in the department."
            )
        elif cgpa >= 7.5:
            achievements.append(
                f"Achieved a consistent CGPA of {cgpa} throughout the academic program."
            )
        elif cgpa > 0:
            achievements.append(
                f"Pursuing Bachelor of Technology with a CGPA of {cgpa}."
            )

        # Internship achievement (only if they actually did one)
        if internship_text:
            achievements.append(
                "Gained industry exposure through an internship, applying classroom concepts to real-world engineering problems."
            )

        # Certificate achievements (from actual uploaded certificates)
        for cert in (certificates or [])[:2]:
            cert_name   = cert.get('name', '')
            cert_issuer = cert.get('issuer', '')
            if cert_name:
                if cert_issuer:
                    achievements.append(
                        f"Earned the '{cert_name}' certification from {cert_issuer}, demonstrating competency in the subject area."
                    )
                else:
                    achievements.append(
                        f"Completed the '{cert_name}' certification program."
                    )

        # Topic mastery achievement (based on quiz performance, but phrased generically)
        if scores_data:
            strong_topics = []
            topic_perf = {}
            for s in scores_data:
                t = s.get('topic', '')
                if t and t.lower() != 'grand test':
                    if t not in topic_perf:
                        topic_perf[t] = {'score': 0, 'total': 0}
                    topic_perf[t]['score'] += s.get('score', 0)
                    topic_perf[t]['total'] += s.get('total_questions', 1)
            for topic, perf in topic_perf.items():
                if perf['total'] > 0 and (perf['score'] / perf['total']) >= 0.75:
                    strong_topics.append(topic)
            if strong_topics:
                topics_str = ' and '.join(strong_topics[:2])
                achievements.append(
                    f"Developed strong technical proficiency in {topics_str} through dedicated self-study and practice."
                )

        # Generic participation achievement
        achievements.append(
            f"Actively participated in technical workshops and seminars related to {branch} engineering."
        )

        return achievements[:5]


# ============================================================================
# HELPERS
# ============================================================================

def analyze_user_for_resume(user_data, scores_data, certificates):
    """Analyze user profile and quiz performance to identify strengths."""
    branch = user_data.get('branch', 'Engineering')
    
    topic_performance = {}
    for score in scores_data:
        key = score['topic']
        if score.get('subtopic'):
            key = f"{score['topic']} - {score['subtopic']}"
        if key.lower() == 'grand test':
            continue
        if key not in topic_performance:
            topic_performance[key] = {'score': 0, 'total': 0}
        topic_performance[key]['score'] += score['score']
        topic_performance[key]['total'] += score['total_questions']

    strengths    = []
    all_topics   = []
    for topic, perf in topic_performance.items():
        all_topics.append(topic)
        if perf['total'] > 0 and (perf['score'] / perf['total']) * 100 >= 60:
            strengths.append((topic, (perf['score'] / perf['total']) * 100))

    strengths.sort(key=lambda x: x[1], reverse=True)
    strength_topics = [s[0] for s in strengths]

    # Readiness score
    if scores_data:
        total_score     = sum(s['score'] for s in scores_data if s.get('topic', '').lower() != 'grand test')
        total_questions = sum(s['total_questions'] for s in scores_data if s.get('topic', '').lower() != 'grand test')
        readiness_score  = (total_score / total_questions * 100) if total_questions > 0 else 0

        if readiness_score >= 80:
            readiness_status = 'Excellent'
        elif readiness_score >= 65:
            readiness_status = 'Good'
        else:
            readiness_status = 'Developing'
    else:
        readiness_score  = 0
        readiness_status = 'Not Assessed'

    return {
        'strengths':   strength_topics,
        'all_topics':  all_topics,
        'branch':      branch,
        'readiness': {
            'score':  round(readiness_score, 1),
            'status': readiness_status,
        },
    }


def generate_complete_resume(user_data, scores_data, certificates=None):
    """Generate complete resume data structure."""
    if certificates is None:
        certificates = []

    generator = ResumeGenerator()
    analysis  = analyze_user_for_resume(user_data, scores_data, certificates)
    branch    = user_data.get('branch', 'Engineering')

    # Generate all sections
    professional_summary = generator.generate_summary(
        user_data, analysis['strengths'], certificates
    )
    projects     = generator.generate_project_ideas(branch, analysis['strengths'], 3)
    skills       = generator.organize_skills(
        analysis['strengths'], certificates, analysis['all_topics'], branch
    )
    achievements = generator.generate_achievements(
        scores_data, analysis['readiness'], certificates, user_data
    )

    resume_data = {
        'personal_info': {
            'name':    user_data['name'],
            'email':   user_data['email'],
            'branch':  branch,
            'cgpa':    user_data['cgpa'],
            'phone':   user_data.get('phone', ''),
            'linkedin': user_data.get('linkedin', ''),
            'github':   user_data.get('github', ''),
        },
        'summary':  professional_summary,
        'education': {
            'degree':   f"Bachelor of Technology in {branch}",
            'cgpa':     user_data['cgpa'],
            'backlogs': user_data.get('backlogs', 0),
            'year':     datetime.now().year + 1,  # expected graduation next year typically
        },
        'skills':       skills,
        'projects':     projects,
        'internships':  _format_internship_text(user_data.get('internships', '')),
        'certificates': certificates,
        'achievements': achievements,
        'readiness':    analysis['readiness'],
    }

    return resume_data