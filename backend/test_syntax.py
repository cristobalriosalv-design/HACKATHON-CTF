#!/usr/bin/env python
"""Test syntax of modified files."""

import sys
import py_compile

files_to_check = [
    "app/api/routes/videos.py",
    "app/api/routes/users.py",
    "app/dependencies.py",
]

errors = []
for file in files_to_check:
    try:
        py_compile.compile(file, doraise=True)
        print(f"✓ {file}: OK")
    except py_compile.PyCompileError as e:
        print(f"✗ {file}: ERROR")
        print(f"  {e}")
        errors.append(file)

if errors:
    print(f"\n{len(errors)} file(s) with syntax errors")
    sys.exit(1)
else:
    print(f"\nAll {len(files_to_check)} files have valid syntax!")
    sys.exit(0)
