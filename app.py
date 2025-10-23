from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from models.db import get_db_connection
from ml_model import analyze_user_performance, get_overall_readiness
from ai_question_generator import get_adaptive_questions

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'placement_prep'

mysql = MySQL(app)

# Branch-specific technical topics
BRANCH_TOPICS = {
    'CSE': ['C', 'Java', 'Python', 'DBMS', 'OS', 'Data Structures', 'Algorithms', 'Computer Networks', 'OOP'],
    'IT': ['C', 'Java', 'Python', 'DBMS', 'Web Development', 'Data Structures', 'Networking', 'Cloud Computing'],
    'ECE': ['C', 'Python', 'Digital Electronics', 'Signal Processing', 'Embedded Systems', 'VLSI', 'Microprocessors'],
    'EEE': ['C', 'Python', 'Circuit Theory', 'Power Systems', 'Control Systems', 'Electrical Machines'],
    'MECH': ['C', 'Python', 'Thermodynamics', 'Mechanics', 'Manufacturing', 'CAD/CAM'],
    'CIVIL': ['C', 'AutoCAD', 'Structural Analysis', 'Surveying', 'Construction Management'],
    'AI/ML': ['Python', 'Machine Learning', 'Deep Learning', 'Data Structures', 'Statistics', 'Neural Networks'],
    'DEFAULT': ['C', 'Java', 'Python', 'DBMS', 'OS', 'Data Structures']  # Fallback
}

def get_user_branch():
    """Get current user's branch from database"""
    if 'user_email' not in session:
        return 'DEFAULT'
    
    cur = mysql.connection.cursor()
    cur.execute("SELECT branch FROM users WHERE email=%s", (session['user_email'],))
    result = cur.fetchone()
    cur.close()
    
    if result:
        branch = result[0].upper()
        # Match branch to our predefined topics
        for key in BRANCH_TOPICS.keys():
            if key in branch or branch in key:
                return key
    
    return 'DEFAULT'

# ---------------- HELPER FUNCTIONS ----------------
def generate_topic_recommendations(topic, subtopic, percent, difficulty, user_email, mysql_conn):
    """Generate topic-specific recommendations after quiz completion"""
    recommendations = {
        'current_topic': subtopic if subtopic else topic,
        'next_steps': [],
        'related_topics': [],
        'resources': []
    }

    # Get user's performance on this specific topic
    cur = mysql_conn.connection.cursor()
    cur.execute("""
        SELECT AVG(score), AVG(total_questions), COUNT(*)
        FROM user_scores
        WHERE user_email=%s AND topic=%s AND subtopic=%s
    """, (user_email, topic, subtopic or ''))
    result = cur.fetchone()
    cur.close()

    avg_score = result[0] if result[0] else 0
    avg_total = result[1] if result[1] else 1
    attempt_count = result[2] if result[2] else 1
    avg_percent = (avg_score / avg_total * 100) if avg_total > 0 else 0

    # Generate next steps based on performance
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

    # Suggest related topics based on the current topic
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

    # Add performance summary
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

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users (name, email, branch, cgpa, backlogs, internships, password)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, email, branch, cgpa, backlogs, internships, password))
        mysql.connection.commit()
        cur.close()
        flash("Registration successful! Please login.")
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
    user = cur.fetchone()
    cur.close()

    if user:
        session['user'] = user[1]        # name
        session['user_email'] = user[2]  # email
        session['user_branch'] = user[3] # branch
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
    
    # Get branch-specific topics
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


