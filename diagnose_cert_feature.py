#!/usr/bin/env python3
"""
Quick fix for certificate folder issues
Run this if you're getting FileExistsError
"""

import os
import shutil

def fix_certificates():
    print("="*60)
    print("🔧 FIXING CERTIFICATE FOLDER")
    print("="*60)
    
    cert_path = 'static/certificates'
    
    # Step 1: Check static folder
    if not os.path.exists('static'):
        print("\n[1] Creating 'static' folder...")
        os.makedirs('static')
        print("✅ Created")
    else:
        print("\n[1] ✅ 'static' folder exists")
    
    # Step 2: Fix certificates issue
    print(f"\n[2] Checking '{cert_path}'...")
    
    if os.path.exists(cert_path):
        if os.path.isfile(cert_path):
            print(f"❌ '{cert_path}' is a FILE!")
            print("   Renaming to certificates.backup...")
            
            backup = 'static/certificates.backup'
            if os.path.exists(backup):
                os.remove(backup)
            
            shutil.move(cert_path, backup)
            print(f"✅ Moved to '{backup}'")
            
            os.makedirs(cert_path)
            print(f"✅ Created '{cert_path}' folder")
        else:
            print(f"✅ '{cert_path}' is already a folder")
    else:
        print(f"'{cert_path}' doesn't exist. Creating...")
        os.makedirs(cert_path)
        print(f"✅ Created '{cert_path}' folder")
    
    # Step 3: Test writability
    print("\n[3] Testing folder permissions...")
    test_file = os.path.join(cert_path, '.test')
    try:
        with open(test_file, 'w') as f:
            f.write('test')
        os.remove(test_file)
        print("✅ Folder is writable")
    except Exception as e:
        print(f"❌ Cannot write to folder: {e}")
        return False
    
    # Step 4: Check .gitkeep
    gitkeep = os.path.join(cert_path, '.gitkeep')
    if not os.path.exists(gitkeep):
        with open(gitkeep, 'w') as f:
            f.write('')
        print("\n[4] ✅ Created .gitkeep file")
    
    print("\n" + "="*60)
    print("✅ CERTIFICATE FOLDER FIXED!")
    print("="*60)
    print("\nYou can now run: python app.py")
    print("="*60)
    return True

if __name__ == '__main__':
    success = fix_certificates()
    exit(0 if success else 1)