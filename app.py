from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
import os
from dotenv import load_dotenv
from ml_model import analyze_user_performance, get_overall_readiness
from ai_question_generator import get_adaptive_questions
from resume_generator import generate_complete_resume 
load_dotenv()
from werkzeug.utils import secure_filename
from certificate_manager import CertificateManager
import json
app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

SUPABASE_URL = os.getenv('VITE_SUPABASE_URL')
SUPABASE_KEY = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Initialize certificate manager
cert_manager = CertificateManager()

# Configure upload settings
UPLOAD_FOLDER = 'static/certificates'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB
# Branch-specific technical topics
BRANCH_TOPICS = {
    'CSE': ['C', 'Java', 'Python', 'DBMS', 'OS', 'Data Structures', 'Algorithms', 'Computer Networks', 'OOP'],
    'IT': ['C', 'Java', 'Python', 'DBMS', 'Web Development', 'Data Structures', 'Networking', 'Cloud Computing'],
    'ECE': ['C', 'Python', 'Digital Electronics', 'Signal Processing', 'Embedded Systems', 'VLSI', 'Microprocessors'],
    'EEE': ['C', 'Python', 'Circuit Theory', 'Power Systems', 'Control Systems', 'Electrical Machines'],
    'MECH': ['C', 'Python', 'Thermodynamics', 'Mechanics', 'Manufacturing', 'CAD/CAM'],
    'CIVIL': ['C', 'AutoCAD', 'Structural Analysis', 'Surveying', 'Construction Management'],
    'AI/ML': ['Python', 'Machine Learning', 'Deep Learning', 'Data Structures', 'Statistics', 'Neural Networks'],
    'DEFAULT': ['C', 'Java', 'Python', 'DBMS', 'OS', 'Data Structures']
}

def get_user_branch():
    if 'user_email' not in session:
        return 'DEFAULT'

    result = supabase.table('users').select('branch').eq('email', session['user_email']).execute()

    if result.data:
        branch = result.data[0]['branch'].upper()
        for key in BRANCH_TOPICS.keys():
            if key in branch or branch in key:
                return key

    return 'DEFAULT'

def generate_topic_recommendations(topic, subtopic, percent, difficulty, user_email, supabase_client):
    recommendations = {
        'current_topic': subtopic if subtopic else topic,
        'next_steps': [],
        'related_topics': [],
        'resources': []
    }

    result = supabase_client.table('user_scores').select('score, total_questions').eq('user_email', user_email).eq('topic', topic).eq('subtopic', subtopic or '').execute()

    if result.data:
        total_score = sum(row['score'] for row in result.data)
        total_questions = sum(row['total_questions'] for row in result.data)
        attempt_count = len(result.data)
        avg_percent = (total_score / total_questions * 100) if total_questions > 0 else 0
    else:
        avg_percent = 0
        attempt_count = 1

    if percent < 40:
        recommendations['next_steps'].append(f"Review fundamental concepts of {subtopic if subtopic else topic}")
        recommendations['next_steps'].append(f"Practice more beginner-level questions")
        recommendations['next_steps'].append(f"Focus on understanding basic syntax and concepts")
    elif percent < 60:
        recommendations['next_steps'].append(f"Continue practicing {subtopic if subtopic else topic}")
        recommendations['next_steps'].append(f"Review questions you got wrong")
        recommendations['next_steps'].append(f"Try solving problems with different approaches")
    elif percent < 80:
        recommendations['next_steps'].append(f"You're doing well! Try more challenging questions")
        recommendations['next_steps'].append(f"Explore advanced concepts in {subtopic if subtopic else topic}")
    else:
        recommendations['next_steps'].append(f"Excellent work! You've mastered {subtopic if subtopic else topic}")
        recommendations['next_steps'].append(f"Challenge yourself with advanced problems")

    related_topics_map = {
        'C': {'Arrays': ['Pointers', 'Loops'], 'Pointers': ['Arrays', 'Functions'],
              'Loops': ['Functions', 'Arrays'], 'Functions': ['Pointers', 'Loops']},
        'Java': {'OOPs': ['Inheritance', 'Exceptions'], 'Inheritance': ['OOPs', 'Exceptions'],
                 'Exceptions': ['OOPs', 'Inheritance']},
        'Python': {'Lists': ['Dictionaries', 'File Handling'], 'Dictionaries': ['Lists', 'File Handling'],
                   'File Handling': ['Lists', 'Dictionaries']},
        'DBMS': {'SQL': ['Normalization', 'Transactions'], 'Normalization': ['SQL', 'Transactions'],
                 'Transactions': ['SQL', 'Normalization']},
        'OS': {'Processes': ['Threads', 'Memory Management'], 'Threads': ['Processes', 'Memory Management'],
               'Memory Management': ['Processes', 'Threads']},
        'Data Structures': {'Linked List': ['Stacks', 'Queues'], 'Stacks': ['Queues', 'Trees'],
                           'Queues': ['Stacks', 'Trees'], 'Trees': ['Linked List', 'Stacks']}
    }

    if topic in related_topics_map and subtopic in related_topics_map[topic]:
        recommendations['related_topics'] = related_topics_map[topic][subtopic]

    recommendations['performance_summary'] = {
        'current_score': percent,
        'average_score': avg_percent,
        'attempts': attempt_count,
        'difficulty_level': difficulty,
        'trend': 'improving' if percent > avg_percent else 'needs_focus' if percent < avg_percent else 'stable'
    }

    return recommendations

