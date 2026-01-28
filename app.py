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
from datetime import datetime
from validators import validate_email, validate_password
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
    'CSE': ['C', 'Java', 'Python', 'DBMS', 'OS', 'Data Structures', 'Algorithms', 'Computer Networks', 'OOP', 'Web Development', 'Cloud Computing'],
    
    'IT': ['C', 'Java', 'Python', 'DBMS', 'Web Development', 'Data Structures', 'Networking', 'Cloud Computing', 'Cybersecurity', 'Software Engineering'],
    
    'ECE': ['C', 'Python', 'Digital Electronics', 'Signal Processing', 'Embedded Systems', 'VLSI', 'Microprocessors', 'Communication Systems', 'Antenna Theory', 'Control Systems'],
    
    'EEE': ['C', 'Python', 'Circuit Theory', 'Power Systems', 'Control Systems', 'Electrical Machines', 'Power Electronics', 'Renewable Energy', 'Electrical Drives', 'Switchgear'],
    
    'MECH': ['C', 'Python', 'Thermodynamics', 'Mechanics', 'Manufacturing', 'CAD/CAM', 'Fluid Mechanics', 'Heat Transfer', 'Machine Design', 'Automobile Engineering'],
    
    'CIVIL': ['C', 'AutoCAD', 'Structural Analysis', 'Surveying', 'Construction Management', 'Geotechnical Engineering', 'Transportation Engineering', 'Environmental Engineering', 'Concrete Technology', 'Estimation & Costing'],
    
    'CHEM': ['C', 'Python', 'Chemical Thermodynamics', 'Fluid Mechanics', 'Process Control', 'Reaction Engineering', 'Mass Transfer', 'Heat Transfer', 'Process Equipment Design', 'Chemical Plant Design'],
    
    'AI/ML': ['Python', 'Machine Learning', 'Deep Learning', 'Data Structures', 'Statistics', 'Neural Networks', 'NLP', 'Computer Vision', 'Data Science', 'TensorFlow'],
    
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
@app.route('/api/branch_topics')
def get_branch_topics():
    """API endpoint to get topics for user's branch"""
    if 'user_email' not in session:
        return {'error': 'Not authenticated'}, 401
    
    branch_key = get_user_branch()
    topics = BRANCH_TOPICS.get(branch_key, BRANCH_TOPICS['DEFAULT'])
    
    return {
        'branch': branch_key,
        'topics': topics
    }

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
                           'Queues': ['Stacks', 'Trees'], 'Trees': ['Linked List', 'Stacks']},
        # Add these to existing subtopic_map:
        'Fluid Mechanics': {'Fluid Properties', 'Fluid Statics', 'Flow Measurement', 'Boundary Layer'},
        'Heat Transfer': {'Conduction', 'Convection', 'Radiation', 'Heat Exchangers'},
        'Machine Design': {'Design of Shafts', 'Gears', 'Bearings', 'Springs'},
        'Geotechnical Engineering': {'Soil Mechanics', 'Foundation Engineering', 'Slope Stability'},
        'Chemical Thermodynamics': {'Laws of Thermodynamics', 'Phase Equilibrium', 'Chemical Equilibrium'},
        'Process Control': {'Feedback Control', 'PID Controllers', 'Advanced Control'},
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
        email = request.form['email']
        password = request.form['password']
        
        # Validate email
        if not validate_email(email):
            flash("Please enter a valid email address")
            return redirect(url_for('register'))
        
        # Validate password
        is_valid, msg = validate_password(password)
        if not is_valid:
            flash(msg)
            return redirect(url_for('register'))
        name = request.form['name']
        branch = request.form['branch']
        cgpa = request.form['cgpa']
        backlogs = request.form['backlogs']
        internships = request.form['internships']
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
            error_str = str(e)
            # User-friendly error messages
            if '23505' in error_str or 'duplicate key' in error_str:
                flash("This email is already registered. Please login or use a different email.")
            else:
                flash("Registration failed. Please try again.")
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
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_email = session.get('user_email')
    
    # Get user profile
    user_result = supabase.table('users').select('*').eq('email', user_email).execute()
    user_profile = user_result.data[0] if user_result.data else None
    
    # Get branch and topics
    branch_key = get_user_branch()
    branch_topics = BRANCH_TOPICS.get(branch_key, BRANCH_TOPICS['DEFAULT'])
    
    # Get quiz data
    result = supabase.table('user_scores').select('*').eq('user_email', user_email).execute()
    
    total_quizzes = len(result.data) if result.data else 0
    
    if result.data:
        total_score = sum(s['score'] for s in result.data)
        total_questions = sum(s['total_questions'] for s in result.data)
        average_score = round((total_score / total_questions * 100), 1) if total_questions > 0 else 0
        
        # Calculate streak
        from datetime import datetime, timedelta
        dates = sorted([datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).date() 
                       for s in result.data], reverse=True)
        
        streak_days = 0
        if dates:
            current_date = datetime.now().date()
            for i, date in enumerate(dates):
                if i == 0:
                    if date == current_date or date == current_date - timedelta(days=1):
                        streak_days = 1
                    else:
                        break
                else:
                    if date == dates[i-1] - timedelta(days=1):
                        streak_days += 1
                    else:
                        break
    else:
        average_score = 0
        streak_days = 0
    
    return render_template('dashboard.html', 
                         user=session['user'],
                         user_profile=user_profile,
                         total_quizzes=total_quizzes,
                         average_score=average_score,
                         streak_days=streak_days,
                         branch_key=branch_key,
                         branch_topics=branch_topics)  # <-- PASS TOPICS