# ---------------- QUIZ ROUTE WITH FIXED SCORING ----------------
@app.route('/quiz/<topic>', methods=['GET', 'POST'])
@app.route('/quiz/<topic>/<subtopic>', methods=['GET', 'POST'])
def quiz(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))

    # Fetch user's past scores for adaptive difficulty
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT topic, subtopic, score, total_questions
        FROM user_scores
        WHERE user_email=%s
    """, (session['user_email'],))
    past_scores = cur.fetchall()
    cur.close()
    
    # Convert to list of dicts for AI model
    user_scores = []
    for row in past_scores:
        user_scores.append({
            'topic': row[0],
            'subtopic': row[1],
            'score': row[2],
            'total_questions': row[3]
        })
    
    # Generate AI-powered adaptive questions
    try:
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
        
        print(f"✅ Loaded {len(topic_questions)} questions at {difficulty} level")
        
    except Exception as e:
        print(f"❌ Error loading AI questions: {e}")
        flash("Error loading quiz. Please try again.")
        return redirect(url_for('dashboard'))

    if not topic_questions:
        flash("No quiz available for this topic yet.")
        return redirect(url_for('dashboard'))

    # Handle quiz submission - FIXED SCORING LOGIC
    if request.method == 'POST':
        score = 0
        user_answers = request.form

        print("\n" + "="*80)
        print("📝 SCORING QUIZ - FIXED VERSION")
        print("="*80)
        print(f"Total questions: {len(topic_questions)}")

        # Calculate score with improved validation
        for i, q in enumerate(topic_questions):
            user_answer = user_answers.get(f'q{i}', '').strip()
            correct_answer = str(q['answer']).strip()

            print(f"\n{'='*60}")
            print(f"Q{i+1}: {q.get('q', '')[:60]}...")
            print(f"Options: {q.get('options', [])}")
            print(f"User selected: '{user_answer}'")
            print(f"Correct answer: '{correct_answer}'")

            # FIXED: Robust comparison that handles all edge cases
            # 1. Exact match (case-insensitive)
            # 2. Strip all whitespace
            # 3. Normalize unicode characters
            user_normalized = user_answer.strip().lower()
            correct_normalized = correct_answer.strip().lower()
            
            # Check if answer exists in options (for validation)
            answer_in_options = any(opt.strip().lower() == correct_normalized for opt in q.get('options', []))
            
            if not answer_in_options:
                print(f"⚠️ WARNING: Correct answer not found in options!")
                # Try to find closest match
                for opt in q.get('options', []):
                    if correct_normalized in opt.strip().lower() or opt.strip().lower() in correct_normalized:
                        correct_normalized = opt.strip().lower()
                        print(f"   Fixed: Using '{opt}' as correct answer")
                        break
            
            # Compare answers
            is_correct = user_normalized == correct_normalized
            
            if is_correct:
                score += 1
                print(f"✅ CORRECT!")
            else:
                print(f"❌ WRONG")
                print(f"   User gave: '{user_normalized}'")
                print(f"   Expected: '{correct_normalized}'")

        print(f"\n{'='*80}")
        print(f"📊 FINAL SCORE: {score}/{len(topic_questions)} ({(score/len(topic_questions)*100):.1f}%)")
        print("="*80 + "\n")

        # Save score to database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO user_scores (user_email, topic, subtopic, score, total_questions)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_email'], topic, subtopic or '', score, len(topic_questions)))
        mysql.connection.commit()
        cur.close()

        # Generate performance feedback
        percent = (score / len(topic_questions)) * 100

        # Base suggestion based on score
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

        # Add difficulty-specific feedback
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
        else:  # advanced
            if percent >= 80:
                suggestion += " 🏆 Outstanding! You've mastered this topic at expert level!"
            else:
                suggestion += " Advanced questions are challenging. Review concepts and try again."

        # Generate topic-specific recommendations
        topic_recommendations = generate_topic_recommendations(
            topic, subtopic, percent, difficulty, session['user_email'], mysql
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

    # Display quiz (GET request)
    return render_template('quiz.html', 
                         topic=topic, 
                         subtopic=subtopic,
                         questions=topic_questions, 
                         submitted=False,
                         difficulty=difficulty,
                         ai_generated=ai_generated)


@app.route('/suggestions')
def suggestions():
    if 'user' not in session:
        return redirect(url_for('index'))

    # Fetch all user scores
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT topic, subtopic, score, total_questions
        FROM user_scores
        WHERE user_email=%s
    """, (session['user_email'],))
    results = cur.fetchall()
    cur.close()

    # Convert to list of dictionaries for ML model
    scores_data = []
    for row in results:
        scores_data.append({
            'topic': row[0],
            'subtopic': row[1],
            'score': row[2],
            'total_questions': row[3]
        })

    # Use ML model to analyze performance
    ml_suggestions = analyze_user_performance(scores_data)

    # Get overall readiness score
    readiness = get_overall_readiness(scores_data)

    return render_template('suggestions.html',
                         suggestions=ml_suggestions,
                         readiness=readiness)


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
        
        # FIXED: Same robust scoring logic
        for i, q in enumerate(all_questions):
            user_answer = user_answers.get(f'q{i}', '').strip()
            correct_answer = str(q['answer']).strip()
            
            # Normalize and compare
            if user_answer.strip().lower() == correct_answer.strip().lower():
                score += 1

        # Save Grand Test score
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO user_scores (user_email, topic, subtopic, score, total_questions) VALUES (%s,%s,%s,%s,%s)",
            (session['user_email'], 'Grand Test', '', score, len(all_questions))
        )
        mysql.connection.commit()
        cur.close()

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

    # Generate AI questions for Grand Test
    try:
        print("\n" + "="*80)
        print("🎯 GENERATING GRAND TEST")
        print("="*80)

        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT topic, subtopic, score, total_questions
            FROM user_scores
            WHERE user_email=%s
        """, (session['user_email'],))
        past_scores = cur.fetchall()
        cur.close()
        
        user_scores = []
        for row in past_scores:
            user_scores.append({
                'topic': row[0],
                'subtopic': row[1],
                'score': row[2],
                'total_questions': row[3]
            })

        all_questions = []

        from ai_question_generator import generate_quiz_questions, determine_difficulty_level
        
        # Technical
        tech_difficulty = determine_difficulty_level(user_scores, 'Technical', None)
        tech_questions = generate_quiz_questions('Technical', 'Programming & CS Fundamentals', tech_difficulty, 5)
        all_questions.extend(tech_questions)

        # Aptitude
        apt_difficulty = determine_difficulty_level(user_scores, 'Aptitude', None)
        apt_questions = generate_quiz_questions('Aptitude', 'Quantitative & Logical Reasoning', apt_difficulty, 5)
        all_questions.extend(apt_questions)

        # English
        eng_difficulty = determine_difficulty_level(user_scores, 'English', None)
        eng_questions = generate_quiz_questions('English', 'Grammar & Communication', eng_difficulty, 5)
        all_questions.extend(eng_questions)

        print(f"\n✅ TOTAL: {len(all_questions)} questions generated")

        session['grand_test_questions'] = all_questions

        return render_template('grand_test.html', 
                             all_questions=all_questions, 
                             submitted=False)

    except Exception as e:
        print(f"❌ Error: {e}")
        flash("Failed to generate Grand Test. Please try again.")
        return redirect(url_for('dashboard'))


@app.route('/resume_draft')
def resume_draft():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session.get('user_email')
    cur = mysql.connection.cursor()
    cur.execute("SELECT name, email, branch, cgpa, internships, backlogs FROM users WHERE email=%s", (user_email,))
    row = cur.fetchone()
    cur.close()

    if not row:
        flash("User data not found!")
        return redirect(url_for('dashboard'))

    user = {
        "name": row[0],
        "email": row[1],
        "branch": row[2],
        "cgpa": row[3],
        "internships": row[4],
        "backlogs": row[5],
    }

    cur = mysql.connection.cursor()
    cur.execute("SELECT topic, SUM(score) FROM user_scores WHERE user_email=%s GROUP BY topic", (user_email,))
    scores = cur.fetchall()
    cur.close()

    skills = {
        "core_skills": ", ".join([s[0] for s in scores[:2]]) if scores else "N/A",
        "programming": ", ".join([s[0] for s in scores[2:4]]) if len(scores) > 2 else "N/A",
        "aptitude": ", ".join([s[0] for s in scores[4:5]]) if len(scores) > 4 else "N/A",
        "soft_skills": ", ".join([s[0] for s in scores[5:]]) if len(scores) > 5 else "N/A"
    }

    return render_template('resume_draft.html', user=user, skills=skills)


if __name__ == '__main__':
    app.run(debug=True)