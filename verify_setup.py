#!/usr/bin/env python3
"""
Quick verification script to ensure everything is set up correctly
Run this before starting your Flask application
"""

import os
import sys

def check_file_exists(filepath):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"  ✅ {filepath}")
        return True
    else:
        print(f"  ❌ {filepath} - NOT FOUND!")
        return False

def check_environment():
    """Check environment variables"""
    print("\n📋 Checking Environment Variables...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    issues = []
    
    # Check API key
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"  ✅ GEMINI_API_KEY found ({api_key[:20]}...)")
    else:
        print("  ❌ GEMINI_API_KEY not found in .env")
        issues.append("Missing GEMINI_API_KEY in .env file")
    
    return len(issues) == 0, issues

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking Dependencies...")
    
    required_packages = [
        ('flask', 'Flask'),
        ('flask_mysqldb', 'Flask-MySQLdb'),
        ('sklearn', 'scikit-learn'),
        ('numpy', 'NumPy'),
        ('google.generativeai', 'google-generativeai'),
        ('dotenv', 'python-dotenv'),
    ]
    
    issues = []
    
    for package_name, display_name in required_packages:
        try:
            __import__(package_name)
            print(f"  ✅ {display_name}")
        except ImportError:
            print(f"  ❌ {display_name} - NOT INSTALLED!")
            issues.append(f"Install {display_name}: pip install {package_name}")
    
    return len(issues) == 0, issues

def check_files():
    """Check if all required files exist"""
    print("\n📁 Checking Required Files...")
    
    required_files = [
        'app.py',
        'ai_question_generator.py',
        'ml_model.py',
        'requirements.txt',
        '.env',
        'templates/index.html',
        'templates/dashboard.html',
        'templates/technical.html',
        'templates/quiz.html',
        'templates/suggestions.html',
        'templates/grand_test.html',
    ]
    
    all_exist = True
    for filepath in required_files:
        if not check_file_exists(filepath):
            all_exist = False
    
    return all_exist

def test_database_connection():
    """Test MySQL database connection"""
    print("\n🗄️  Testing Database Connection...")
    
    try:
        import mysql.connector
        
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="placement_prep"
        )
        
        cursor = conn.cursor()
        
        # Check if required tables exist
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        required_tables = ['users', 'user_scores']
        
        for table in required_tables:
            if table in tables:
                print(f"  ✅ Table '{table}' exists")
            else:
                print(f"  ❌ Table '{table}' NOT FOUND!")
                return False, [f"Create table: {table}"]
        
        cursor.close()
        conn.close()
        
        print("  ✅ Database connection successful")
        return True, []
        
    except Exception as e:
        print(f"  ❌ Database connection failed: {e}")
        return False, [str(e)]

def test_ai_generation():
    """Test AI question generation"""
    print("\n🤖 Testing AI Question Generation...")
    
    try:
        from ai_question_generator import generate_quiz_questions
        
        questions = generate_quiz_questions('C', 'Arrays', 'beginner', 2)
        
        if len(questions) >= 2:
            print(f"  ✅ Generated {len(questions)} AI questions")
            print(f"  ✅ Sample question: {questions[0]['q'][:50]}...")
            return True, []
        else:
            print(f"  ⚠️  Only generated {len(questions)} questions")
            return False, ["AI generation returned fewer questions than requested"]
            
    except Exception as e:
        print(f"  ❌ AI generation failed: {e}")
        return False, [str(e)]

def test_branch_topics():
    """Test branch-specific topics"""
    print("\n🎓 Testing Branch-Specific Topics...")
    
    try:
        # Import after verifying file exists
        sys.path.insert(0, os.getcwd())
        from app import BRANCH_TOPICS
        
        branches = ['CSE', 'ECE', 'MECH', 'EEE', 'CIVIL', 'IT', 'AI/ML', 'DEFAULT']
        
        for branch in branches:
            if branch in BRANCH_TOPICS:
                topic_count = len(BRANCH_TOPICS[branch])
                print(f"  ✅ {branch}: {topic_count} topics")
            else:
                print(f"  ⚠️  {branch}: Not configured")
        
        return True, []
        
    except Exception as e:
        print(f"  ❌ Error checking branch topics: {e}")
        return False, [str(e)]

def main():
    """Run all verification checks"""
    print("="*80)
    print("🔍 CAREERLENS SETUP VERIFICATION")
    print("="*80)
    
    all_passed = True
    all_issues = []
    
    # Check files
    if not check_files():
        all_passed = False
        all_issues.append("Some required files are missing")
    
    # Check dependencies
    deps_ok, deps_issues = check_dependencies()
    if not deps_ok:
        all_passed = False
        all_issues.extend(deps_issues)
    
    # Check environment
    env_ok, env_issues = check_environment()
    if not env_ok:
        all_passed = False
        all_issues.extend(env_issues)
    
    # Check database
    db_ok, db_issues = test_database_connection()
    if not db_ok:
        all_passed = False
        all_issues.extend(db_issues)
    
    # Check AI generation (only if previous checks passed)
    if all_passed:
        ai_ok, ai_issues = test_ai_generation()
        if not ai_ok:
            all_passed = False
            all_issues.extend(ai_issues)
    
    # Check branch topics
    branch_ok, branch_issues = test_branch_topics()
    if not branch_ok:
        all_passed = False
        all_issues.extend(branch_issues)
    
    # Final report
    print("\n" + "="*80)
    print("📊 VERIFICATION RESULTS")
    print("="*80)
    
    if all_passed:
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 You're ready to start the application:")
        print("   python app.py")
        print("\n💡 Tips:")
        print("   - Login with different branch users to test branch-specific topics")
        print("   - Take quizzes to verify scoring is working correctly")
        print("   - Check console output for detailed debug information")
        print("   - Run test_scoring_fix.py for comprehensive scoring tests")
    else:
        print("❌ SOME CHECKS FAILED!")
        print("\n🔧 Issues to fix:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
        print("\n📝 After fixing these issues, run this script again.")
    
    print("="*80)
    
    return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)