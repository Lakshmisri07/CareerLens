#!/usr/bin/env python3
"""
Diagnostic Script for CareerLens
Identifies and reports all setup issues
"""

import sys
import os

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_step(step_num, text):
    print(f"\n[Step {step_num}] {text}")
    print("-"*70)

# Step 1: Check Python Version
print_header("🐍 CAREERLENS DIAGNOSTIC TOOL")
print_step(1, "Checking Python Version")

python_version = sys.version_info
print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")

if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
    print("❌ ERROR: Python 3.8 or higher required!")
    print("   Current version is too old. Please upgrade Python.")
    sys.exit(1)
else:
    print("✅ Python version OK")

# Step 2: Check Dependencies
print_step(2, "Checking Required Packages")

required_packages = {
    'flask': 'Flask',
    'flask_mysqldb': 'Flask-MySQLdb',
    'sklearn': 'scikit-learn',
    'numpy': 'numpy',
    'google.generativeai': 'google-generativeai',
    'dotenv': 'python-dotenv'
}

missing_packages = []

for package, display_name in required_packages.items():
    try:
        __import__(package)
        print(f"✅ {display_name} installed")
    except ImportError:
        print(f"❌ {display_name} NOT installed")
        missing_packages.append(display_name)

if missing_packages:
    print(f"\n⚠️ MISSING PACKAGES: {', '.join(missing_packages)}")
    print("\nTo install missing packages:")
    print("pip install Flask Flask-MySQLdb scikit-learn numpy google-generativeai python-dotenv")
    sys.exit(1)

# Step 3: Check .env file
print_step(3, "Checking Environment Configuration")

if not os.path.exists('.env'):
    print("❌ .env file NOT FOUND!")
    print("\nCreate a .env file with:")
    print("GEMINI_API_KEY=your_api_key_here")
    sys.exit(1)
else:
    print("✅ .env file exists")

from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY not found in .env file!")
    print("\nAdd this line to your .env file:")
    print("GEMINI_API_KEY=your_api_key_here")
    print("\nGet your API key from: https://aistudio.google.com/app/apikey")
    sys.exit(1)
else:
    print(f"✅ GEMINI_API_KEY found: {api_key[:20]}...")

# Step 4: Test Gemini API
print_step(4, "Testing Gemini API Connection")

try:
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    
    # Try different model names
    model_names = [
        'gemini-1.5-flash',
        'gemini-1.5-pro',
        'gemini-pro'
    ]
    
    model_loaded = False
    working_model = None
    
    for model_name in model_names:
        try:
            print(f"Testing {model_name}...", end=" ")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("Say 'working' in one word")
            print(f"✅ {model_name} works!")
            working_model = model_name
            model_loaded = True
            break
        except Exception as e:
            print(f"❌ Failed: {str(e)[:50]}")
    
    if not model_loaded:
        print("\n❌ No working Gemini models found!")
        print("\nPossible issues:")
        print("1. API key is invalid or expired")
        print("2. No internet connection")
        print("3. Gemini API service is down")
        print("\nGet a new API key: https://aistudio.google.com/app/apikey")
        sys.exit(1)
    else:
        print(f"\n✅ Gemini API working! Use model: {working_model}")
        print(f"\nUpdate ai_question_generator.py line 9 to:")
        print(f"model = genai.GenerativeModel('{working_model}')")

except Exception as e:
    print(f"❌ Gemini API Error: {e}")
    sys.exit(1)

# Step 5: Check MySQL
print_step(5, "Checking Database Connection")

try:
    import mysql.connector
    
    print("Attempting to connect to MySQL...")
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    print("✅ MySQL connection successful")
    
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES")
    databases = [db[0] for db in cursor.fetchall()]
    
    if 'placement_prep' in databases:
        print("✅ Database 'placement_prep' exists")
        
        # Check tables
        cursor.execute("USE placement_prep")
        cursor.execute("SHOW TABLES")
        tables = [table[0] for table in cursor.fetchall()]
        
        if 'users' in tables:
            print("✅ Table 'users' exists")
        else:
            print("❌ Table 'users' NOT FOUND")
            print("   Run the SQL setup script to create tables")
        
        if 'user_scores' in tables:
            print("✅ Table 'user_scores' exists")
        else:
            print("❌ Table 'user_scores' NOT FOUND")
            print("   Run the SQL setup script to create tables")
    else:
        print("❌ Database 'placement_prep' NOT FOUND")
        print("\nCreate database:")
        print("CREATE DATABASE placement_prep;")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Database Error: {e}")
    print("\nCommon solutions:")
    print("1. Start MySQL: sudo service mysql start")
    print("2. Check MySQL credentials in app.py")
    print("3. Create database: CREATE DATABASE placement_prep;")

# Step 6: Check Required Files
print_step(6, "Checking Required Files")

required_files = [
    'app.py',
    'ai_question_generator.py',
    'ml_model.py',
    'templates/index.html',
    'templates/dashboard.html',
    'templates/quiz.html'
]

missing_files = []

for filepath in required_files:
    if os.path.exists(filepath):
        print(f"✅ {filepath}")
    else:
        print(f"❌ {filepath} NOT FOUND")
        missing_files.append(filepath)

if missing_files:
    print(f"\n⚠️ Missing files: {', '.join(missing_files)}")

# Final Report
print_header("📊 DIAGNOSTIC SUMMARY")

if not missing_packages and api_key and model_loaded:
    print("\n✅ SYSTEM READY!")
    print("\n🚀 Next Steps:")
    print("1. Update ai_question_generator.py with working model name")
    print("2. Ensure database and tables exist")
    print("3. Run: python app.py")
    print("\n💡 If you still get errors, run: python app.py")
    print("   and share the error message for specific help.")
else:
    print("\n⚠️ SETUP INCOMPLETE")
    print("\nFix the issues above and run this script again.")

print("\n" + "="*70)