# ---------------- ROUTES ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        branch = request.form['branch']
        cgpa = request.form['cgpa']
        backlogs = request.form['backlogs']
        internships = request.form['internships']
        password = request.form['password']

        try:
            supabase.table('users').insert({
                'name': name,
                'email': email,
                'branch': branch,
                'cgpa': float(cgpa),
                'backlogs': int(backlogs),
                'internships': internships,
                'password': password
            }).execute()
            flash("Registration successful! Please login.")
            return redirect(url_for('index'))
        except Exception as e:
            flash(f"Registration failed: {str(e)}")
            return redirect(url_for('register'))
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    result = supabase.table('users').select('*').eq('email', email).eq('password', password).execute()

    if result.data:
        user = result.data[0]
        session['user'] = user['name']
        session['user_email'] = user['email']
        session['user_branch'] = user['branch']
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password.")
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_email', None)
    session.pop('user_branch', None)
    flash("Logged out successfully.")
    return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        return render_template('dashboard.html', user=session['user'])
    return redirect(url_for('index'))


@app.route('/technical')
def technical():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_branch = get_user_branch()
    topics = BRANCH_TOPICS.get(user_branch, BRANCH_TOPICS['DEFAULT'])
    
    return render_template('technical.html', topics=topics, branch=session.get('user_branch', 'N/A'))


