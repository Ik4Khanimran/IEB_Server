import os
import subprocess
import os
# Code to take backup of Database
# Database connection details
DB_NAME = 'IEB1'
DB_USER = 'postgres'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '5432'
# Prompt user for backup file name
backup_filename = input("Enter backup file name (without extension): ")
BACKUP_FILE = f"D:/Server_Folders/Database_Backup/{backup_filename}.backup"  # Adjust the path and extension as needed

PG_DUMP_PATH = r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"

# Set the environment variable for the password
os.environ['PGPASSWORD'] = DB_PASSWORD

# Create the pg_dump command
command = [
    PG_DUMP_PATH,
    '--file', BACKUP_FILE,
    '--host', DB_HOST,
    '--port', DB_PORT,
    '--username', DB_USER,
    '--no-password',
    '--format=c',  # Custom format
    '--verbose',
    DB_NAME
]

try:
    # Run the pg_dump command
    subprocess.run(command, check=True)
    print("Backup completed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Backup failed: {e}")
finally:
    # Clean up the environment variable
    del os.environ['PGPASSWORD']
