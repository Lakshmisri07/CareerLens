"""
CRITICAL BUG FIXES for Resume Feature

Apply these fixes to your code:
"""

# ==============================================================================
# FIX #1: Update app.py - Certificate Upload Route (Line ~665)
# ==============================================================================

# REPLACE THIS:
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

# WITH THIS (FIXED VERSION):
@app.route('/certificates/upload', methods=['POST'])
def upload_certificate():
    """Handle certificate file upload"""
    if 'user' not in session:
        return {'error': 'Not authenticated'}, 401
    
    # Validate file presence
    if 'certificate_file' not in request.files:
        return {'error': 'No file uploaded'}, 400
    
    file = request.files['certificate_file']
    
    # Check if file was actually selected
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    # Validate form fields
    cert_name = request.form.get('cert_name', '').strip()
    cert_issuer = request.form.get('cert_issuer', '').strip()
    cert_date = request.form.get('cert_date', '').strip()
    cert_id = request.form.get('cert_id', '').strip()
    
    if not cert_name or not cert_issuer:
        return {'error': 'Certificate name and issuer are required'}, 400
    
    # Validate file type
    if not cert_manager.allowed_file(file.filename):
        return {'error': 'Invalid file type. Only PDF, PNG, JPG, JPEG allowed.'}, 400


# ==============================================================================
# FIX #2: Update resume_generator.py - generate_achievements() (Line ~168)
# ==============================================================================

# REPLACE THIS:
def generate_achievements(self, scores_data, readiness, certificates):
    """Generate achievement bullets from performance and certificates"""
    achievements = []
    
    total_quizzes = len(scores_data)
    avg_score = sum(s['score'] for s in scores_data) / sum(s['total_questions'] for s in scores_data) * 100 if scores_data else 0
    
    # Certificates as achievements
    for cert in certificates[:2]:  # Top 2 certificates
        achievements.append(f"Earned {cert['name']} certification from {cert['issuer']}")

# WITH THIS (FIXED VERSION):
def generate_achievements(self, scores_data, readiness, certificates):
    """Generate achievement bullets from performance and certificates"""
    achievements = []
    
    total_quizzes = len(scores_data)
    
    # Safe calculation of avg_score
    if scores_data:
        total_score = sum(s['score'] for s in scores_data)
        total_questions = sum(s['total_questions'] for s in scores_data)
        avg_score = (total_score / total_questions * 100) if total_questions > 0 else 0
    else:
        avg_score = 0
    
    # Certificates as achievements (SAFE - handles empty list)
    if certificates:
        for cert in certificates[:2]:  # Top 2 certificates
            achievements.append(f"Earned {cert['name']} certification from {cert['issuer']}")


# ==============================================================================
# FIX #3: Update certificate_manager.py - save_certificate() (Line ~38)
# ==============================================================================

# REPLACE THIS:
def save_certificate(self, file, user_email):
    """
    Save uploaded certificate file
    Returns: dict with file info or None if error
    """
    if not file or file.filename == '':
        return None

# WITH THIS (FIXED VERSION):
def save_certificate(self, file, user_email):
    """
    Save uploaded certificate file
    Returns: dict with file info or None if error
    """
    if not file or file.filename == '':
        return {'error': 'No file provided'}
    
    # Validate file extension
    if not self.allowed_file(file.filename):
        return {'error': f'Invalid file type. Allowed types: {", ".join(self.ALLOWED_EXTENSIONS)}'}


# ==============================================================================
# FIX #4: Update app.py - resume_draft route (Line ~612)
# ==============================================================================

# REPLACE THIS:
@app.route('/resume_draft')
def resume_draft():
    if 'user' not in session:
        return redirect(url_for('index'))

    user_email = session.get('user_email')
    
    # Get user data
    result = supabase.table('users').select('*').eq('email', user_email).execute()
    if not result.data:
        flash("User data not found!")
        return redirect(url_for('dashboard'))
    
    user_data = result.data[0]
    
    # Get quiz scores (filter out Grand Test)
    scores_result = supabase.table('user_scores').select('*').eq('user_email', user_email).execute()
    scores_data = [s for s in scores_result.data if s.get('topic', '').lower() != 'grand test'] if scores_result.data else []
    
    # Get certificates with files (NEW)
    try:
        certs_result = supabase.table('user_certificates').select('*').eq('user_email', user_email).execute()
        certificates = certs_result.data if certs_result.data else []
    except Exception as e:
        print(f"Error fetching certificates: {e}")
        certificates = []
    
    # Generate resume data
    resume_data = generate_complete_resume(user_data, scores_data, certificates)
    
    return render_template('resume_builder.html', resume_data=resume_data)

# WITH THIS (FIXED VERSION - BETTER ERROR HANDLING):
@app.route('/resume_draft')
def resume_draft():
    if 'user' not in session:
        flash("Please login to access resume builder")
        return redirect(url_for('index'))

    user_email = session.get('user_email')
    
    try:
        # Get user data
        result = supabase.table('users').select('*').eq('email', user_email).execute()
        if not result.data:
            flash("User data not found!")
            return redirect(url_for('dashboard'))
        
        user_data = result.data[0]
        
        # Get quiz scores (filter out Grand Test)
        scores_result = supabase.table('user_scores').select('*').eq('user_email', user_email).execute()
        scores_data = [s for s in scores_result.data if s.get('topic', '').lower() != 'grand test'] if scores_result.data else []
        
        # Get certificates (SAFE - handles table not existing)
        certificates = []
        try:
            certs_result = supabase.table('user_certificates').select('*').eq('user_email', user_email).execute()
            certificates = certs_result.data if certs_result.data else []
        except Exception as e:
            print(f"Warning: Could not fetch certificates: {e}")
            # Continue without certificates
        
        # Generate resume data
        resume_data = generate_complete_resume(user_data, scores_data, certificates)
        
        return render_template('resume_builder.html', resume_data=resume_data)
        
    except Exception as e:
        print(f"Error in resume_draft route: {e}")
        flash("Error loading resume builder. Please try again.")
        return redirect(url_for('dashboard'))


# ==============================================================================
# FIX #5: Add to app.py - REMOVE DUPLICATE ROUTE (Line ~648)
# ==============================================================================

# REMOVE THIS DUPLICATE ROUTE ENTIRELY:
"""
@app.route('/resume_builder')
def resume_builder():
    # ... duplicate code ...
"""

# Keep only /resume_draft route


# ==============================================================================
# FIX #6: Update resume_generator.py - organize_skills() (Line ~140)
# ==============================================================================

# ADD THIS SAFETY CHECK at the beginning:
def organize_skills(self, strengths, certificates, all_topics):
    """Organize skills into professional categories"""
    all_skills = self.recommend_skills(strengths, certificates, all_topics)
    
    # SAFETY CHECK - handle empty skills
    if not all_skills:
        return {
            'programming': ['Python', 'C', 'Java'],
            'technologies': ['SQL', 'Git'],
            'tools': ['GitHub', 'Linux'],
            'soft_skills': ['Problem Solving', 'Team Collaboration']
        }
    
    # ... rest of function


# ==============================================================================
# TESTING SCRIPT
# ==============================================================================

print("""
✅ FIXES APPLIED

Test the fixes:
1. python app.py
2. Login and go to Resume Draft
3. Try uploading a certificate
4. Check if resume generates without errors

If you still get errors, share the EXACT error message!
""")