@app.route('/technical/<topic>')
def subtopics(topic):
    subtopic_map = {
        'C': ['Arrays', 'Pointers', 'Loops', 'Functions'],
        'Java': ['OOPs', 'Inheritance', 'Exceptions'],
        'Python': ['Lists', 'Dictionaries', 'File Handling'],
        'DBMS': ['SQL', 'Normalization', 'Transactions'],
        'OS': ['Processes', 'Threads', 'Memory Management'],
        'Data Structures': ['Linked List', 'Stacks', 'Queues', 'Trees'],
        'Algorithms': ['Sorting', 'Searching', 'Dynamic Programming'],
        'Computer Networks': ['OSI Model', 'TCP/IP', 'Routing'],
        'OOP': ['Classes', 'Inheritance', 'Polymorphism'],
        'Web Development': ['HTML/CSS', 'JavaScript', 'Backend'],
        'Networking': ['Protocols', 'Security', 'Troubleshooting'],
        'Cloud Computing': ['AWS', 'Azure', 'Docker'],
        'Digital Electronics': ['Logic Gates', 'Combinational Circuits', 'Sequential Circuits'],
        'Signal Processing': ['Fourier Transform', 'Filters', 'Sampling'],
        'Embedded Systems': ['Microcontrollers', 'Sensors', 'Programming'],
        'VLSI': ['Design', 'Verification', 'Testing'],
        'Microprocessors': ['8086', 'Architecture', 'Assembly'],
        'Circuit Theory': ['Kirchhoff Laws', 'Network Theorems', 'AC Circuits'],
        'Power Systems': ['Generation', 'Transmission', 'Distribution'],
        'Control Systems': ['Transfer Functions', 'Stability', 'Controllers'],
        'Electrical Machines': ['DC Machines', 'Transformers', 'Induction Motors'],
        'Thermodynamics': ['Laws', 'Heat Transfer', 'Entropy'],
        'Mechanics': ['Statics', 'Dynamics', 'Strength of Materials'],
        'Manufacturing': ['Casting', 'Welding', 'Machining'],
        'CAD/CAM': ['AutoCAD', '3D Modeling', 'CNC'],
        'AutoCAD': ['2D Drawing', '3D Modeling', 'Commands'],
        'Structural Analysis': ['Beams', 'Trusses', 'Frames'],
        'Surveying': ['Leveling', 'Theodolite', 'GPS'],
        'Construction Management': ['Planning', 'Scheduling', 'Cost Estimation'],
        'Machine Learning': ['Supervised Learning', 'Unsupervised Learning', 'Neural Networks'],
        'Deep Learning': ['CNN', 'RNN', 'Transfer Learning'],
        'Statistics': ['Probability', 'Hypothesis Testing', 'Regression'],
        'Neural Networks': ['Perceptron', 'Backpropagation', 'Activation Functions']
    }
    subtopics = subtopic_map.get(topic, [])
    return render_template('subtopics.html', topic=topic, subtopics=subtopics)


@app.route('/aptitude')
def aptitude():
    topics = ['Quantitative Aptitude', 'Logical Reasoning', 'Data Interpretation']
    return render_template('aptitude.html', topics=topics)


@app.route('/english')
def english():
    topics = ['Grammar', 'Reading Comprehension', 'Synonyms & Antonyms']
    return render_template('english.html', topics=topics)


# Key changes needed in app.py