# Add this to your app.py

# Update the grand_test_details route
@app.route('/grand_test/details')
def grand_test_details():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_email = session['user_email']
    
    # Check for saved progress
    saved_progress = None
    has_saved = False
    saved_question = 0
    saved_time_left = "20:00"
    
    try:
        result = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()
        
        if result.data:
            saved_progress = result.data[0]
            has_saved = True
            saved_question = saved_progress['current_question']
            time_left_seconds = saved_progress['time_left']
            
            # Format time
            mins = time_left_seconds // 60
            secs = time_left_seconds % 60
            saved_time_left = f"{mins}:{secs:02d}"
    except Exception as e:
        print(f"Error checking saved progress: {e}")
    
    return render_template('grand_test_details.html',
                         has_saved_progress=has_saved,
                         saved_question=saved_question,
                         saved_time_left=saved_time_left)


# Update the grand_test route to handle resume/restart
@app.route('/grand_test', methods=['GET', 'POST'])
def grand_test():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session['user_email']
    
    # Handle resume or restart
    resume = request.args.get('resume') == 'true'
    restart = request.args.get('restart') == 'true'
    
    if restart:
        # Delete saved progress
        try:
            supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()
        except:
            pass
    
    # POST - Submit quiz
    if request.method == 'POST':
        all_questions = session.get('grand_test_questions', [])
    
        if not all_questions:
            flash("Grand Test session expired. Please start again.")
            return redirect(url_for('grand_test_details'))

        score = 0
        user_answers = request.form
    
        for i, q in enumerate(all_questions):
            user_answer = user_answers.get(f'q{i}', '')
            correct_answer = str(q['answer'])
        
            if user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1

        # Get user's score history for difficulty calculation
        result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', user_email).execute()
        user_scores = [{'topic': row['topic'], 'subtopic': row['subtopic'], 
                        'score': row['score'], 'total_questions': row['total_questions']} 
                       for row in result.data]
    
        from ai_question_generator import determine_difficulty_level
        difficulty = determine_difficulty_level(user_scores, 'Grand Test', '')
    
        # Save score WITH DIFFICULTY
        supabase.table('user_scores').insert({
            'user_email': user_email,
            'topic': 'Grand Test',
            'subtopic': '',
            'score': score,
            'total_questions': len(all_questions),
            'difficulty': difficulty
        }).execute()
        
        # Delete saved progress after submission
        try:
            supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()
        except:
            pass

        percent = (score / len(all_questions) * 100)
        
        if percent >= 80:
            suggestion = "Excellent! You're well-prepared for placements."
        elif percent >= 60:
            suggestion = "Good work! Review weak areas and practice more."
        else:
            suggestion = "Keep practicing. Focus on improving your fundamentals."

        return render_template('grand_test.html',
                             all_questions=all_questions,
                             submitted=True,
                             score=score,
                             suggestion=suggestion)

    # GET - Load or generate quiz
    saved_progress = None
    if resume and not restart:
        try:
            result = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()
            if result.data:
                saved_progress = result.data[0]
        except:
            pass
    
    if saved_progress:
        # Resume from saved
        all_questions = json.loads(saved_progress['questions'])
        current_question = saved_progress['current_question']
        time_left = saved_progress['time_left']
        saved_answers = json.loads(saved_progress['answers']) if saved_progress['answers'] else {}
    else:
        # Generate new questions
        try:
            print("\n" + "="*80)
            print("🎯 GENERATING GRAND TEST - ALL AI QUESTIONS")
            print("="*80)

            result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', user_email).execute()

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

            # Initialize variables for new test
            current_question = 0
            time_left = 1200  # 20 minutes
            saved_answers = {}

        except Exception as e:
            print(f"❌ Error generating Grand Test: {e}")
            import traceback
            traceback.print_exc()
            flash("Failed to generate Grand Test. Please try again.")
            return redirect(url_for('grand_test_details'))
    
    # Store in session
    session['grand_test_questions'] = all_questions
    
    return render_template('grand_test.html',
                         all_questions=all_questions,
                         submitted=False,
                         time_left=time_left,
                         current_question=current_question,
                         saved_answers=saved_answers)
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

