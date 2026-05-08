"""Verification script for database indices implementation."""

import sys
from pathlib import Path

# Read the modified files and verify the changes
def verify_implementation():
    backend_path = Path(__file__).parent
    
    # Check database.py
    db_file = backend_path / "app" / "core" / "database.py"
    db_content = db_file.read_text()
    
    print("=== Checking database.py ===")
    checks = [
        ("Import text from sqlalchemy", "from sqlalchemy import create_engine, event, text" in db_content),
        ("create_indices function defined", "def create_indices() -> None:" in db_content),
        ("Function has docstring", '"""Create database indices for query optimization."""' in db_content),
        ("idx_video_uploader_id index", "idx_video_uploader_id ON videos(uploader_id)" in db_content),
        ("idx_video_created_at index", "idx_video_created_at ON videos(created_at DESC)" in db_content),
        ("idx_video_category index", "idx_video_category ON videos(category)" in db_content),
        ("idx_comment_video_id index", "idx_comment_video_id ON comments(video_id)" in db_content),
        ("idx_comment_created_at index", "idx_comment_created_at ON comments(created_at DESC)" in db_content),
        ("idx_subscription_follower_id index", "idx_subscription_follower_id ON subscriptions(follower_id)" in db_content),
        ("idx_subscription_creator_id index", "idx_subscription_creator_id ON subscriptions(creator_id)" in db_content),
        ("IF NOT EXISTS clause used", "CREATE INDEX IF NOT EXISTS" in db_content),
        ("Using engine.begin()", "with engine.begin() as connection:" in db_content),
    ]
    
    db_passed = all(check[1] for check in checks)
    for desc, result in checks:
        status = "✓" if result else "✗"
        print(f"  {status} {desc}")
    
    # Check main.py
    print("\n=== Checking main.py ===")
    main_file = backend_path / "app" / "main.py"
    main_content = main_file.read_text()
    
    main_checks = [
        ("Import create_indices", "from app.core.database import Base, engine, create_indices" in main_content),
        ("Call create_indices in startup", "create_indices()" in main_content),
        ("In on_startup function", "@app.on_event(\"startup\")" in main_content and "create_indices()" in main_content),
    ]
    
    main_passed = all(check[1] for check in main_checks)
    for desc, result in main_checks:
        status = "✓" if result else "✗"
        print(f"  {status} {desc}")
    
    print("\n=== Summary ===")
    if db_passed and main_passed:
        print("✓ All checks passed!")
        return True
    else:
        print("✗ Some checks failed")
        return False

if __name__ == "__main__":
    success = verify_implementation()
    sys.exit(0 if success else 1)
