from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from models.db import get_db_connection  # assuming you have this helper
from ml_model import analyze_user_performance, get_overall_readiness

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
                {"q": "Which of these is a correct array declaration?", "options": ["int arr[];","arr int[];","array int arr;","int arr{};"], "answer": "int arr[];"},
                {"q": "What is the size of int array[10]?", "options": ["10 bytes","40 bytes","Depends on system","10 elements"], "answer": "Depends on system"}
            ],
            'Pointers': [
                {"q": "Which operator gives the value at the address stored in a pointer?", "options": ["*","&","->","."], "answer": "*"},
                {"q": "Which keyword is used to declare a pointer?", "options": ["ptr","*","pointer","&"], "answer": "*"},
                {"q": "What is a NULL pointer?", "options": ["Pointer with value 0","Pointer pointing to nothing","Invalid pointer","Both A and B"], "answer": "Both A and B"}
            ],
            'Loops': [
                {"q": "Which loop is guaranteed to execute at least once?", "options": ["for","while","do-while","None"], "answer": "do-while"},
                {"q": "Which keyword is used to exit a loop?", "options": ["exit","break","return","stop"], "answer": "break"},
                {"q": "What does 'continue' statement do?", "options": ["Exit loop","Skip current iteration","Start from beginning","Nothing"], "answer": "Skip current iteration"}
            ],
            'Functions': [
                {"q": "What is the return type of a function that doesn't return any value?", "options": ["int","void","null","None"], "answer": "void"},
                {"q": "How are arguments passed to functions in C by default?", "options": ["By reference","By value","By pointer","By address"], "answer": "By value"},
                {"q": "Which function is the entry point of a C program?", "options": ["start()","main()","begin()","run()"], "answer": "main()"}
            ]
        },
        'Java': {
            'OOPs': [
                {"q": "Which keyword is used to inherit a class in Java?", "options": ["extends","implements","super","inherits"], "answer": "extends"},
                {"q": "Java supports multiple inheritance via:", "options": ["Classes","Interfaces","Methods","None"], "answer": "Interfaces"},
                {"q": "What is encapsulation?", "options": ["Hiding data","Binding data and methods","Inheritance","Polymorphism"], "answer": "Binding data and methods"}
            ],
            'Inheritance': [
                {"q": "Which keyword prevents a class from being inherited?", "options": ["final","static","private","sealed"], "answer": "final"},
                {"q": "What is method overriding?", "options": ["Same method in child class","Multiple methods same name","Private method","Static method"], "answer": "Same method in child class"},
                {"q": "Which type of inheritance is not supported in Java?", "options": ["Single","Multiple","Multilevel","Hierarchical"], "answer": "Multiple"}
            ],
            'Exceptions': [
                {"q": "Which keyword is used to throw an exception manually?", "options": ["throw","throws","try","catch"], "answer": "throw"},
                {"q": "Which block always executes whether exception occurs or not?", "options": ["try","catch","finally","throws"], "answer": "finally"},
                {"q": "Which is a checked exception?", "options": ["IOException","NullPointerException","ArithmeticException","ArrayIndexOutOfBounds"], "answer": "IOException"}
            ]
        },
        'Python': {
            'Lists': [
                {"q": "Which method adds an element at the end of a list?", "options": ["append()","add()","insert()","extend()"], "answer": "append()"},
                {"q": "Which method removes the last element?", "options": ["pop()","remove()","delete()","clear()"], "answer": "pop()"},
                {"q": "How to access the last element of a list?", "options": ["list[-1]","list[last]","list[end]","list.last()"], "answer": "list[-1]"}
            ],
            'Dictionaries': [
                {"q": "How to add a new key-value pair?", "options": ["dict[key] = value","dict.add(key, value)","dict.insert(key, value)","dict.append(key, value)"], "answer": "dict[key] = value"},
                {"q": "Which method returns all keys?", "options": ["keys()","getKeys()","allKeys()","keyList()"], "answer": "keys()"},
                {"q": "What happens if you access a non-existent key?", "options": ["Returns None","KeyError","Returns 0","Returns empty string"], "answer": "KeyError"}
            ],
            'File Handling': [
                {"q": "Which mode opens a file for writing?", "options": ["'w'","'r'","'a'","'x'"], "answer": "'w'"},
                {"q": "Which function reads entire file content?", "options": ["read()","readAll()","get()","fetch()"], "answer": "read()"},
                {"q": "What does 'a' mode do?", "options": ["Append to file","Create new file","Read file","Delete file"], "answer": "Append to file"}
            ]
        },
        'DBMS': {
            'SQL': [
                {"q": "Which command is used to remove a table from database?", "options": ["DELETE TABLE","DROP TABLE","REMOVE TABLE","TRUNCATE TABLE"], "answer": "DROP TABLE"},
                {"q": "Which clause is used to filter rows?", "options": ["WHERE","HAVING","FILTER","SELECT"], "answer": "WHERE"},
                {"q": "Which command is used to modify existing data?", "options": ["UPDATE","MODIFY","CHANGE","ALTER"], "answer": "UPDATE"}
            ],
            'Normalization': [
                {"q": "What is the goal of normalization?", "options": ["Reduce redundancy","Increase speed","Add more tables","Remove constraints"], "answer": "Reduce redundancy"},
                {"q": "Which normal form removes partial dependency?", "options": ["1NF","2NF","3NF","BCNF"], "answer": "2NF"},
                {"q": "What is a candidate key?", "options": ["Minimal superkey","Primary key","Foreign key","Composite key"], "answer": "Minimal superkey"}
            ],
            'Transactions': [
                {"q": "Which property ensures all-or-nothing execution?", "options": ["Atomicity","Consistency","Isolation","Durability"], "answer": "Atomicity"},
                {"q": "Which command saves changes permanently?", "options": ["COMMIT","SAVE","ROLLBACK","END"], "answer": "COMMIT"},
                {"q": "What does ROLLBACK do?", "options": ["Undo changes","Save changes","Delete data","Create backup"], "answer": "Undo changes"}
            ]
        },
        'OS': {
            'Processes': [
                {"q": "Which of these is a state of a process?", "options": ["Running","Waiting","Terminated","All of the above"], "answer": "All of the above"},
                {"q": "What is a PCB?", "options": ["Process Control Block","Program Counter Block","Process Code Block","None"], "answer": "Process Control Block"},
                {"q": "Which scheduling algorithm is non-preemptive?", "options": ["FCFS","Round Robin","Priority","None"], "answer": "FCFS"}
            ],
            'Threads': [
                {"q": "What is a thread?", "options": ["Lightweight process","Heavy process","System call","None"], "answer": "Lightweight process"},
                {"q": "Threads share which of these?", "options": ["Code section","Data section","Files","All of the above"], "answer": "All of the above"},
                {"q": "Which model has many-to-one mapping?", "options": ["User level threads","Kernel level threads","Hybrid","None"], "answer": "User level threads"}
            ],
            'Memory Management': [
                {"q": "What is paging?", "options": ["Divide memory into pages","Divide disk","Allocate memory","Free memory"], "answer": "Divide memory into pages"},
                {"q": "What is a page fault?", "options": ["Page not in memory","Page error","Disk error","Memory error"], "answer": "Page not in memory"},
                {"q": "Which algorithm replaces least recently used page?", "options": ["LRU","FIFO","LFU","Optimal"], "answer": "LRU"}
            ]
        },
        'Data Structures': {
            'Stacks': [
                {"q": "Stack follows which order?", "options": ["FIFO","LIFO","LILO","FILO"], "answer": "LIFO"},
                {"q": "Which operation removes top element?", "options": ["pop()","push()","peek()","remove()"], "answer": "pop()"},
                {"q": "What is stack overflow?", "options": ["Stack is full","Stack is empty","Invalid operation","Memory leak"], "answer": "Stack is full"}
            ],
            'Linked List': [
                {"q": "What is the first node called?", "options": ["Head","Root","Start","First"], "answer": "Head"},
                {"q": "Which has bidirectional traversal?", "options": ["Singly linked list","Doubly linked list","Circular linked list","Array"], "answer": "Doubly linked list"},
                {"q": "Time complexity to insert at beginning?", "options": ["O(1)","O(n)","O(log n)","O(n^2)"], "answer": "O(1)"}
            ],
            'Queues': [
                {"q": "Queue follows which order?", "options": ["FIFO","LIFO","LILO","Random"], "answer": "FIFO"},
                {"q": "Which operation adds element to queue?", "options": ["enqueue","push","insert","add"], "answer": "enqueue"},
                {"q": "What is circular queue?", "options": ["Last connects to first","Queue in circle","Rotating queue","None"], "answer": "Last connects to first"}
            ],
            'Trees': [
                {"q": "What is the root of a tree?", "options": ["Top node","Bottom node","Middle node","Any node"], "answer": "Top node"},
                {"q": "Maximum children in binary tree?", "options": ["1","2","3","Unlimited"], "answer": "2"},
                {"q": "Which traversal visits root first?", "options": ["Preorder","Inorder","Postorder","Level order"], "answer": "Preorder"}
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

        # Generate suggestion for this quiz
        percent = (score / len(topic_questions)) * 100
        suggestion = ""
        if percent < 40:
            suggestion = f"Your score is {percent:.1f}%. You need significant practice in {subtopic if subtopic else topic}."
        elif percent < 60:
            suggestion = f"Your score is {percent:.1f}%. Keep practicing {subtopic if subtopic else topic} to improve."
        elif percent < 80:
            suggestion = f"Your score is {percent:.1f}%. Good work! A bit more practice on {subtopic if subtopic else topic} will help."
        else:
            suggestion = f"Your score is {percent:.1f}%. Excellent! You have strong knowledge in {subtopic if subtopic else topic}."

        return render_template('quiz.html', topic=topic, subtopic=subtopic,
                               questions=topic_questions, submitted=True, score=score,
                               suggestion=suggestion)

    return render_template('quiz.html', topic=topic, subtopic=subtopic,
                           questions=topic_questions, submitted=False)


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
