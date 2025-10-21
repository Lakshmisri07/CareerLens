from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from models.db import get_db_connection  # assuming you have this helper

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'placement_prep'

mysql = MySQL(app)

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
@app.route('/quiz/<topic>', methods=['GET', 'POST'])
@app.route('/quiz/<topic>/<subtopic>', methods=['GET', 'POST'])
def quiz(topic, subtopic=None):
    if 'user' not in session:
        return redirect(url_for('index'))

    # Dynamic questions dictionary
    questions = {
        # ---------------- Technical ----------------
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
        # ---------------- Aptitude ----------------
        'Quantitative Aptitude': [
            {"q": "If 5x = 25, what is x?", "options": ["5","25","20","10"], "answer": "5"}
        ],
        'Logical Reasoning': [
            {"q": "If all cats are animals, all animals are not cats. True or False?", "options": ["True","False"], "answer": "True"}
        ],
        'Data Interpretation': [
            {"q": "A table shows sales of 5 products. Which product sold the most?", "options": ["A","B","C","D"], "answer": "C"}
        ],
        # ---------------- English ----------------
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

    # Select questions based on topic/subtopic
    if subtopic:
        topic_questions = questions.get(topic, {}).get(subtopic, [])
    else:
        topic_questions = questions.get(topic, [])

    if not topic_questions:
        flash("No quiz available for this topic yet.")
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        score = 0
        user_answers = request.form
        for i, q in enumerate(topic_questions):
            if user_answers.get(f'q{i}') == q['answer']:
                score += 1

        # Save score to database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO user_scores (user_email, topic, subtopic, score, total_questions)
            VALUES (%s, %s, %s, %s, %s)
        """, (session['user_email'], topic, subtopic or '', score, len(topic_questions)))
        mysql.connection.commit()
        cur.close()

        return render_template('quiz.html', topic=topic, subtopic=subtopic,
                               questions=topic_questions, submitted=True, score=score)

    return render_template('quiz.html', topic=topic, subtopic=subtopic,
                           questions=topic_questions, submitted=False)


@app.route('/suggestions')
def suggestions():
    if 'user' not in session:
        return redirect(url_for('index'))

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT topic, subtopic, SUM(score), SUM(total_questions)
        FROM user_scores
        WHERE user_email=%s
        GROUP BY topic, subtopic
    """, (session['user_email'],))
    performance = cur.fetchall()
    cur.close()

    suggestions_list = []
    for row in performance:
        topic, subtopic, score, total = row
        percent = (score / total) * 100 if total else 0
        if percent < 60:
            if subtopic:
                suggestions_list.append(f"Focus on {subtopic} in {topic}")
            else:
                suggestions_list.append(f"Focus on {topic}")

    return render_template('suggestions.html', suggestions=suggestions_list)


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

        return render_template('grand_test.html', all_questions=all_questions, submitted=True, score=score)


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
