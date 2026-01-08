#!/usr/bin/env python3
"""
CareerLens Diagnostic Script
Run this to identify all errors before starting the app
"""

import os
import sys

print("="*70)
print("🔍 CAREERLENS DIAGNOSTIC TOOL")
print("="*70)

errors = []
warnings = []

# Check 1: Python version
print("\n[1/8] Checking Python version...")
if sys.version_info < (3, 8):
    errors.append("Python 3.8+ required")
    print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} (need 3.8+)")
else:
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")

# Check 2: Required files exist
print("\n[2/8] Checking required files...")
required_files = [
    'app.py',
    'ai_question_generator.py',
    'ml_model.py',
    'resume_generator.py',
    'certificate_manager.py',
    '.env',
    'requirements.txt'
]

for file in required_files:
    if not os.path.exists(file):
        errors.append(f"Missing file: {file}")
        print(f"❌ {file} not found")
    else:
        print(f"✅ {file}")

# Check 3: .env file configuration
print("\n[3/8] Checking .env configuration...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = {
        'GEMINI_API_KEY': os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY'),
        'VITE_SUPABASE_URL': os.getenv('VITE_SUPABASE_URL'),
        'VITE_SUPABASE_SUPABASE_ANON_KEY': os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
    }
    
    for key, value in env_vars.items():
        if not value:
            errors.append(f"Missing environment variable: {key}")
            print(f"❌ {key} not set")
        else:
            print(f"✅ {key} configured")
            
except Exception as e:
    errors.append(f"Error loading .env: {e}")
    print(f"❌ Error: {e}")

# Check 4: Required packages
print("\n[4/8] Checking installed packages...")
required_packages = {
    'flask': 'Flask',
    'google.genai': 'google-genai',
    'supabase': 'supabase',
    'sklearn': 'scikit-learn',
    'numpy': 'numpy',
    'dotenv': 'python-dotenv',
    'PIL': 'Pillow',
    'werkzeug': 'werkzeug'
}

for module, package in required_packages.items():
    try:
        __import__(module)
        print(f"✅ {package}")
    except ImportError:
        errors.append(f"Missing package: {package}")
        print(f"❌ {package} not installed")

# Check 5: Test Google GenAI import
print("\n[5/8] Testing Google GenAI SDK...")
try:
    from google import genai
    from google.genai import types
    print("✅ google-genai imports working")
    
    # Try to create client
    api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            print("✅ GenAI client initialized")
        except Exception as e:
            warnings.append(f"GenAI client warning: {e}")
            print(f"⚠️  Client init warning: {e}")
    else:
        warnings.append("Cannot test GenAI client (no API key)")
        print("⚠️  No API key to test client")
        
except ImportError as e:
    errors.append(f"GenAI import error: {e}")
    print(f"❌ Import error: {e}")

# Check 6: Verify certificate folder
print("\n[6/8] Checking certificate storage...")
cert_folder = 'static/certificates'
if not os.path.exists('static'):
    try:
        os.makedirs('static')
        print(f"✅ Created 'static' folder")
    except Exception as e:
        errors.append(f"Cannot create static folder: {e}")
        print(f"❌ Error: {e}")

if os.path.exists(cert_folder):
    if os.path.isfile(cert_folder):
        errors.append(f"{cert_folder} is a file, not a folder!")
        print(f"❌ {cert_folder} is a FILE (should be folder)")
    else:
        print(f"✅ {cert_folder} folder exists")
else:
    try:
        os.makedirs(cert_folder, exist_ok=True)
        print(f"✅ Created {cert_folder}")
    except Exception as e:
        errors.append(f"Cannot create {cert_folder}: {e}")
        print(f"❌ Error: {e}")

# Check 7: Test imports from app.py
print("\n[7/8] Testing app.py imports...")
try:
    from ai_question_generator import get_adaptive_questions
    print("✅ ai_question_generator.get_adaptive_questions")
except Exception as e:
    errors.append(f"Cannot import get_adaptive_questions: {e}")
    print(f"❌ Error: {e}")

try:
    from ml_model import analyze_user_performance, get_overall_readiness
    print("✅ ml_model imports")
except Exception as e:
    errors.append(f"Cannot import from ml_model: {e}")
    print(f"❌ Error: {e}")

try:
    from resume_generator import generate_complete_resume
    print("✅ resume_generator.generate_complete_resume")
except Exception as e:
    errors.append(f"Cannot import generate_complete_resume: {e}")
    print(f"❌ Error: {e}")

try:
    from certificate_manager import CertificateManager
    print("✅ certificate_manager.CertificateManager")
except Exception as e:
    errors.append(f"Cannot import CertificateManager: {e}")
    print(f"❌ Error: {e}")

# Check 8: Syntax check app.py
print("\n[8/8] Checking app.py syntax...")
try:
    import py_compile
    py_compile.compile('app.py', doraise=True)
    print("✅ app.py syntax valid")
except Exception as e:
    errors.append(f"app.py syntax error: {e}")
    print(f"❌ Syntax error: {e}")

# Summary
print("\n" + "="*70)
print("📊 DIAGNOSTIC SUMMARY")
print("="*70)

if errors:
    print(f"\n❌ {len(errors)} CRITICAL ERROR(S) FOUND:\n")
    for i, error in enumerate(errors, 1):
        print(f"   {i}. {error}")
    
    print("\n" + "="*70)
    print("🛠️  FIX THESE ERRORS BEFORE RUNNING APP:")
    print("="*70)
    
    if any('package' in e.lower() or 'import' in e.lower() for e in errors):
        print("\n1. Install missing packages:")
        print("   pip install -r requirements.txt")
    
    if any('api_key' in e.lower() or 'env' in e.lower() for e in errors):
        print("\n2. Configure .env file with:")
        print("   GEMINI_API_KEY=your_api_key_here")
        print("   VITE_SUPABASE_URL=your_supabase_url")
        print("   VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_key")
    
    if any('certificate' in e.lower() for e in errors):
        print("\n3. Run: python diagnose_cert_feature.py")

if warnings:
    print(f"\n⚠️  {len(warnings)} WARNING(S):\n")
    for i, warning in enumerate(warnings, 1):
        print(f"   {i}. {warning}")

if not errors:
    print("\n✅ ALL CHECKS PASSED!")
    print("\nYou can now run:")
    print("   python app.py")
else:
    print(f"\n❌ Found {len(errors)} error(s). Fix them before running app.py")

print("="*70)