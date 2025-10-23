from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from models.db import get_db_connection  # assuming you have this helper
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

# ---------------- HELPER FUNCTIONS ----------------
def generate_topic_recommendations(topic, subtopic, percent, difficulty, user_email, mysql_conn):
    """
    Generate topic-specific recommendations after quiz completion
    """
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
        return redirect(url_for('dashboard'))
    else:
        flash("Invalid email or password.")
        return redirect(url_for('index'))


@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_email', None)
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
    topics = ['C', 'Java', 'Python', 'DBMS', 'OS', 'Data Structures']
    return render_template('technical.html', topics=topics)


@app.route('/technical/<topic>')
def subtopics(topic):
    subtopic_map = {
        'C': ['Arrays', 'Pointers', 'Loops', 'Functions'],
        'Java': ['OOPs', 'Inheritance', 'Exceptions'],
        'Python': ['Lists', 'Dictionaries', 'File Handling'],
        'DBMS': ['SQL', 'Normalization', 'Transactions'],
        'OS': ['Processes', 'Threads', 'Memory Management'],
        'Data Structures': ['Linked List', 'Stacks', 'Queues', 'Trees']
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


# ---------------- QUIZ ROUTE ----------------
# Add this import at the top of your app.py
from ai_question_generator import get_adaptive_questions

# Replace your existing /quiz route with this enhanced version:

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

    # Handle quiz submission
    if request.method == 'POST':
        score = 0
        user_answers = request.form

        print("\n" + "="*80)
        print("📝 SCORING QUIZ - DETAILED DEBUG")
        print("="*80)
        print(f"Total questions: {len(topic_questions)}")

        # First, let's see all form data
        print("\n📋 ALL FORM DATA:")
        for key, value in user_answers.items():
            print(f"   {key}: '{value}'")

        # Calculate score with proper string comparison
        for i, q in enumerate(topic_questions):
            user_answer = user_answers.get(f'q{i}', '').strip()
            correct_answer = str(q['answer']).strip()

            print(f"\n{'='*60}")
            print(f"Q{i+1}: {q.get('q', '')[:60]}...")
            print(f"Options: {q.get('options', [])}")
            print(f"User answer: '{user_answer}' (length: {len(user_answer)})")
            print(f"Correct answer: '{correct_answer}' (length: {len(correct_answer)})")
            print(f"Answer in options? {correct_answer in q.get('options', [])}")

            # Show byte representation for debugging hidden characters
            print(f"User bytes: {user_answer.encode('utf-8')}")
            print(f"Correct bytes: {correct_answer.encode('utf-8')}")

            # Try multiple comparison methods
            exact_match = user_answer == correct_answer
            case_insensitive = user_answer.lower() == correct_answer.lower()
            stripped_match = user_answer.strip().lower() == correct_answer.strip().lower()

            print(f"Exact match: {exact_match}")
            print(f"Case-insensitive: {case_insensitive}")
            print(f"Stripped match: {stripped_match}")

            if case_insensitive:
                score += 1
                print(f"✅ CORRECT!")
            else:
                print(f"❌ WRONG")

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

    # Full questions dictionary (same as in your quiz route)
    questions = {
        # Technical
        'C': {
            'Arrays': [
                {"q": "What is the index of the first element in an array?", "options": ["0","1","-1","Depends on compiler"], "answer": "0"},
                {"q": "Which of these is a correct array declaration?", "options": ["int arr[];","arr int[];","array int arr;","int arr{};"], "answer": "int arr[];"}
            ],
            'Pointers': [
                {"q": "Which operator gives the value at the address stored in a pointer?", "options": ["*","&","->","."], "answer": "*"},
                {"q": "Which keyword is used to declare a pointer?", "options": ["ptr","*","pointer","&"], "answer": "*"}
            ]
        },
        'Java': {
            'OOPs': [
                {"q": "Which keyword is used to inherit a class in Java?", "options": ["extends","implements","super","inherits"], "answer": "extends"},
                {"q": "Java supports multiple inheritance via:", "options": ["Classes","Interfaces","Methods","None"], "answer": "Interfaces"}
            ]
        },
        'Python': {
            'Lists': [
                {"q": "Which method adds an element at the end of a list?", "options": ["append()","add()","insert()","extend()"], "answer": "append()"}
            ]
        },
        'DBMS': {
            'SQL': [
                {"q": "Which command is used to remove a table from database?", "options": ["DELETE TABLE","DROP TABLE","REMOVE TABLE","TRUNCATE TABLE"], "answer": "DROP TABLE"}
            ]
        },
        'OS': {
            'Processes': [
                {"q": "Which of these is a state of a process?", "options": ["Running","Waiting","Terminated","All of the above"], "answer": "All of the above"}
            ]
        },
        'Data Structures': {
            'Stacks': [
                {"q": "Stack follows which order?", "options": ["FIFO","LIFO","LILO","FILO"], "answer": "LIFO"}
            ]
        },
        # Aptitude
        'Quantitative Aptitude': [
            {"q": "If 5x = 25, what is x?", "options": ["5","25","20","10"], "answer": "5"}
        ],
        'Logical Reasoning': [
            {"q": "If all cats are animals, all animals are not cats. True or False?", "options": ["True","False"], "answer": "True"}
        ],
        'Data Interpretation': [
            {"q": "A table shows sales of 5 products. Which product sold the most?", "options": ["A","B","C","D"], "answer": "C"}
        ],
        # English
        'Grammar': [
            {"q": "Choose the correct form: She ____ going to school.", "options": ["is","are","am","be"], "answer": "is"}
        ],
        'Reading Comprehension': [
            {"q": "What is the main idea of a passage called?", "options": ["Theme","Topic","Summary","Moral"], "answer": "Theme"}
        ],
        'Synonyms & Antonyms': [
            {"q": "Select the synonym of 'Happy'", "options": ["Sad","Joyful","Angry","Tired"], "answer": "Joyful"}
        ]
    }

    # Flatten all questions into a single list for grand test
    all_questions = []
    for topic, value in questions.items():
        if isinstance(value, dict):
            # Technical subtopics
            for subtopic, qlist in value.items():
                all_questions.extend(qlist)
        else:
            # Aptitude and English
            all_questions.extend(value)

    if request.method == 'POST':
        score = 0
        user_answers = request.form
        for i, q in enumerate(all_questions):
            if user_answers.get(f'q{i}') == q['answer']:
                score += 1

        # Save Grand Test score to database
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO user_scores (user_email, topic, subtopic, score, total_questions) VALUES (%s,%s,%s,%s,%s)",
            (session['user_email'], 'Grand Test', '', score, len(all_questions))
        )
        mysql.connection.commit()
        cur.close()

        # Generate suggestion for Grand Test
        percent = (score / len(all_questions)) * 100
        suggestion = ""
        if percent < 40:
            suggestion = f"Your overall score is {percent:.1f}%. Focus on all core areas - Technical, Aptitude, and English."
        elif percent < 60:
            suggestion = f"Your overall score is {percent:.1f}%. You're on the right track. Review weak areas and practice more."
        elif percent < 80:
            suggestion = f"Your overall score is {percent:.1f}%. Good performance! Focus on refining your skills."
        else:
            suggestion = f"Your overall score is {percent:.1f}%. Outstanding! You're well-prepared for placements."

        return render_template('grand_test.html', all_questions=all_questions, submitted=True, score=score, suggestion=suggestion)


    return render_template('grand_test.html', all_questions=all_questions, submitted=False)


