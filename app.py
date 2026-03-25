from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from supabase import create_client, Client
from threading import Thread
import os
from dotenv import load_dotenv
from ml_model import analyze_user_performance, get_overall_readiness, get_ml_insights
from ai_question_generator import get_adaptive_questions
from resume_generator import generate_complete_resume
load_dotenv()
from werkzeug.utils import secure_filename
from certificate_manager import CertificateManager
from datetime import datetime
from validators import validate_email, validate_password
import json
import uuid
from learning_resources import get_resources_for_topic
from smart_topic_resolver import resolve_topic, build_ai_context


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

# ============================================================================
# Global storage for generation progress AND grand test questions
# Using server-side dict to avoid session cookie size limits (4KB browser cap)
# Grand test stores 40 questions which easily exceeds this limit.
# ============================================================================
generation_progress = {}
# grand_test_store: task_id -> {'questions': [...], 'type': 'grand_test'}
grand_test_store = {}

# Branch-specific technical topics (Placement-Ready Syllabus)
BRANCH_TOPICS = {
    'CSE': [
        'C', 'C++', 'Java', 'Python',
        'Data Structures', 'Algorithms',
        'DBMS', 'OS', 'Computer Networks',
        'OOP', 'Web Development', 'Cloud Computing'
    ],
    'IT': [
        'C', 'C++', 'Java', 'Python',
        'Data Structures', 'Algorithms',
        'DBMS', 'Web Development', 'Computer Networks',
        'OOP', 'Cloud Computing'
    ],
    'ECE': [
        'C', 'Python',
        'Digital Electronics', 'Analog Electronics',
        'Signal Processing', 'Embedded Systems',
        'VLSI', 'Microprocessors',
        'Communication Systems', 'Control Systems'
    ],
    'EEE': [
        'C', 'Python',
        'Circuit Theory', 'Power Systems',
        'Electrical Machines', 'Power Electronics',
        'Control Systems', 'Electromagnetic Theory',
        'Measurements'
    ],
    'MECH': [
        'C', 'Python',
        'Thermodynamics', 'Mechanics',
        'Strength of Materials', 'Manufacturing',
        'CAD/CAM', 'Fluid Mechanics',
        'Heat Transfer', 'Machine Design',
        'Automobile Engineering'
    ],
    'CIVIL': [
        'C', 'AutoCAD',
        'Structural Analysis', 'Surveying',
        'Geotechnical Engineering', 'Concrete Technology',
        'RCC Design', 'Transportation Engineering',
        'Environmental Engineering'
    ],
    'CHEM': [
        'C', 'Python',
        'Chemical Thermodynamics', 'Process Control',
        'Reaction Engineering', 'Mass Transfer',
        'Fluid Mechanics', 'Heat Transfer',
        'Chemical Engineering Thermodynamics', 'Process Equipment Design'
    ],
    'DEFAULT': ['C', 'Java', 'Python', 'DBMS', 'OS', 'Data Structures']
}


def get_user_branch():
    if 'user_email' not in session:
        return 'DEFAULT'

    result = supabase.table('users').select('branch').eq('email', session['user_email']).execute()

    if result.data:
        branch = result.data[0]['branch'].upper()

        branch_mapping = {
            'COMPUTER SCIENCE': 'CSE',
            'CSE': 'CSE',
            'CS': 'CSE',
            'INFORMATION TECHNOLOGY': 'IT',
            'IT': 'IT',
            'ELECTRONICS AND COMMUNICATION': 'ECE',
            'ECE': 'ECE',
            'ELECTRICAL AND ELECTRONICS': 'EEE',
            'ELECTRICAL': 'EEE',
            'EEE': 'EEE',
            'MECHANICAL': 'MECH',
            'MECH': 'MECH',
            'CIVIL': 'CIVIL',
            'CHEMICAL': 'CHEM',
            'CHEM': 'CHEM',
            'ARTIFICIAL INTELLIGENCE': 'AI/ML',
            'AI/ML': 'AI/ML',
            'AI': 'AI/ML',
            'ML': 'AI/ML'
        }

        if branch in branch_mapping:
            return branch_mapping[branch]

        for key, value in branch_mapping.items():
            if key in branch or branch in key:
                return value

    return 'DEFAULT'