# 1. Update the quiz route to use AI for ALL topics (around line 300)
@app.route('/quiz/<topic>', methods=['GET', 'POST'])
@app.route('/quiz/<topic>/<subtopic>', methods=['GET', 'POST'])
def quiz(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))

    # Get user scores for adaptive difficulty
    result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', session['user_email']).execute()

    user_scores = []
    for row in result.data:
        user_scores.append({
            'topic': row['topic'],
            'subtopic': row['subtopic'],
            'score': row['score'],
            'total_questions': row['total_questions']
        })
    
    try:
        # Use AI for ALL topics and subtopics
        ai_result = get_adaptive_questions(
            user_email=session['user_email'],
            topic=topic,
            subtopic=subtopic or '',
            user_scores=user_scores,
            num_questions=5
        )
        
        topic_questions = ai_result['questions']
        difficulty = ai_result['difficulty']
        ai_generated = True
        
        print(f"✅ Loaded {len(topic_questions)} AI-generated questions at {difficulty} level")
        
    except Exception as e:
        print(f"❌ Error loading AI questions: {e}")
        flash("Error loading quiz. Please try again.")
        return redirect(url_for('dashboard'))

    if not topic_questions:
        flash("No quiz available for this topic yet.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        score = 0
        user_answers = request.form

        print("\n" + "="*80)
        print("📝 SCORING DEBUG")
        print("="*80)
        
        for i, q in enumerate(topic_questions):
            user_answer = user_answers.get(f'q{i}', '')
            correct_answer = str(q['answer'])
            
            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            
            if is_correct:
                score += 1
            
            print(f"Q{i+1}: User='{user_answer}' | Correct='{correct_answer}' | Match={is_correct}")

        print(f"\n📊 FINAL: {score}/{len(topic_questions)}")

        # Save score to database
        supabase.table('user_scores').insert({
            'user_email': session['user_email'],
            'topic': topic,
            'subtopic': subtopic or '',
            'score': score,
            'total_questions': len(topic_questions)
        }).execute()

        percent = (score / len(topic_questions)) * 100

        # Generate feedback
        if percent < 40:
            suggestion = f"Your score is {percent:.1f}%. You need significant practice in {subtopic if subtopic else topic}."
            performance = "needs_work"
        elif percent < 60:
            suggestion = f"Your score is {percent:.1f}%. Keep practicing {subtopic if subtopic else topic} to improve."
            performance = "fair"
        elif percent < 80:
            suggestion = f"Your score is {percent:.1f}%. Good work! A bit more practice will help you master {subtopic if subtopic else topic}."
            performance = "good"
        else:
            suggestion = f"Your score is {percent:.1f}%. Excellent! You have strong knowledge in {subtopic if subtopic else topic}."
            performance = "excellent"

        # Adaptive feedback
        if difficulty == 'beginner':
            if percent >= 80:
                suggestion += " 🎉 Great job on beginner questions! Next quiz will be at intermediate level."
            else:
                suggestion += " Keep practicing fundamentals to build a strong foundation."
        elif difficulty == 'intermediate':
            if percent >= 80:
                suggestion += " 🔥 Impressive! Next quiz will challenge you with advanced questions."
            else:
                suggestion += " You're making progress. Keep practicing at this level."
        else:
            if percent >= 80:
                suggestion += " 🏆 Outstanding! You've mastered this topic at expert level!"
            else:
                suggestion += " Advanced questions are challenging. Review concepts and try again."

        # Generate topic recommendations
        topic_recommendations = generate_topic_recommendations(
            topic, subtopic, percent, difficulty, session['user_email'], supabase
        )

        return render_template('quiz.html',
                             topic=topic,
                             subtopic=subtopic,
                             questions=topic_questions,
                             submitted=True,
                             score=score,
                             suggestion=suggestion,
                             difficulty=difficulty,
                             ai_generated=ai_generated,
                             performance=performance,
                             recommendations=topic_recommendations)

    return render_template('quiz.html', 
                         topic=topic, 
                         subtopic=subtopic,
                         questions=topic_questions, 
                         submitted=False,
                         difficulty=difficulty,
                         ai_generated=ai_generated)


# 2. Update Grand Test to use AI questions (around line 500)
@app.route('/grand_test', methods=['GET', 'POST'])
def grand_test():
    if 'user' not in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        all_questions = session.get('grand_test_questions', [])
        
        if not all_questions:
            flash("Grand Test session expired. Please start again.")
            return redirect(url_for('grand_test'))

        score = 0
        user_answers = request.form
        
        for i, q in enumerate(all_questions):
            user_answer = user_answers.get(f'q{i}', '')
            correct_answer = str(q['answer'])
            
            if user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1

        # Save to database
        supabase.table('user_scores').insert({
            'user_email': session['user_email'],
            'topic': 'Grand Test',
            'subtopic': '',
            'score': score,
            'total_questions': len(all_questions)
        }).execute()

        session.pop('grand_test_questions', None)

        percent = (score / len(all_questions)) * 100
        
        if percent < 40:
            suggestion = f"Your overall score is {percent:.1f}%. Focus on all core areas."
        elif percent < 60:
            suggestion = f"Your overall score is {percent:.1f}%. You're on the right track."
        elif percent < 80:
            suggestion = f"Your overall score is {percent:.1f}%. Good performance!"
        else:
            suggestion = f"Your overall score is {percent:.1f}%. Outstanding!"

        return render_template('grand_test.html', 
                             all_questions=all_questions, 
                             submitted=True, 
                             score=score, 
                             suggestion=suggestion)

    try:
        print("\n" + "="*80)
        print("🎯 GENERATING GRAND TEST - ALL AI QUESTIONS")
        print("="*80)

        # Get user scores for adaptive difficulty
        result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', session['user_email']).execute()

        user_scores = []
        for row in result.data:
            user_scores.append({
                'topic': row['topic'],
                'subtopic': row['subtopic'],
                'score': row['score'],
                'total_questions': row['total_questions']
            })

        all_questions = []

        from ai_question_generator import generate_quiz_questions, determine_difficulty_level
        
        # Technical Questions (5 questions)
        print("\n[1/3] Generating Technical Questions...")
        tech_difficulty = determine_difficulty_level(user_scores, 'Technical', None)
        tech_questions = generate_quiz_questions(
            'Technical', 
            'Programming & CS Fundamentals', 
            tech_difficulty, 
            5
        )
        all_questions.extend(tech_questions)
        print(f"✅ Added {len(tech_questions)} technical questions")

        # Aptitude Questions (5 questions)
        print("\n[2/3] Generating Aptitude Questions...")
        apt_difficulty = determine_difficulty_level(user_scores, 'Aptitude', None)
        apt_questions = generate_quiz_questions(
            'Quantitative Aptitude', 
            'Quantitative & Logical Reasoning', 
            apt_difficulty, 
            5
        )
        all_questions.extend(apt_questions)
        print(f"✅ Added {len(apt_questions)} aptitude questions")

        # English Questions (5 questions)
        print("\n[3/3] Generating English Questions...")
        eng_difficulty = determine_difficulty_level(user_scores, 'English', None)
        eng_questions = generate_quiz_questions(
            'Grammar', 
            'Grammar & Communication', 
            eng_difficulty, 
            5
        )
        all_questions.extend(eng_questions)
        print(f"✅ Added {len(eng_questions)} English questions")

        print(f"\n✅ TOTAL: {len(all_questions)} AI-generated questions")
        print("="*80)

        # Store in session
        session['grand_test_questions'] = all_questions

        return render_template('grand_test.html', 
                             all_questions=all_questions, 
                             submitted=False)

    except Exception as e:
        print(f"❌ Error generating Grand Test: {e}")
        import traceback
        traceback.print_exc()
        flash("Failed to generate Grand Test. Please try again.")
        return redirect(url_for('dashboard'))

@app.route('/suggestions')
def suggestions():
    if 'user' not in session:
        return redirect(url_for('index'))

    result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', session['user_email']).neq('topic', 'Grand Test').execute()

    scores_data = []
    for row in result.data:
        scores_data.append({
            'topic': row['topic'],
            'subtopic': row['subtopic'],
            'score': row['score'],
            'total_questions': row['total_questions']
        })

    ml_suggestions = analyze_user_performance(scores_data)
    readiness = get_overall_readiness(scores_data)

    return render_template('suggestions.html',
                         suggestions=ml_suggestions,
                         readiness=readiness)



@app.route('/resume_draft')
def resume_draft():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session.get('user_email')
    
    result = supabase.table('users').select('*').eq('email', user_email).execute()
    if not result.data:
        flash("User data not found!")
        return redirect(url_for('dashboard'))
    
    user_data = result.data[0]
    
    scores_result = supabase.table('user_scores').select('*').eq('user_email', user_email).execute()
    scores_data = [s for s in scores_result.data if s.get('topic', '').lower() != 'grand test'] if scores_result.data else []
    
    try:
        certs_result = supabase.table('user_certificates').select('*').eq('email', user_email).execute()
        certificates = certs_result.data if certs_result.data else []
    except:
        certificates = []
    
    resume_data = generate_complete_resume(user_data, scores_data, certificates)
    
    # Show beautiful resume display page
    return render_template('resume_draft.html', resume_data=resume_data)

@app.route('/resume_edit')
def resume_edit():
    # Same code as resume_draft but return different template
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_email = session.get('user_email')
    result = supabase.table('users').select('*').eq('email', user_email).execute()
    user_data = result.data[0]
    
    scores_result = supabase.table('user_scores').select('*').eq('user_email', user_email).execute()
    scores_data = [s for s in scores_result.data if s.get('topic', '').lower() != 'grand test'] if scores_result.data else []
    
    try:
        certs_result = supabase.table('user_certificates').select('*').eq('user_email', user_email).execute()
        certificates = certs_result.data if certs_result.data else []
    except:
        certificates = []
    
    resume_data = generate_complete_resume(user_data, scores_data, certificates)
    
    return render_template('resume_editor.html', resume_data=resume_data)

@app.route('/certificates/upload', methods=['POST'])
def upload_certificate():
    """Handle certificate file upload"""
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401
    
    if 'certificate_file' not in request.files:
        return {'error': 'No file uploaded'}, 400
    
    file = request.files['certificate_file']
    cert_name = request.form.get('cert_name', '')
    cert_issuer = request.form.get('cert_issuer', '')
    cert_date = request.form.get('cert_date', '')
    cert_id = request.form.get('cert_id', '')
    
    if not cert_name or not cert_issuer:
        return {'error': 'Certificate name and issuer are required'}, 400
    
    # Save file
    file_info = cert_manager.save_certificate(file, session['user_email'])
    
    if not file_info or 'error' in file_info:
        return {'error': file_info.get('error', 'Upload failed')}, 400
    
    # Save to database
    try:
        cert_data = {
            'user_email': session['user_email'],
            'name': cert_name,
            'issuer': cert_issuer,
            'date': cert_date,
            'credential_id': cert_id,
            'file_url': file_info['url'],
            'file_type': file_info['file_type'],
            'file_size': file_info['file_size'],
            'uploaded_at': file_info['uploaded_at']
        }
        
        result = supabase.table('user_certificates').insert(cert_data).execute()
        
        if result.data:
            return {
                'success': True,
                'certificate': result.data[0],
                'message': 'Certificate uploaded successfully'
            }, 200
        else:
            return {'error': 'Failed to save certificate to database'}, 500
            
    except Exception as e:
        # Clean up uploaded file if database save fails
        cert_manager.delete_certificate(file_info['filename'])
        return {'error': f'Database error: {str(e)}'}, 500
    
@app.route('/certificates/delete/<int:cert_id>', methods=['DELETE'])
def delete_certificate(cert_id):
    """Delete a certificate"""
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401
    
    try:
        # Get certificate info
        result = supabase.table('user_certificates').select('*').eq('id', cert_id).eq('user_email', session['user_email']).execute()
        
        if not result.data:
            return {'error': 'Certificate not found'}, 404
        
        cert = result.data[0]
        
        # Delete file
        filename = cert['file_url'].split('/')[-1]
        cert_manager.delete_certificate(filename)
        
        # Delete from database
        supabase.table('user_certificates').delete().eq('id', cert_id).execute()
        
        return {'success': True, 'message': 'Certificate deleted successfully'}, 200
        
    except Exception as e:
        return {'error': f'Error deleting certificate: {str(e)}'}, 500
@app.route('/resume/save', methods=['POST'])
def save_resume():
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401
    
    data = request.json
    user_email = session['user_email']
    
    try:
        # Update user info
        supabase.table('users').update({
            'name': data['personal_info']['name'],
            'email': data['personal_info']['email']
        }).eq('email', user_email).execute()
        
        return {'success': True}, 200
    except Exception as e:
        return {'error': str(e)}, 500
        
@app.route('/certificates/list', methods=['GET'])
def list_certificates():
    """Get all certificates for current user"""
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401
    
    try:
        result = supabase.table('user_certificates').select('*').eq('user_email', session['user_email']).order('uploaded_at', desc=True).execute()
        
        certificates = result.data if result.data else []
        
        return {'certificates': certificates}, 200
        
    except Exception as e:
        return {'error': f'Error fetching certificates: {str(e)}'}, 500
       
if __name__ == '__main__':
    app.run(debug=True)