@app.route('/resume_draft')
def resume_draft():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session.get('user_email')
    if not user_email:
        flash("User email not found in session.")
        return redirect(url_for('dashboard'))

    cur = mysql.connection.cursor()
    # Fetch user info as dictionary
    cur.execute("SELECT name, email, branch, cgpa, internships, backlogs FROM users WHERE email=%s", (user_email,))
    row = cur.fetchone()
    cur.close()

    if not row:
        flash("User data not found!")
        return redirect(url_for('dashboard'))

    # Convert row to dict
    user = {
        "name": row[0],
        "email": row[1],
        "branch": row[2],
        "cgpa": row[3],
        "internships": row[4],
        "backlogs": row[5],
    }

    # Fetch user scores and generate skills
    cur = mysql.connection.cursor()
    cur.execute("SELECT topic, SUM(score) FROM user_scores WHERE user_email=%s GROUP BY topic", (user_email,))
    scores = cur.fetchall()
    cur.close()

    # Convert scores into a dict for template
    skills = {
        "core_skills": ", ".join([s[0] for s in scores[:2]]) if scores else "N/A",
        "programming": ", ".join([s[0] for s in scores[2:4]]) if len(scores) > 2 else "N/A",
        "aptitude": ", ".join([s[0] for s in scores[4:5]]) if len(scores) > 4 else "N/A",
        "soft_skills": ", ".join([s[0] for s in scores[5:]]) if len(scores) > 5 else "N/A"
    }

    return render_template('resume_draft.html', user=user, skills=skills)

if __name__ == '__main__':
    app.run(debug=True)