@app.route('/api/branch_topics')
def get_branch_topics():
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
        recommendations['next_steps'].append("Practice more beginner-level questions")
        recommendations['next_steps'].append("Focus on understanding basic syntax and concepts")
    elif percent < 60:
        recommendations['next_steps'].append(f"Continue practicing {subtopic if subtopic else topic}")
        recommendations['next_steps'].append("Review questions you got wrong")
        recommendations['next_steps'].append("Try solving problems with different approaches")
    elif percent < 80:
        recommendations['next_steps'].append("You're doing well! Try more challenging questions")
        recommendations['next_steps'].append(f"Explore advanced concepts in {subtopic if subtopic else topic}")
    else:
        recommendations['next_steps'].append(f"Excellent work! You've mastered {subtopic if subtopic else topic}")
        recommendations['next_steps'].append("Challenge yourself with advanced problems")

    recommendations['performance_summary'] = {
        'current_score': percent,
        'average_score': avg_percent,
        'attempts': attempt_count,
        'difficulty_level': difficulty,
        'trend': 'improving' if percent > avg_percent else 'needs_focus' if percent < avg_percent else 'stable'
    }

    return recommendations


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not validate_email(email):
            flash("Please enter a valid email address")
            return redirect(url_for('register'))

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
        return redirect(url_for('dashboard', welcome='true'))
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

    user_result = supabase.table('users').select('*').eq('email', user_email).execute()
    user_profile = user_result.data[0] if user_result.data else None

    branch_key = get_user_branch()
    branch_topics = BRANCH_TOPICS.get(branch_key, BRANCH_TOPICS['DEFAULT'])

    result = supabase.table('user_scores').select('*').eq('user_email', user_email).execute()

    total_quizzes = len(result.data) if result.data else 0

    if result.data:
        total_score = sum(s['score'] for s in result.data)
        total_questions = sum(s['total_questions'] for s in result.data)
        average_score = round((total_score / total_questions * 100), 1) if total_questions > 0 else 0

        from datetime import datetime, timedelta
        dates = sorted([
            datetime.fromisoformat(s['created_at'].replace('Z', '+00:00')).date()
            for s in result.data
        ], reverse=True)

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
                    if date == dates[i - 1] - timedelta(days=1):
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
                           branch_topics=branch_topics)


# ─────────────────────────────────────────────────────────────────────────────
# GRAND TEST
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/grand_test/details')
def grand_test_details():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session['user_email']

    saved_progress = None
    has_saved = False
    saved_question = 0
    saved_time_left = "60:00"

    try:
        result = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()

        if result.data:
            saved_progress = result.data[0]
            has_saved = True
            saved_question = saved_progress['current_question']
            time_left_seconds = saved_progress['time_left']
            mins = time_left_seconds // 60
            secs = time_left_seconds % 60
            saved_time_left = f"{mins}:{secs:02d}"
    except Exception as e:
        print(f"Error checking saved progress: {e}")

    return render_template('grand_test_details.html',
                           has_saved_progress=has_saved,
                           saved_question=saved_question,
                           saved_time_left=saved_time_left)


