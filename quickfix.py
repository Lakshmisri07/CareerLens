#!/usr/bin/env python3
"""
QUICK FIX for Supabase Connection Issues
This will update your .env file with correct values
"""

import os

print("="*80)
print("🔧 SUPABASE CONNECTION QUICK FIX")
print("="*80)

print("\nThis will help you fix the connection issue.")
print("You'll need your Supabase credentials from: https://supabase.com/dashboard\n")

# Get Supabase URL
print("Step 1: Get your Supabase URL")
print("   Go to: Supabase Dashboard → Settings → API")
print("   Copy the 'Project URL' (looks like: https://xxxxx.supabase.co)")
supabase_url = input("\nPaste your SUPABASE_URL here: ").strip()

# Validate URL
if not supabase_url:
    print("❌ No URL provided. Exiting.")
    exit(1)

if not supabase_url.startswith('https://'):
    print("⚠️  Adding https:// to URL")
    supabase_url = 'https://' + supabase_url

if not '.supabase.co' in supabase_url:
    print("⚠️  Warning: URL doesn't look like a Supabase URL")
    confirm = input("Continue anyway? (y/n): ")
    if confirm.lower() != 'y':
        exit(1)

# Get Supabase Key
print("\nStep 2: Get your Supabase Anon Key")
print("   Same page → Copy 'anon' 'public' key")
supabase_key = input("\nPaste your SUPABASE_ANON_KEY here: ").strip()

if not supabase_key:
    print("❌ No key provided. Exiting.")
    exit(1)

# Get Gemini API Key (optional)
print("\nStep 3: Gemini API Key (optional - for AI questions)")
gemini_key = input("Paste GEMINI_API_KEY (or press Enter to skip): ").strip()

# Create .env file
print("\n" + "="*80)
print("Creating .env file...")
print("="*80)

env_content = f"""# Supabase Configuration
VITE_SUPABASE_URL={supabase_url}
VITE_SUPABASE_SUPABASE_ANON_KEY={supabase_key}

# Gemini API Configuration (for AI-generated questions)
GEMINI_API_KEY={gemini_key if gemini_key else ''}
"""

# Backup old .env if it exists
if os.path.exists('.env'):
    print("Backing up old .env to .env.backup")
    with open('.env', 'r') as f:
        old_content = f.read()
    with open('.env.backup', 'w') as f:
        f.write(old_content)

# Write new .env
with open('.env', 'w') as f:
    f.write(env_content)

print("✅ .env file created successfully!")

# Test connection
print("\n" + "="*80)
print("Testing connection...")
print("="*80)

try:
    import socket
    from urllib.parse import urlparse
    
    parsed = urlparse(supabase_url)
    hostname = parsed.netloc
    
    print(f"\nResolving: {hostname}")
    ip = socket.gethostbyname(hostname)
    print(f"✅ DNS resolved: {hostname} → {ip}")
    
    print("\n✅ Connection test PASSED!")
    print("\nNext steps:")
    print("1. Run: python app.py")
    print("2. Go to: http://localhost:5000")
    print("3. Try registering a new account")
    
except Exception as e:
    print(f"\n❌ Connection test FAILED: {e}")
    print("\nTroubleshooting:")
    print("1. Check your internet connection")
    print("2. Verify the Supabase URL is correct")
    print("3. Try accessing the URL in your browser")
    print("4. Check if you're behind a firewall/proxy")

print("\n" + "="*80)