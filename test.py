#!/usr/bin/env python3
"""
Script to find duplicate route definitions in app.py
"""

import re
from collections import defaultdict

print("="*80)
print("🔍 CHECKING FOR DUPLICATE ROUTES IN APP.PY")
print("="*80)

try:
    with open('app.py', 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
    
    # Find all route definitions
    routes = defaultdict(list)
    current_line = 0
    
    for i, line in enumerate(lines, 1):
        if '@app.route' in line:
            # Find the function name
            for j in range(i, min(i + 3, len(lines))):
                if lines[j-1].strip().startswith('def '):
                    func_name = lines[j-1].strip().split('(')[0].replace('def ', '')
                    routes[func_name].append((i, line.strip()))
                    break
    
    # Find duplicates
    duplicates = {name: locs for name, locs in routes.items() if len(locs) > 1}
    
    if duplicates:
        print("\n❌ FOUND DUPLICATE ROUTES:\n")
        for func_name, locations in duplicates.items():
            print(f"Function: {func_name}")
            print(f"Defined {len(locations)} times:")
            for line_num, route in locations:
                print(f"  Line {line_num}: {route}")
            print()
        
        print("="*80)
        print("🛠️  FIX INSTRUCTIONS:")
        print("="*80)
        print("\n1. Open app.py")
        print("2. Go to the line numbers shown above")
        print("3. DELETE one of the duplicate definitions (keep the newer one)")
        print("4. Save the file and restart Flask\n")
        
    else:
        print("\n✅ No duplicate routes found!")
        print("\nYour routes are clean. The error might be from a different issue.")
    
    # Check for quiz_details specifically
    if 'quiz_details' in routes:
        print("\n" + "="*80)
        print("📍 QUIZ_DETAILS ROUTE LOCATIONS:")
        print("="*80)
        for line_num, route in routes['quiz_details']:
            print(f"Line {line_num}: {route}")
            # Show context
            start = max(0, line_num - 2)
            end = min(len(lines), line_num + 5)
            print("\nContext:")
            for i in range(start, end):
                prefix = ">>> " if i == line_num - 1 else "    "
                print(f"{prefix}{i+1:4d}: {lines[i]}")
            print()

except FileNotFoundError:
    print("❌ ERROR: app.py not found in current directory")
    print("Please run this script from your CareerLens root directory")
except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("="*80)