import subprocess
import os

def backup_table(pg_dump_path, database_name, user, password, host, port, schema_name, table_name, output_file):
    try:
        # Construct the pg_dump command with the full path to pg_dump
        command = [
            pg_dump_path,
            '-h', host,
            '-p', port,
            '-U', user,
            '-t', f'{schema_name}."{table_name}"',  # Use schema and double quotes for case-sensitive table names
            '-F', 'c',  # Custom format
            '-f', output_file,
            database_name
        ]

        # Set the environment variable for password
        env = os.environ.copy()
        env['PGPASSWORD'] = password

        # Execute the command
        subprocess.run(command, env=env, check=True)
        print(f'Table {schema_name}.{table_name} backed up successfully to {output_file}')
    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')

# Usage example
DB_NAME = 'IEB1'
DB_USER = 'postgres'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_SCHEMA = 'public'  # Specify the schema, change if different
DB_TABLE = 'MC_productiondata'
# Prompt user for backup file name
# backup_filename = input("Enter backup file name (without extension): ")
BACKUP_FILE = f"C:/Users/1037117/Desktop/IEB Machine Shop/{DB_TABLE}.backup"
PG_DUMP_PATH = r"C:\Program Files\PostgreSQL\16\bin\pg_dump.exe"

backup_table(PG_DUMP_PATH, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA, DB_TABLE, BACKUP_FILE)
