#!/usr/bin/env python3
"""
CareerLens Complete Diagnostic & Fix Script
This will identify all issues and provide exact solutions
"""

import os
import sys

def print_header(text):
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80)

def print_step(step_num, text):
    print(f"\n[Step {step_num}] {text}")
    print("-"*80)

def main():
    print_header("🔍 CAREERLENS COMPLETE DIAGNOSTIC")
    
    issues = []
    fixes = []
    
    # Step 1: Check Python version
    print_step(1, "Checking Python Version")
    python_version = sys.version_info
    print(f"Python Version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        issues.append("Python version too old")
        fixes.append("Upgrade to Python 3.8 or higher")
    else:
        print("✅ Python version OK")
    
    # Step 2: Check .env file
    print_step(2, "Checking Environment File")
    
    if not os.path.exists('.env'):
        issues.append(".env file missing")
        fixes.append("Create .env file with required credentials")
        print("❌ .env file NOT FOUND")
    else:
        print("✅ .env file exists")
        
        # Load and check variables
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # Check Supabase credentials
            supabase_url = os.getenv('VITE_SUPABASE_URL')
            supabase_key = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
            gemini_key = os.getenv('GEMINI_API_KEY')
            
            if not supabase_url:
                issues.append("VITE_SUPABASE_URL missing in .env")
                fixes.append("Add VITE_SUPABASE_URL to .env file")
                print("❌ VITE_SUPABASE_URL not found")
            else:
                print(f"✅ VITE_SUPABASE_URL found: {supabase_url[:30]}...")
            
            if not supabase_key:
                issues.append("VITE_SUPABASE_SUPABASE_ANON_KEY missing in .env")
                fixes.append("Add VITE_SUPABASE_SUPABASE_ANON_KEY to .env file")
                print("❌ VITE_SUPABASE_SUPABASE_ANON_KEY not found")
            else:
                print(f"✅ VITE_SUPABASE_SUPABASE_ANON_KEY found: {supabase_key[:30]}...")
            
            if not gemini_key:
                issues.append("GEMINI_API_KEY missing in .env")
                fixes.append("Add GEMINI_API_KEY to .env file")
                print("❌ GEMINI_API_KEY not found")
            else:
                print(f"✅ GEMINI_API_KEY found: {gemini_key[:20]}...")
                
        except ImportError:
            issues.append("python-dotenv not installed")
            fixes.append("Run: pip install python-dotenv")
            print("❌ python-dotenv not installed")
    
    # Step 3: Check required packages
    print_step(3, "Checking Required Packages")
    
    required_packages = {
        'flask': 'Flask',
        'supabase': 'supabase',
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
            issues.append(f"{display_name} not installed")
    
    if missing_packages:
        fixes.append(f"Install packages: pip install {' '.join(missing_packages)}")
    
    # Step 4: Check critical files
    print_step(4, "Checking Critical Files")
    
    critical_files = [
        'app.py',
        'ai_question_generator.py',
        'ml_model.py',
        'templates/index.html',
        'templates/dashboard.html',
        'templates/quiz.html'
    ]
    
    for filepath in critical_files:
        if os.path.exists(filepath):
            print(f"✅ {filepath}")
        else:
            print(f"❌ {filepath} NOT FOUND")
            issues.append(f"{filepath} missing")
            fixes.append(f"Restore {filepath} from backup or repository")
    
    # Step 5: Test Supabase connection (if packages installed)
    if 'supabase' not in [p for p, _ in required_packages.items() if p in missing_packages]:
        print_step(5, "Testing Supabase Connection")
        
        try:
            from dotenv import load_dotenv
            from supabase import create_client
            
            load_dotenv()
            
            supabase_url = os.getenv('VITE_SUPABASE_URL')
            supabase_key = os.getenv('VITE_SUPABASE_SUPABASE_ANON_KEY')
            
            if supabase_url and supabase_key:
                try:
                    supabase = create_client(supabase_url, supabase_key)
                    
                    # Try to query users table
                    result = supabase.table('users').select('*').limit(1).execute()
                    print("✅ Supabase connection successful")
                    print(f"✅ Users table accessible")
                    
                    # Try to query user_scores table
                    result = supabase.table('user_scores').select('*').limit(1).execute()
                    print("✅ User_scores table accessible")
                    
                except Exception as e:
                    print(f"❌ Supabase connection failed: {str(e)[:100]}")
                    issues.append("Supabase connection failed")
                    fixes.append("Check Supabase credentials and ensure tables are created")
            else:
                print("⚠️ Skipping Supabase test - credentials missing")
                
        except Exception as e:
            print(f"❌ Error testing Supabase: {str(e)[:100]}")
            issues.append("Supabase test failed")
    
    # Step 6: Test Gemini API (if packages installed)
    if 'google.generativeai' not in [p for p, _ in required_packages.items() if p in missing_packages]:
        print_step(6, "Testing Gemini API")
        
        try:
            from dotenv import load_dotenv
            import google.generativeai as genai
            
            load_dotenv()
            gemini_key = os.getenv('GEMINI_API_KEY')
            
            if gemini_key:
                try:
                    genai.configure(api_key=gemini_key)
                    
                    # Try different models
                    models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
                    model_found = False
                    
                    for model_name in models:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content("Say OK")
                            print(f"✅ Gemini API working with {model_name}")
                            model_found = True
                            break
                        except:
                            continue
                    
                    if not model_found:
                        print("❌ No working Gemini model found")
                        issues.append("Gemini API not working")
                        fixes.append("Check GEMINI_API_KEY validity or get new key from https://aistudio.google.com/app/apikey")
                        
                except Exception as e:
                    print(f"❌ Gemini API failed: {str(e)[:100]}")
                    issues.append("Gemini API failed")
                    fixes.append("Verify GEMINI_API_KEY is valid")
            else:
                print("⚠️ Skipping Gemini test - API key missing")
                
        except Exception as e:
            print(f"❌ Error testing Gemini: {str(e)[:100]}")
    
    # Generate Report
    print_header("📊 DIAGNOSTIC REPORT")
    
    if not issues:
        print("\n✅ ✅ ✅ ALL CHECKS PASSED! ✅ ✅ ✅")
        print("\n🚀 Your application is ready to run!")
        print("\nTo start the application:")
        print("   python app.py")
        print("\nOr:")
        print("   python3 app.py")
        print("\nThen open: http://localhost:5000")
        
    else:
        print(f"\n❌ Found {len(issues)} issue(s):\n")
        for i, issue in enumerate(issues, 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 SOLUTIONS:\n")
        for i, fix in enumerate(fixes, 1):
            print(f"   {i}. {fix}")
        
        print("\n" + "="*80)
        print("💡 QUICK FIX GUIDE")
        print("="*80)
        
        # Provide specific fix commands
        if missing_packages:
            print("\n1️⃣ Install missing packages:")
            print("   pip install Flask supabase scikit-learn numpy google-generativeai python-dotenv")
            print("   Or if using pip3:")
            print("   pip3 install Flask supabase scikit-learn numpy google-generativeai python-dotenv")
        
        if 'VITE_SUPABASE_URL' in str(issues) or 'VITE_SUPABASE_SUPABASE_ANON_KEY' in str(issues):
            print("\n2️⃣ Fix .env file:")
            print("   Create/update .env with:")
            print("   VITE_SUPABASE_URL=your_supabase_url_here")
            print("   VITE_SUPABASE_SUPABASE_ANON_KEY=your_supabase_anon_key_here")
            print("   GEMINI_API_KEY=your_gemini_api_key_here")
        
        if 'GEMINI_API_KEY' in str(issues):
            print("\n3️⃣ Get Gemini API Key:")
            print("   Visit: https://aistudio.google.com/app/apikey")
            print("   Create a new API key and add to .env file")
        
        if 'Supabase' in str(issues):
            print("\n4️⃣ Check Supabase Setup:")
            print("   - Verify your Supabase project is active")
            print("   - Ensure tables 'users' and 'user_scores' exist")
            print("   - Check that RLS policies are configured")
    
    print("\n" + "="*80)
    print("📞 Need more help? Run this script again after applying fixes")
    print("="*80)

if __name__ == '__main__':
    main()