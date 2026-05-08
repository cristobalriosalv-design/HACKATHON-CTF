#!/usr/bin/env python
"""Test that the modified files can be imported."""

import sys
import os

sys.path.insert(0, os.getcwd())

try:
    print("Testing imports...")
    
    print("  - Importing dependencies...")
    from app import dependencies
    print("    ✓ app.dependencies")
    
    print("  - Checking get_limiter function...")
    assert hasattr(dependencies, 'get_limiter'), "get_limiter not found in dependencies"
    print("    ✓ get_limiter function exists")
    
    print("  - Importing video routes...")
    from app.api.routes import videos
    print("    ✓ app.api.routes.videos")
    
    print("  - Importing user routes...")
    from app.api.routes import users
    print("    ✓ app.api.routes.users")
    
    print("\n✓ All imports successful!")
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
