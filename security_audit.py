#!/usr/bin/env python3
"""
Security Audit Script - Check for leaked API keys
Run this to see if you have security issues
"""

import os
import subprocess
import re

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_env_file():
    """Check if .env file exists and is in .gitignore"""
    print_header("1. Checking .env file")
    
    if os.path.exists('.env'):
        print("✅ .env file found")
        
        # Check if it has keys
        with open('.env', 'r') as f:
            content = f.read()
            if 'GEMINI' in content or 'AIza' in content:
                print("✅ .env contains API keys")
            else:
                print("⚠️  .env exists but no GEMINI keys found")
    else:
        print("❌ .env file NOT found")
        print("   You need to create .env with your API keys")

def check_gitignore():
    """Check if .gitignore excludes .env"""
    print_header("2. Checking .gitignore")
    
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'r') as f:
            content = f.read()
            
        if '.env' in content or '*.env' in content:
            print("✅ .gitignore includes .env")
        else:
            print("❌ .gitignore does NOT exclude .env")
            print("   CRITICAL: Add '.env' to .gitignore NOW!")
    else:
        print("❌ .gitignore file NOT found")
        print("   Create .gitignore and add .env to it")

def check_git_status():
    """Check if .env is staged/tracked"""
    print_header("3. Checking Git Status")
    
    try:
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if '.env' in result.stdout:
            print("❌ CRITICAL: .env is being tracked by git!")
            print("   Run: git rm --cached .env")
            print("   Then add .env to .gitignore")
        else:
            print("✅ .env is not in git staging area")
    except:
        print("⚠️  Could not check git status (git not initialized?)")

def search_for_keys_in_code():
    """Search for hardcoded API keys"""
    print_header("4. Searching for Hardcoded Keys")
    
    found_issues = []
    
    # Patterns to search for
    patterns = [
        r'AIza[0-9A-Za-z_-]{35}',  # Google API keys
        r'sk-[0-9A-Za-z]{48}',      # OpenAI keys
        r'GEMINI_API_KEY\s*=\s*["\'][^"\']+["\']',  # Hardcoded assignments
    ]
    
    # Files to check
    for root, dirs, files in os.walk('.'):
        # Skip common directories
        dirs[:] = [d for d in dirs if d not in ['.git', 'venv', 'node_modules', '__pycache__', '.vscode']]
        
        for file in files:
            if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx', '.env')):
                if file == '.env':  # Skip .env file itself
                    continue
                    
                filepath = os.path.join(root, file)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        
                    for pattern in patterns:
                        matches = re.findall(pattern, content)
                        if matches:
                            found_issues.append({
                                'file': filepath,
                                'pattern': pattern,
                                'matches': matches
                            })
                except:
                    pass
    
    if found_issues:
        print("❌ CRITICAL: Found potential hardcoded keys:")
        for issue in found_issues:
            print(f"\n   File: {issue['file']}")
            print(f"   Found: {issue['matches'][0][:20]}...")
    else:
        print("✅ No hardcoded keys found in code files")

def check_git_history():
    """Check if keys exist in git history"""
    print_header("5. Checking Git History (last 10 commits)")
    
    try:
        result = subprocess.run(['git', 'log', '-p', '-10'], 
                              capture_output=True, text=True)
        
        if 'AIza' in result.stdout or 'GEMINI_API_KEY' in result.stdout:
            print("❌ CRITICAL: API keys found in git history!")
            print("   Your keys are PUBLIC if pushed to GitHub!")
            print("\n   IMMEDIATE ACTION REQUIRED:")
            print("   1. Delete keys in Google AI Studio")
            print("   2. Create new keys")
            print("   3. Clean git history (see security guide)")
        else:
            print("✅ No obvious keys found in recent history")
    except:
        print("⚠️  Could not check git history")

def check_requirements():
    """Check if python-dotenv is installed"""
    print_header("6. Checking Dependencies")
    
    try:
        import dotenv
        print("✅ python-dotenv is installed")
    except ImportError:
        print("⚠️  python-dotenv NOT installed")
        print("   Run: pip install python-dotenv")

def generate_gitignore():
    """Generate a proper .gitignore if needed"""
    print_header("7. Generate .gitignore")
    
    if os.path.exists('.gitignore'):
        print("ℹ️  .gitignore already exists")
        response = input("   Do you want to update it? (y/n): ")
        if response.lower() != 'y':
            return
    
    gitignore_content = """# Environment variables - NEVER COMMIT THESE
.env
.env.local
.env.production
.env.test
*.env

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/
env/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log

# Database
*.db
*.sqlite

# Secrets
secrets/
keys/
*.pem
*.key

# Certificates
static/certificates/*
!static/certificates/.gitkeep
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content)
    
    print("✅ .gitignore created/updated")

def main():
    print("""
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          🔐 API KEY SECURITY AUDIT                        ║
║          CareerLens Security Check                        ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    # Run all checks
    check_env_file()
    check_gitignore()
    check_git_status()
    search_for_keys_in_code()
    check_git_history()
    check_requirements()
    
    print_header("RECOMMENDATIONS")
    
    print("""
📋 IMMEDIATE ACTIONS:

1. If ANY checks failed, DO NOT push to GitHub yet!

2. If keys found in history:
   ❌ DELETE all API keys in Google AI Studio NOW
   ✅ Create new keys
   ✅ Add to .env file
   ✅ Clean git history (see security guide)

3. If .env not in .gitignore:
   ✅ Run: echo ".env" >> .gitignore
   ✅ Run: git rm --cached .env (if tracked)

4. Verify security:
   ✅ Run: git status (should NOT show .env)
   ✅ Check files before committing

📚 Read the full security guide in API_KEY_SECURITY_GUIDE.md
""")
    
    # Offer to generate .gitignore
    if not os.path.exists('.gitignore') or '.env' not in open('.gitignore').read():
        response = input("\n❓ Generate/update .gitignore now? (y/n): ")
        if response.lower() == 'y':
            generate_gitignore()

if __name__ == "__main__":
    main()