@app.route('/grand_test', methods=['GET', 'POST'])
def grand_test():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session['user_email']

    resume = request.args.get('resume') == 'true'
    restart = request.args.get('restart') == 'true'

    if restart:
        try:
            supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()
        except Exception:
            pass
        # Also clean up any stale server-side store for this user
        gt_key = session.pop('grand_test_key', None)
        if gt_key and gt_key in grand_test_store:
            del grand_test_store[gt_key]

    # ── POST: submit quiz ─────────────────────────────────────────────────
    if request.method == 'POST':
        # Try to get questions from hidden form field first (most reliable)
        questions_json = request.form.get('questions_data')
        if questions_json:
            try:
                all_questions = json.loads(questions_json)
            except Exception:
                all_questions = []
        else:
            all_questions = []

        # Fallback: server-side store (avoids re-parsing large session cookies)
        if not all_questions:
            gt_key = session.get('grand_test_key', '')
            gt_data = grand_test_store.get(gt_key, {})
            all_questions = gt_data.get('questions', [])

        if not all_questions:
            flash("Grand Test session expired. Please start again.")
            return redirect(url_for('grand_test_details'))

        score = 0
        user_answers = request.form

        for i, q in enumerate(all_questions):
            user_answer = user_answers.get(f'q{i}', '').strip()
            correct_answer = str(q['answer']).strip()

            is_correct = False
            if user_answer == correct_answer:
                is_correct = True
            else:
                try:
                    answer_index = q['options'].index(correct_answer)
                    if user_answer == q['options'][answer_index]:
                        is_correct = True
                except Exception:
                    pass

            if is_correct:
                score += 1

        result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', user_email).execute()
        user_scores = [
            {'topic': row['topic'], 'subtopic': row['subtopic'],
             'score': row['score'], 'total_questions': row['total_questions']}
            for row in result.data
        ]

        from ai_question_generator import determine_difficulty_level
        difficulty = determine_difficulty_level(user_scores, 'Grand Test', '')

        supabase.table('user_scores').upsert({
            'user_email': user_email,
            'topic': 'Grand Test',
            'subtopic': '',
            'score': score,
            'total_questions': len(all_questions),
            'difficulty': difficulty
        }, on_conflict='user_email,topic,subtopic').execute()

        # Clean up saved progress and server-side store
        try:
            supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()
        except Exception:
            pass

        gt_key = session.pop('grand_test_key', None)
        if gt_key and gt_key in grand_test_store:
            del grand_test_store[gt_key]

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

    # ── GET: load or generate quiz ────────────────────────────────────────
    saved_progress = None
    if resume and not restart:
        try:
            result = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', 'Grand Test').eq('subtopic', '').execute()
            if result.data:
                saved_progress = result.data[0]
        except Exception:
            pass

    if saved_progress:
        # Resume from saved DB progress
        all_questions = json.loads(saved_progress['questions'])
        current_question = saved_progress['current_question']
        time_left = saved_progress['time_left']
        saved_answers = json.loads(saved_progress['answers']) if saved_progress['answers'] else {}
    else:
        # Generate new questions
        try:
            print("\n" + "=" * 80)
            print("🎯 GENERATING GRAND TEST - ALL AI QUESTIONS")
            print("=" * 80)

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

            print("\n[1/3] Generating Technical Questions...")
            tech_difficulty = determine_difficulty_level(user_scores, 'Technical', None)
            tech_questions = generate_quiz_questions('Technical', 'Programming & CS Fundamentals', tech_difficulty, 20)
            all_questions.extend(tech_questions)
            print(f"✅ Added {len(tech_questions)} technical questions")

            print("\n[2/3] Generating Aptitude Questions...")
            apt_difficulty = determine_difficulty_level(user_scores, 'Aptitude', None)
            apt_questions = generate_quiz_questions('Quantitative Aptitude', 'Quantitative & Logical Reasoning', apt_difficulty, 10)
            all_questions.extend(apt_questions)
            print(f"✅ Added {len(apt_questions)} aptitude questions")

            print("\n[3/3] Generating English Questions...")
            eng_difficulty = determine_difficulty_level(user_scores, 'English', None)
            eng_questions = generate_quiz_questions('Grammar', 'Grammar & Communication', eng_difficulty, 10)
            all_questions.extend(eng_questions)
            print(f"✅ Added {len(eng_questions)} English questions")

            print(f"\n✅ TOTAL: {len(all_questions)} AI-generated questions")
            print("=" * 80)

            current_question = 0
            time_left = 3600  # 60 minutes
            saved_answers = {}

        except Exception as e:
            print(f"❌ Error generating Grand Test: {e}")
            import traceback
            traceback.print_exc()
            flash("Failed to generate Grand Test. Please try again.")
            return redirect(url_for('grand_test_details'))

    # ── Store questions SERVER-SIDE to avoid 4KB session cookie limit ─────
    # The session only stores a small UUID key, not the question data.
    gt_key = str(uuid.uuid4())
    grand_test_store[gt_key] = {
        'questions': all_questions,
        'type': 'grand_test',
        'user_email': user_email
    }
    session['grand_test_key'] = gt_key

    # Clean up old entries if store grows large (simple LRU-like cap)
    if len(grand_test_store) > 500:
        oldest_keys = list(grand_test_store.keys())[:100]
        for k in oldest_keys:
            grand_test_store.pop(k, None)

    return render_template('grand_test.html',
                           all_questions=all_questions,
                           submitted=False,
                           time_left=time_left,
                           current_question=current_question,
                           saved_answers=saved_answers)


# ─────────────────────────────────────────────────────────────────────────────
# SUGGESTIONS
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/suggestions')
def suggestions():
    if 'user' not in session:
        return redirect(url_for('index'))

    result = supabase.table('user_scores') \
        .select('topic, subtopic, score, total_questions, created_at') \
        .eq('user_email', session['user_email']) \
        .neq('topic', 'Grand Test') \
        .execute()

    scores_data = []
    for row in result.data:
        scores_data.append({
            'topic': row['topic'],
            'subtopic': row['subtopic'],
            'score': row['score'],
            'total_questions': row['total_questions'],
            'timestamp': row.get('created_at')
        })

    ml_insights = get_ml_insights(scores_data)

    return render_template('suggestions.html',
                           suggestions=ml_insights['weak_topics'],
                           readiness=ml_insights['readiness'],
                           recommendations=ml_insights['recommendations'],
                           ml_features=ml_insights['features'],
                           ml_powered=ml_insights['ml_powered'])


