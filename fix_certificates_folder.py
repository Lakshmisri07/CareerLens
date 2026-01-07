"""
Diagnostic and fix script for certificates folder issue
Run this to fix the FileExistsError
"""

import os
import shutil

def fix_certificates_folder():
    """Fix the certificates folder issue"""
    
    print("="*60)
    print("Certificate Folder Diagnostic & Fix")
    print("="*60)
    
    # Check static folder
    print("\n[1] Checking static folder...")
    if not os.path.exists('static'):
        print("❌ 'static' folder doesn't exist!")
        print("Creating 'static' folder...")
        os.makedirs('static')
        print("✅ Created 'static' folder")
    else:
        print("✅ 'static' folder exists")
    
    # Check certificates path
    cert_path = 'static/certificates'
    print(f"\n[2] Checking '{cert_path}'...")
    
    if os.path.exists(cert_path):
        if os.path.isfile(cert_path):
            print(f"❌ '{cert_path}' exists but it's a FILE, not a folder!")
            print("This is the problem. Fixing...")
            
            # Backup the file
            backup_name = 'static/certificates.backup'
            shutil.move(cert_path, backup_name)
            print(f"✅ Moved file to '{backup_name}'")
            
            # Create the folder
            os.makedirs(cert_path)
            print(f"✅ Created '{cert_path}' folder")
            
        elif os.path.isdir(cert_path):
            print(f"✅ '{cert_path}' exists and is a folder")
            
            # Check if writable
            test_file = os.path.join(cert_path, 'test.txt')
            try:
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print("✅ Folder is writable")
            except Exception as e:
                print(f"❌ Folder is not writable: {e}")
                print("Try running as administrator or check folder permissions")
    else:
        print(f"'{cert_path}' doesn't exist. Creating...")
        try:
            os.makedirs(cert_path)
            print(f"✅ Created '{cert_path}' folder")
        except Exception as e:
            print(f"❌ Failed to create folder: {e}")
            return False
    
    # Final verification
    print("\n[3] Final verification...")
    if os.path.isdir(cert_path):
        print("✅ All checks passed!")
        print(f"\nYou can now run: python app.py")
        return True
    else:
        print("❌ Something is still wrong")
        print("\nManual fix:")
        print(f"1. Open File Explorer")
        print(f"2. Navigate to your project folder")
        print(f"3. Delete any file named 'certificates' in the 'static' folder")
        print(f"4. Create a new folder: 'static\\certificates'")
        print(f"5. Run this script again")
        return False

if __name__ == '__main__':
    success = fix_certificates_folder()
    
    print("\n" + "="*60)
    if success:
        print("✅ FIXED! You can now start your app.")
    else:
        print("⚠️  Manual intervention needed. See instructions above.")
    print("="*60)