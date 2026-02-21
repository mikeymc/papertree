import os
import sys
import yoyo
import psycopg

def run_debug_migration():
    TEST_DB = 'debug_migration_test'
    USER = 'lynch'
    PASSWORD = 'lynch_dev_password'
    HOST = 'localhost'
    PORT = 5432

    print(f"Connecting to postgres to create {TEST_DB}...")
    conn = psycopg.connect(
        dbname='postgres',
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        autocommit=True
    )
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB}")
    cursor.execute(f"CREATE DATABASE {TEST_DB}")
    cursor.close()
    conn.close()

    yoyo_uri = f"postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{TEST_DB}"
    print(f"Applying migrations to {yoyo_uri}...")
    
    backend = yoyo.get_backend(yoyo_uri)
    migrations_dir = os.path.join(os.getcwd(), 'backend', 'migrations')
    migrations = yoyo.read_migrations(migrations_dir)
    
    try:
        backend.apply_migrations(backend.to_apply(migrations))
        print("✓ Migrations applied successfully!")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_debug_migration()