@app.route('/topic_suggestions/<path:topic>')
@app.route('/topic_suggestions/<path:topic>/<path:subtopic>')
def topic_suggestions(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))

    from urllib.parse import unquote
    topic = unquote(topic)
    if subtopic:
        subtopic = unquote(subtopic)

    user_email = session['user_email']

    try:
        search_subtopic = subtopic if subtopic else ''
        result = supabase.table('user_scores') \
            .select('score, total_questions, created_at') \
            .eq('user_email', user_email) \
            .eq('topic', topic) \
            .eq('subtopic', search_subtopic) \
            .order('created_at', desc=True) \
            .execute()

        if not result.data or len(result.data) == 0:
            flash("No quiz data found for this topic.")
            return redirect(url_for('dashboard'))

        scores_data = []
        for row in result.data:
            percentage = (row['score'] / row['total_questions']) * 100
            scores_data.append({
                'score': row['score'],
                'total': row['total_questions'],
                'percentage': percentage,
                'timestamp': row['created_at']
            })

        latest = scores_data[0]
        current_score = round(latest['percentage'], 1)

        total_attempts = len(scores_data)
        avg_score = round(sum(s['percentage'] for s in scores_data) / total_attempts, 1)
        best_score = round(max(s['percentage'] for s in scores_data), 1)

        if total_attempts >= 3:
            recent_avg = sum(s['percentage'] for s in scores_data[:2]) / 2
            old_avg = sum(s['percentage'] for s in scores_data[-2:]) / 2
            improvement = round(recent_avg - old_avg, 1)
        else:
            improvement = 0

        if total_attempts >= 5 and avg_score >= 80:
            status = "Mastered! 🎉"
            performance_class = "excellent"
        elif total_attempts >= 3 and avg_score >= 70:
            status = "Strong Understanding 💪"
            performance_class = "good"
        elif avg_score >= 60:
            status = "Good Progress 👍"
            performance_class = "good"
        elif avg_score >= 40:
            status = "Keep Practicing 📚"
            performance_class = "average"
        else:
            status = "Needs Focus 🎯"
            performance_class = "weak"

        insights = []

        if avg_score >= 80:
            insights.append({
                'icon': 'fas fa-trophy',
                'title': 'Excellent Performance',
                'text': f'You\'re performing exceptionally well in {topic} with an average of {avg_score}%. Continue practicing to maintain this level.'
            })
        elif avg_score >= 60:
            insights.append({
                'icon': 'fas fa-chart-line',
                'title': 'Solid Foundation',
                'text': f'You have a good grasp of {topic} fundamentals. Focus on advanced concepts and edge cases to reach mastery level.'
            })
        else:
            insights.append({
                'icon': 'fas fa-book-reader',
                'title': 'Build Strong Foundation',
                'text': f'Spend more time understanding {topic} basics. Use the resources below and practice regularly for at least 2-3 weeks.'
            })

        if improvement > 10:
            insights.append({
                'icon': 'fas fa-arrow-trend-up',
                'title': 'Great Improvement!',
                'text': f'You\'ve improved by {improvement}% in recent attempts! Your learning strategy is working well.'
            })
        elif improvement > 0:
            insights.append({
                'icon': 'fas fa-seedling',
                'title': 'Steady Progress',
                'text': f'You\'re improving gradually (+{improvement}%). Keep practicing consistently to see faster gains.'
            })
        elif total_attempts >= 3:
            insights.append({
                'icon': 'fas fa-exclamation-triangle',
                'title': 'Need Different Approach',
                'text': 'Your recent scores haven\'t improved. Try using the learning resources below or take a different approach to studying.'
            })

        if total_attempts < 3:
            insights.append({
                'icon': 'fas fa-redo',
                'title': 'Practice More',
                'text': f'You\'ve attempted only {total_attempts} quiz(s). Take at least 3-5 quizzes to get reliable insights on your {topic} proficiency.'
            })
        elif avg_score >= 80:
            insights.append({
                'icon': 'fas fa-forward',
                'title': 'Ready for Next Topic',
                'text': f'You\'ve mastered {topic}! Consider exploring related advanced topics.'
            })
        else:
            insights.append({
                'icon': 'fas fa-list-check',
                'title': 'Recommended Action',
                'text': 'Review questions you got wrong, practice daily for 30 minutes, and retake the quiz after 2-3 days of focused study.'
            })

    except Exception as e:
        print(f"Error in topic_suggestions: {e}")
        flash("Error loading analysis.")
        return redirect(url_for('dashboard'))

    resources = get_resources_for_topic(topic)

    return render_template('topic_suggestions.html',
                           topic=topic,
                           subtopic=subtopic,
                           current_score=current_score,
                           avg_score=avg_score,
                           best_score=best_score,
                           total_attempts=total_attempts,
                           improvement=improvement,
                           status=status,
                           performance_class=performance_class,
                           insights=insights,
                           resources=resources)


# ─────────────────────────────────────────────────────────────────────────────
# RESUME
# ─────────────────────────────────────────────────────────────────────────────

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
    except Exception:
        certificates = []

    resume_data = generate_complete_resume(user_data, scores_data, certificates)

    return render_template('resume_draft.html', resume_data=resume_data)


@app.route('/resume_edit')
def resume_edit():
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
    except Exception:
        certificates = []

    resume_data = generate_complete_resume(user_data, scores_data, certificates)

    return render_template('resume_editor.html', resume_data=resume_data)


