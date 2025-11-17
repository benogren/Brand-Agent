#!/usr/bin/env python3
"""
Database Migration Runner for AI Brand Studio
Executes SQL migration files in order to set up the database schema.
"""

import os
import sys
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_db_connection():
    """Create database connection from DATABASE_URL environment variable."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError(
            "DATABASE_URL environment variable not set. "
            "Please configure .env file with your database connection string."
        )

    try:
        conn = psycopg2.connect(database_url)
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to database: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure Cloud SQL instance is running")
        print("2. Verify DATABASE_URL is correct in .env")
        print("3. If using Cloud SQL Proxy, ensure it's running:")
        print("   ./cloud-sql-proxy PROJECT:REGION:INSTANCE")
        sys.exit(1)

def create_migrations_table(conn):
    """Create migrations tracking table if it doesn't exist."""
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version VARCHAR(255) PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        conn.commit()
    print("✅ Migrations tracking table ready")

def get_applied_migrations(conn):
    """Get list of already applied migrations."""
    with conn.cursor() as cur:
        cur.execute("SELECT version FROM schema_migrations ORDER BY version;")
        return {row[0] for row in cur.fetchall()}

def get_pending_migrations(migrations_dir, applied):
    """Get list of migrations that haven't been applied yet."""
    migration_files = sorted(migrations_dir.glob('*.sql'))
    pending = []

    for migration_file in migration_files:
        version = migration_file.stem  # filename without extension
        if version not in applied:
            pending.append((version, migration_file))

    return pending

def apply_migration(conn, version, migration_file):
    """Apply a single migration file."""
    print(f"\n📝 Applying migration: {version}")

    # Read migration SQL
    with open(migration_file, 'r') as f:
        sql = f.read()

    try:
        with conn.cursor() as cur:
            # Execute migration SQL
            cur.execute(sql)

            # Record migration as applied
            cur.execute(
                "INSERT INTO schema_migrations (version) VALUES (%s);",
                (version,)
            )

            conn.commit()
        print(f"✅ Migration {version} applied successfully")
        return True
    except Exception as e:
        conn.rollback()
        print(f"❌ Error applying migration {version}: {e}")
        return False

def main():
    """Main migration runner."""
    print("=== AI Brand Studio - Database Migration Runner ===\n")

    # Get project root and migrations directory
    project_root = Path(__file__).parent.parent
    migrations_dir = project_root / 'migrations'

    if not migrations_dir.exists():
        print(f"Error: Migrations directory not found at {migrations_dir}")
        sys.exit(1)

    # Connect to database
    print("Connecting to database...")
    conn = get_db_connection()
    print("✅ Connected to database\n")

    try:
        # Set up migrations tracking
        create_migrations_table(conn)

        # Get applied and pending migrations
        applied = get_applied_migrations(conn)
        pending = get_pending_migrations(migrations_dir, applied)

        if applied:
            print(f"\n📊 Already applied: {len(applied)} migrations")
            for version in sorted(applied):
                print(f"   ✓ {version}")

        if not pending:
            print("\n✅ All migrations are up to date!")
            return

        print(f"\n📋 Pending migrations: {len(pending)}")
        for version, _ in pending:
            print(f"   - {version}")

        # Apply pending migrations
        print("\n" + "="*50)
        for version, migration_file in pending:
            success = apply_migration(conn, version, migration_file)
            if not success:
                print(f"\n❌ Migration failed. Stopping.")
                sys.exit(1)

        print("\n" + "="*50)
        print("✅ All migrations applied successfully!")

    finally:
        conn.close()
        print("\n🔌 Database connection closed")

if __name__ == '__main__':
    main()
