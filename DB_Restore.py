import subprocess
import os
#  Code to restore Database, There is two step, first create a new databse & then restore backup on new DB
# Database connection details
DB_NAME = 'IEB1'
DB_USER = 'postgres'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '5432'
BACKUP_FILE = r"C:/Users/1037117/Desktop/03102024.backup"
PG_RESTORE_PATH = r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe"
PSQL_PATH = r"C:\Program Files\PostgreSQL\16\bin\psql.exe"

# Set the environment variable for the password
os.environ['PGPASSWORD'] = DB_PASSWORD

# Create the pg_restore command
create_db_command = [
    PSQL_PATH,
    '--host', DB_HOST,
    '--port', DB_PORT,
    '--username', DB_USER,
    '--no-password',
    '--command', f'CREATE DATABASE {DB_NAME};'
]

try:
    # Create the database
    subprocess.run(create_db_command, check=True)
    print(f"Database {DB_NAME} created successfully.")
except subprocess.CalledProcessError as e:
    print(f"Database creation failed: {e}")

# Create the pg_restore command
restore_command = [
    PG_RESTORE_PATH,
    '--host', DB_HOST,
    '--port', DB_PORT,
    '--username', DB_USER,
    '--no-password',
    '--dbname', DB_NAME,
    '--verbose',
    BACKUP_FILE
]

try:
    # Run the pg_restore command
    subprocess.run(restore_command, check=True)
    print("Restore completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Restore failed: {e}")
finally:
    # Clean up the environment variable
    del os.environ['PGPASSWORD']