# ─────────────────────────────────────────────────────────────────────────────
# CERTIFICATES
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/certificates/upload', methods=['POST'])
def upload_certificate():
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

    file_info = cert_manager.save_certificate(file, session['user_email'])

    if not file_info or 'error' in file_info:
        return {'error': file_info.get('error', 'Upload failed')}, 400

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
            return {'success': True, 'certificate': result.data[0], 'message': 'Certificate uploaded successfully'}, 200
        else:
            return {'error': 'Failed to save certificate to database'}, 500

    except Exception as e:
        cert_manager.delete_certificate(file_info['filename'])
        return {'error': f'Database error: {str(e)}'}, 500


@app.route('/certificates/delete/<int:cert_id>', methods=['DELETE'])
def delete_certificate(cert_id):
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401

    try:
        result = supabase.table('user_certificates').select('*').eq('id', cert_id).eq('user_email', session['user_email']).execute()

        if not result.data:
            return {'error': 'Certificate not found'}, 404

        cert = result.data[0]
        filename = cert['file_url'].split('/')[-1]
        cert_manager.delete_certificate(filename)

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
        supabase.table('users').update({
            'name': data['personal_info']['name'],
            'email': data['personal_info']['email']
        }).eq('email', user_email).execute()

        return {'success': True}, 200
    except Exception as e:
        return {'error': str(e)}, 500


@app.route('/certificates/list', methods=['GET'])
def list_certificates():
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401

    try:
        result = supabase.table('user_certificates').select('*').eq('user_email', session['user_email']).order('uploaded_at', desc=True).execute()
        certificates = result.data if result.data else []
        return {'certificates': certificates}, 200

    except Exception as e:
        return {'error': f'Error fetching certificates: {str(e)}'}, 500


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ PROGRESS SAVE / LOAD
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/quiz/save', methods=['POST'])
def save_quiz():
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401

    data = request.json
    user_email = session['user_email']

    try:
        search_subtopic = data.get('subtopic') if data.get('subtopic') else ''
        supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', data['topic']).eq('subtopic', search_subtopic).execute()

        supabase.table('quiz_progress').insert({
            'user_email': user_email,
            'topic': data['topic'],
            'subtopic': data.get('subtopic', ''),
            'questions': json.dumps(data['questions']),
            'current_question': data['current_question'],
            'answers': json.dumps(data['answers']),
            'time_left': data['time_left'],
            'saved_at': datetime.now().isoformat()
        }).execute()

        return {'success': True}, 200

    except Exception as e:
        return {'error': str(e)}, 500


# ─────────────────────────────────────────────────────────────────────────────
# ASYNC QUESTION GENERATION
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/api/generate_questions_async', methods=['POST'])
def generate_questions_async():
    if 'user' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json
    user_email = session['user_email']
    topic = data.get('topic', '').strip()
    subtopic = data.get('subtopic', '').strip()
    num_questions = int(data.get('num_questions', 20))

    task_id = str(uuid.uuid4())

    generation_progress[task_id] = {
        'status': 'starting',
        'progress': 0,
        'message': 'Initializing...',
        'questions': None,
        'difficulty': None,
        'error': None
    }

    def generate_in_background():
        try:
            result = supabase.table('user_scores').select('topic, subtopic, score, total_questions').eq('user_email', user_email).execute()

            user_scores = []
            for row in result.data:
                user_scores.append({
                    'topic': row['topic'],
                    'subtopic': row.get('subtopic', ''),
                    'score': row['score'],
                    'total_questions': row['total_questions']
                })

            def update_progress(percent, message):
                generation_progress[task_id]['progress'] = percent
                generation_progress[task_id]['message'] = message
                generation_progress[task_id]['status'] = 'generating'

            from ai_question_generator import generate_questions
            questions, difficulty = generate_questions(
                user_email,
                topic,
                subtopic,
                user_scores,
                num_questions,
                progress_callback=update_progress
            )

            generation_progress[task_id]['status'] = 'complete'
            generation_progress[task_id]['progress'] = 100
            generation_progress[task_id]['message'] = 'Questions ready!'
            generation_progress[task_id]['questions'] = questions
            generation_progress[task_id]['difficulty'] = difficulty

        except Exception as e:
            generation_progress[task_id]['status'] = 'error'
            generation_progress[task_id]['error'] = str(e)
            generation_progress[task_id]['message'] = f'Error: {str(e)}'

    thread = Thread(target=generate_in_background)
    thread.daemon = True
    thread.start()

    return jsonify({'task_id': task_id, 'status': 'started'}), 200


