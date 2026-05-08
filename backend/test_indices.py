#!/usr/bin/env python
"""Test script to verify database indices are created correctly."""

import sys
import sqlite3
from app.main import app
from app.core.database import engine

def check_indices():
    """Check if all required indices exist in the database."""
    required_indices = [
        "idx_video_uploader_id",
        "idx_video_created_at",
        "idx_video_category",
        "idx_comment_video_id",
        "idx_comment_created_at",
        "idx_subscription_follower_id",
        "idx_subscription_creator_id",
    ]
    
    # Get the database connection
    with engine.connect() as connection:
        db_connection = connection.connection
        cursor = db_connection.cursor()
        
        # Query all indices from sqlite_master
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'")
        existing_indices = {row[0] for row in cursor.fetchall()}
        
        print("\n=== Database Indices Check ===")
        print(f"Required indices: {sorted(required_indices)}")
        print(f"Existing indices: {sorted(existing_indices)}")
        
        missing_indices = set(required_indices) - existing_indices
        if missing_indices:
            print(f"\n❌ FAILED: Missing indices: {missing_indices}")
            return False
        
        print("\n✓ SUCCESS: All required indices are present!")
        
        # Show details of each index
        print("\n=== Index Details ===")
        for idx_name in sorted(existing_indices):
            cursor.execute(f"PRAGMA index_info({idx_name})")
            columns = cursor.fetchall()
            print(f"{idx_name}: {columns}")
        
        cursor.close()
        return True

if __name__ == "__main__":
    try:
        # Trigger startup event
        print("Starting up application...")
        from app.main import on_startup
        on_startup()
        
        # Check indices
        success = check_indices()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
