#!/usr/bin/env python3
"""
Database migration script using Alembic.
"""
import subprocess
import sys

def run_migration():
    """Run database migrations."""
    try:
        # Run Alembic upgrade
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            cwd="."
        )

        if result.returncode == 0:
            print("Migration completed successfully!")
            print(result.stdout)
        else:
            print("Migration failed!")
            print(result.stderr)
            sys.exit(1)

    except FileNotFoundError:
        print("Alembic not found. Please install it with: pip install alembic")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