@app.route('/api/check_progress/<task_id>')
def check_progress(task_id):
    if task_id not in generation_progress:
        return jsonify({'error': 'Task not found'}), 404

    progress_data = generation_progress[task_id]

    response = {
        'status': progress_data['status'],
        'progress': progress_data['progress'],
        'message': progress_data['message']
    }

    if progress_data['status'] == 'complete':
        response['questions'] = progress_data['questions']
        response['difficulty'] = progress_data['difficulty']

    elif progress_data['status'] == 'error':
        response['error'] = progress_data['error']

    return jsonify(response), 200


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ DETAILS
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/quiz/<path:topic>/details')
@app.route('/quiz/<path:topic>/<path:subtopic>/details')
def quiz_details(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session['user_email']

    from urllib.parse import unquote
    topic = unquote(topic).strip().rstrip('/')
    if subtopic:
        subtopic = unquote(subtopic).strip().rstrip('/')

    print(f"Quiz Details: topic={topic}, subtopic={subtopic}")

    try:
        search_subtopic = subtopic if subtopic else ''
        saved = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', topic).eq('subtopic', search_subtopic).execute()
        has_saved = bool(saved.data)
        saved_question = saved.data[0]['current_question'] if has_saved else 0
        saved_time = saved.data[0]['time_left'] if has_saved else 1800

        mins = saved_time // 60
        secs = saved_time % 60
        saved_time_left = f"{mins}:{secs:02d}"

    except Exception as e:
        print(f"Error checking saved progress: {e}")
        has_saved = False
        saved_question = 0
        saved_time_left = "30:00"

    try:
        result = supabase.table('user_scores').select('score, total_questions').eq('user_email', user_email).eq('topic', topic).eq('subtopic', subtopic or '').execute()

        user_scores = []
        for row in result.data:
            user_scores.append({
                'topic': topic,
                'subtopic': subtopic or '',
                'score': row['score'],
                'total_questions': row['total_questions'],
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
                           saved_time_left=saved_time_left,
                           use_async=True)


# ─────────────────────────────────────────────────────────────────────────────
# QUIZ
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/quiz/<path:topic>', methods=['GET', 'POST'])
@app.route('/quiz/<path:topic>/<path:subtopic>', methods=['GET', 'POST'])
def quiz(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))

    from urllib.parse import unquote
    topic = unquote(topic).strip().rstrip('/')
    if subtopic:
        subtopic = unquote(subtopic).strip().rstrip('/')

    user_email = session['user_email']

    resume = request.args.get('resume') == 'true'
    restart = request.args.get('restart') == 'true'

    if restart:
        try:
            search_subtopic = subtopic if subtopic else ''
            supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', topic).eq('subtopic', search_subtopic).execute()
        except Exception:
            pass

    # ── POST: submit quiz ─────────────────────────────────────────────────
    if request.method == 'POST':
        # Questions stored in session for regular quizzes (20 questions ~ 3-4KB OK)
        topic_questions = session.get('quiz_questions', [])

        if not topic_questions:
            flash("Quiz session expired. Please start again.")
            return redirect(url_for('quiz_details', topic=topic, subtopic=subtopic or ''))

        score = 0
        user_answers = request.form

        for i, q in enumerate(topic_questions):
            user_answer = user_answers.get(f'q{i}', '').strip()
            correct_answer = str(q['answer']).strip()

            if user_answer == correct_answer:
                score += 1
            else:
                print(f"Q{i}: User='{user_answer}' vs Correct='{correct_answer}' - WRONG")

        try:
            result = supabase.table('user_scores').select('*').eq('user_email', user_email).execute()
            user_scores = [
                {'topic': row['topic'], 'subtopic': row.get('subtopic', ''),
                 'score': row['score'], 'total_questions': row['total_questions']}
                for row in result.data
            ]
            from ai_question_generator import determine_difficulty_level
            difficulty = determine_difficulty_level(user_scores, topic, subtopic or '')
        except Exception:
            difficulty = 'intermediate'

        try:
            supabase.table('user_scores').upsert({
                'user_email': user_email,
                'topic': topic,
                'subtopic': subtopic or '',
                'score': score,
                'total_questions': len(topic_questions),
                'difficulty': difficulty
            }, on_conflict='user_email,topic,subtopic').execute()

            try:
                search_subtopic = subtopic if subtopic else ''
                supabase.table('quiz_progress').delete().eq('user_email', user_email).eq('topic', topic).eq('subtopic', search_subtopic).execute()
            except Exception:
                pass

        except Exception as e:
            print(f"Error saving score: {e}")
            flash("Error saving quiz results")
            return redirect(url_for('dashboard'))

        session['last_quiz_score'] = {
            'topic': topic,
            'subtopic': subtopic,
            'score': score,
            'total': len(topic_questions)
        }

        if subtopic:
            return redirect(url_for('topic_suggestions', topic=topic, subtopic=subtopic))
        else:
            return redirect(url_for('topic_suggestions', topic=topic))

    # ── GET ───────────────────────────────────────────────────────────────
    saved_progress = None
    if resume and not restart:
        try:
            search_subtopic = subtopic if subtopic else ''
            result = supabase.table('quiz_progress').select('*').eq('user_email', user_email).eq('topic', topic).eq('subtopic', search_subtopic).execute()
            if result.data:
                saved_progress = result.data[0]
        except Exception:
            pass

    if saved_progress:
        topic_questions = json.loads(saved_progress['questions'])
        current_question = saved_progress['current_question']
        time_left = saved_progress['time_left']
        saved_answers = json.loads(saved_progress['answers']) if saved_progress['answers'] else {}
    else:
        # Check if coming from async generation
        task_id = request.args.get('task_id')
        if task_id and task_id in generation_progress:
            progress_data = generation_progress[task_id]

            if progress_data['status'] == 'complete':
                topic_questions = progress_data['questions']
                difficulty = progress_data['difficulty']
                current_question = 0
                time_left = 1800
                saved_answers = {}
                del generation_progress[task_id]
            else:
                flash("Question generation not complete. Please try again.")
                return redirect(url_for('quiz_details', topic=topic, subtopic=subtopic or ''))
        else:
            # Generate synchronously (fallback)
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
                from ai_question_generator import generate_questions

                topic_questions, difficulty = generate_questions(
                    user_email=user_email,
                    topic=topic,
                    subtopic=subtopic or '',
                    user_scores=user_scores,
                    num_questions=20
                )

                if not topic_questions:
                    flash(f"No questions available for {topic}. Please try another topic.")
                    return redirect(url_for('dashboard'))

                current_question = 0
                time_left = 1800
                saved_answers = {}

            except Exception as e:
                print(f"Error generating questions: {e}")
                flash("Error loading quiz. Please try again.")
                return redirect(url_for('dashboard'))

    # Regular quizzes (20 questions) are small enough for session storage
    session['quiz_questions'] = topic_questions

    return render_template('quiz.html',
                           topic=topic,
                           subtopic=subtopic,
                           questions=topic_questions,
                           submitted=False,
                           time_left=time_left,
                           current_question=current_question,
                           saved_answers=saved_answers)


# ─────────────────────────────────────────────────────────────────────────────
# TOPIC CLASSIFICATION (for search validation)
# ─────────────────────────────────────────────────────────────────────────────

_TECHNICAL_KEYWORDS = {
    'python', 'java', 'c++', 'javascript', 'typescript', 'golang', 'rust', 'kotlin', 'swift',
    'ruby', 'php', 'scala', 'matlab', 'assembly', 'perl', 'dart', 'julia',
    'algorithm', 'data structure', 'sorting', 'searching', 'hashing', 'tree', 'graph',
    'linked list', 'stack', 'queue', 'heap', 'trie', 'recursion', 'dynamic programming',
    'greedy', 'backtracking', 'complexity', 'big o', 'bit manipulation',
    'sql', 'nosql', 'database', 'dbms', 'mongodb', 'postgresql', 'mysql', 'sqlite',
    'normalization', 'indexing', 'transaction', 'query', 'orm', 'redis',
    'networking', 'tcp', 'ip', 'http', 'dns', 'socket', 'protocol', 'osi', 'subnet',
    'operating system', 'process', 'thread', 'deadlock', 'scheduling', 'memory', 'paging',
    'virtual memory', 'file system', 'kernel', 'concurrency', 'semaphore', 'mutex',
    'circuit', 'electronics', 'vlsi', 'verilog', 'vhdl', 'embedded', 'microcontroller',
    'fpga', 'signal', 'digital', 'analog', 'communication', 'antenna', 'microprocessor',
    'transistor', 'diode', 'amplifier', 'filter', 'modulation', 'semiconductor',
    'power', 'electrical', 'motor', 'generator', 'transformer', 'inverter', 'rectifier',
    'thyristor', 'scr', 'converter', 'drives', 'switchgear', 'relay', 'protection',
    'electromagnetic', 'maxwell', 'capacitor', 'inductor',
    'thermodynamics', 'mechanics', 'fluid', 'heat transfer', 'machine design', 'cad',
    'manufacturing', 'welding', 'casting', 'autocad', 'structural', 'surveying',
    'geotechnical', 'concrete', 'rcc', 'transportation', 'reaction', 'distillation',
    'mass transfer', 'process control', 'chemical reactor',
    'machine learning', 'deep learning', 'neural network', 'nlp', 'computer vision',
    'tensorflow', 'pytorch', 'scikit', 'pandas', 'numpy', 'statistics', 'regression',
    'classification', 'clustering', 'reinforcement', 'transformer', 'bert', 'llm',
    'data science', 'feature engineering', 'model', 'training',
    'html', 'css', 'react', 'angular', 'vue', 'node', 'flask', 'django', 'spring',
    'rest', 'api', 'graphql', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
    'devops', 'ci/cd', 'git', 'linux', 'bash', 'cloud', 'serverless',
    'cybersecurity', 'cryptography', 'blockchain', 'iot', 'robotics', 'automation',
    'testing', 'agile', 'design pattern', 'solid', 'microservices', 'architecture',
}

_APTITUDE_KEYWORDS = {
    'aptitude', 'arithmetic', 'percentage', 'profit', 'loss', 'ratio', 'proportion',
    'average', 'mean', 'median', 'mode', 'number system', 'hcf', 'lcm', 'prime',
    'speed', 'distance', 'time', 'work', 'pipe', 'cistern', 'train', 'boat',
    'simple interest', 'compound interest', 'probability', 'permutation', 'combination',
    'series', 'sequence', 'algebra', 'geometry', 'mensuration', 'trigonometry',
    'logical reasoning', 'puzzle', 'syllogism', 'blood relation', 'direction',
    'coding decoding', 'arrangement', 'seating', 'calendar', 'clock', 'data interpretation',
    'bar chart', 'pie chart', 'table', 'graph', 'venn diagram', 'set theory',
}

_VERBAL_KEYWORDS = {
    'grammar', 'vocabulary', 'synonym', 'antonym', 'reading comprehension', 'passage',
    'verbal', 'sentence', 'paragraph', 'error', 'correction', 'fill blank',
    'idiom', 'phrase', 'one word', 'analogy', 'word', 'meaning', 'spelling',
    'tense', 'voice', 'narration', 'preposition', 'conjunction', 'noun', 'verb',
    'adjective', 'adverb', 'pronoun', 'article', 'essay', 'letter', 'communication',
    'english', 'language', 'comprehension', 'jumble', 'para',
}


def _classify_topic(topic_name: str) -> str:
    import re as _re
    t = topic_name.lower()
    words = set(_re.split(r'[\s\-/&]+', t))

    def hits(kw_set):
        for kw in kw_set:
            if kw in t:
                return True
        for word in words:
            if word in kw_set:
                return True
        return False

    if hits(_TECHNICAL_KEYWORDS):
        return 'Technical'
    if hits(_APTITUDE_KEYWORDS):
        return 'Aptitude'
    if hits(_VERBAL_KEYWORDS):
        return 'Verbal'
    return 'Unknown'


@app.route('/api/validate_topic', methods=['POST'])
def validate_topic():
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json or {}
    topic = data.get('topic', '').strip()
    card_category = data.get('card_category', '').strip()

    if not topic or len(topic) < 2:
        return jsonify({'error': 'Topic too short'}), 400

    detected = _classify_topic(topic)

    card_to_detected = {
        'Technical': 'Technical',
        'Aptitude': 'Aptitude',
        'Verbal': 'Verbal',
    }
    expected = card_to_detected.get(card_category, 'Technical')
    belongs = (detected == expected) or (detected == 'Unknown')

    already_exists = False
    try:
        res = supabase.table('custom_topics').select('id').ilike('name', topic).execute()
        already_exists = bool(res.data)
    except Exception as e:
        print(f"validate_topic DB check error: {e}")

    return jsonify({
        'belongs': belongs,
        'detected_category': detected,
        'already_exists': already_exists,
        'topic': topic,
    })


# ─────────────────────────────────────────────────────────────────────────────
# SMART TOPIC RESOLVER ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.route('/api/resolve_topic', methods=['POST'])
def resolve_topic_api():
    """
    Smart topic resolver — called from the browse-dropdown search.
    Body: { "query": "boats", "card_category": "Aptitude" }
    Returns one of:
        { status: 'single', topic, subtopic, ai_context, display_label }
        { status: 'multi',  options: [{...}] }
        { status: 'new',    topic, ai_context }
        { status: 'invalid', message }
    """
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json or {}
    query = data.get('query', '').strip()

    if not query:
        return jsonify({'status': 'invalid', 'message': 'Empty query'}), 400

    result = resolve_topic(query)
    return jsonify(result)


@app.route('/api/add_dynamic_topic', methods=['POST'])
def add_dynamic_topic():
    """
    Saves a new topic to custom_topics and redirects to its quiz.
    Body: { "topic": "JWT Authentication", "category": "Technical", "ai_context": "..." }
    """
    if 'user_email' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json or {}
    topic = data.get('topic', '').strip()
    category = data.get('category', 'Technical').strip()
    ai_context = data.get('ai_context', '').strip()

    if not topic or len(topic) < 2:
        return jsonify({'error': 'Topic name too short'}), 400

    try:
        existing = supabase.table('custom_topics') \
            .select('id, name') \
            .ilike('name', topic) \
            .execute()
        if not existing.data:
            supabase.table('custom_topics').insert({
                'name': topic,
                'category': category,
                'ai_context': ai_context,
                'created_by': session['user_email'],
            }).execute()
    except Exception as e:
        print(f"add_dynamic_topic DB error: {e}")

    return jsonify({
        'success': True,
        'topic': topic,
        'quiz_url': f'/quiz/{topic}/details',
    })


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)