@app.route('/quiz/<path:topic>/details')
@app.route('/quiz/<path:topic>/<path:subtopic>/details')
def quiz_details(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    user_email = session['user_email']
    
    # Decode URL encoding
    from urllib.parse import unquote
    topic = unquote(topic)
    if subtopic:
        subtopic = unquote(subtopic)
    
    print(f"Quiz Details: topic={topic}, subtopic={subtopic}")
    
    # Check for saved progress
    try:
        search_subtopic = subtopic if subtopic else ''
        saved = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', topic).eq('subtopic', search_subtopic).execute()
        has_saved = bool(saved.data)
        saved_question = saved.data[0]['current_question'] if has_saved else 0
        saved_time = saved.data[0]['time_left'] if has_saved else 900
        
        # Format time
        mins = saved_time // 60
        secs = saved_time % 60
        saved_time_left = f"{mins}:{secs:02d}"
        
    except Exception as e:
        print(f"Error checking saved progress: {e}")
        has_saved = False
        saved_question = 0
        saved_time_left = "15:00"
    
    # Get difficulty based on past performance
    try:
        result = supabase.table('user_scores').select('score, total_questions').eq('user_email', user_email).eq('topic', topic).eq('subtopic', subtopic or '').execute()
        
        user_scores = []
        for row in result.data:
            user_scores.append({
                'topic': topic,
                'subtopic': subtopic or '',
                'score': row['score'],
                'total_questions': row['total_questions']
            })
        
        from ai_question_generator import determine_difficulty_level
        difficulty = determine_difficulty_level(user_scores, topic, subtopic or '')
    except Exception as e:
        print(f"Error determining difficulty: {e}")
        difficulty = 'intermediate'
    
    return render_template('quiz_details.html',
                         topic=topic,
                         subtopic=subtopic,
                         difficulty=difficulty.capitalize(),
                         has_saved_progress=has_saved,
                         saved_question=saved_question,
                         saved_time_left=saved_time_left)

@app.route('/quiz/<path:topic>', methods=['GET', 'POST'])
@app.route('/quiz/<path:topic>/<path:subtopic>', methods=['GET', 'POST'])
def quiz(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))
    
    # Decode URL encoding
    from urllib.parse import unquote
    topic = unquote(topic)
    if subtopic:
        subtopic = unquote(subtopic)
    
    user_email = session['user_email']
        # Handle resume or restart
    resume = request.args.get('resume') == 'true'
    restart = request.args.get('restart') == 'true'
    
    if restart:
        # Delete saved progress
        try:
            search_subtopic = subtopic if subtopic else ''
            supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', topic).eq('subtopic', search_subtopic).execute()
        except:
            pass
    
    # Check for saved progress
    saved_progress = None
    if resume and not restart:
        try:
            search_subtopic = subtopic if subtopic else ''
            result = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', topic).eq('subtopic', search_subtopic).execute()
            if result.data:
                saved_progress = result.data[0]
        except:
            pass
    
    
    # POST - Submit quiz
    if request.method == 'POST':
        # Get questions from session
        topic_questions = session.get('quiz_questions', [])
    
        if not topic_questions:
            flash("Quiz session expired. Please start again.")
            return redirect(url_for('quiz_details', topic=topic, subtopic=subtopic or ''))
    
        score = 0
        user_answers = request.form
    
        for i, q in enumerate(topic_questions):
            user_answer = user_answers.get(f'q{i}', '')
            correct_answer = str(q['answer'])
        
            if user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1
    
        # ⬇️ ADD THIS BLOCK HERE ⬇️
        # Get user's score history for difficulty calculation
        result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', user_email).execute()
        user_scores = [{'topic': row['topic'], 'subtopic': row['subtopic'], 
                        'score': row['score'], 'total_questions': row['total_questions']} 
                       for row in result.data]
    
        from ai_question_generator import determine_difficulty_level
        difficulty = determine_difficulty_level(user_scores, topic, subtopic or '')
    
        # Save score WITH DIFFICULTY
        supabase.table('user_scores').insert({
            'user_email': user_email,
            'topic': topic,
            'subtopic': subtopic or '',
            'score': score,
            'total_questions': len(topic_questions),
            'difficulty': difficulty  # ADD THIS LINE
        }).execute()
    # GET - Load quiz
    if saved_progress:
        # Resume from saved
        topic_questions = json.loads(saved_progress['questions'])
        current_question = saved_progress['current_question']
        time_left = saved_progress['time_left']
        saved_answers = json.loads(saved_progress['answers']) if saved_progress['answers'] else {}
    else:
        # Generate new questions
        result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', user_email).execute()
        
        user_scores = []
        for row in result.data:
            user_scores.append({
                'topic': row['topic'],
                'subtopic': row['subtopic'],
                'score': row['score'],
                'total_questions': row['total_questions']
            })
        
        try:
            from ai_question_generator import get_adaptive_questions
            ai_result = get_adaptive_questions(
                user_email=user_email,
                topic=topic,
                subtopic=subtopic or '',
                user_scores=user_scores,
                num_questions=5
            )
            
            topic_questions = ai_result['questions']
            difficulty = ai_result['difficulty']
            current_question = 0
            time_left = 900  # 15 minutes
            saved_answers = {}
            
        except Exception as e:
            print(f"Error generating questions: {e}")
            flash("Error loading quiz. Please try again.")
            return redirect(url_for('dashboard'))
    
    # Store in session
    session['quiz_questions'] = topic_questions
    
    return render_template('quiz.html',
                         topic=topic,
                         subtopic=subtopic,
                         questions=topic_questions,
                         submitted=False,
                         time_left=time_left,
                         current_question=current_question,
                         saved_answers=saved_answers)


# ============================================================================
# SAVE QUIZ PROGRESS (AJAX)
# ============================================================================
@app.route('/quiz/save', methods=['POST'])
def save_quiz():
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401
    
    data = request.json
    user_email = session['user_email']
    
    try:
        # Delete existing progress
        search_subtopic = data.get('subtopic') if data.get('subtopic') else ''
        supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', data['topic']).eq('subtopic', search_subtopic).execute()
        # Save new progress
        supabase.table('quiz_progress').insert({
            'user_email': user_email,
            'topic': data['topic'],
            'subtopic': search_subtopic,
            'questions': json.dumps(data['questions']),
            'current_question': data['current_question'],
            'answers': json.dumps(data['answers']),
            'time_left': data['time_left'],
            'saved_at': datetime.now().isoformat()
        }).execute()
        
        return {'success': True}, 200
        
    except Exception as e:
        return {'error': str(e)}, 500
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)