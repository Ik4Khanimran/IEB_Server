import subprocess
import os


def restore_table(pg_restore_path, database_name, user, password, host, port, schema_name, table_name, backup_file):
    try:
        # Check the contents of the backup file
        list_command = [
            pg_restore_path,
            '-l',  # List the contents of the backup
            backup_file
        ]

        print("Listing contents of the backup file:")
        subprocess.run(list_command, check=True)

        # Prepare the restore command for the specified table
        command = [
            pg_restore_path,
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', database_name,
            '-t', f'{schema_name}."{table_name}"',  # Specify the table to restore
            '--data-only',  # Restore data only
            '--disable-triggers',  # Disable triggers during restore
            '-v',  # Verbose output
            backup_file
        ]

        # Set up the environment variable for the password
        env = os.environ.copy()
        env['PGPASSWORD'] = password

        # Run the restore command
        subprocess.run(command, env=env, check=True)
        print(f'Table {schema_name}.{table_name} restored successfully from {backup_file}')

        # Verify if the table exists after restore
        verify_table_existence(database_name, user, password, host, port, schema_name, table_name)

    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')


def verify_table_existence(database_name, user, password, host, port, schema_name, table_name):
    try:
        import psycopg2

        # Connect to the database
        conn = psycopg2.connect(
            host=host,
            database=database_name,
            user=user,
            password=password,
            port=port
        )
        cursor = conn.cursor()

        # Check if the table exists
        query = f"""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables 
                WHERE table_schema = '{schema_name}' 
                AND table_name = '{table_name}'
            );
        """
        cursor.execute(query)
        exists = cursor.fetchone()[0]

        if exists:
            print(f'Table {schema_name}.{table_name} exists in the database.')
        else:
            print(f'Table {schema_name}.{table_name} does not exist in the database.')

        # Close the cursor and connection
        cursor.close()
        conn.close()

    except Exception as e:
        print(f'Error checking table existence: {e}')


# Usage example
if __name__ == '__main__':
    DB_NAME = 'IEB1'
    DB_USER = 'postgres'
    DB_PASSWORD = 'root'
    DB_HOST = 'localhost'
    DB_PORT = '5432'
    DB_SCHEMA = 'public'  # Specify the schema
    DB_TABLE = "MC_machinelist"
    BACKUP_FILE = r"C:/Users/1037117/Desktop/IEB Machine Shop/machinelist.backup"
    PG_RESTORE_PATH = r"C:\Program Files\PostgreSQL\16\bin\pg_restore.exe"

    restore_table(PG_RESTORE_PATH, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SCHEMA, DB_TABLE, BACKUP_FILE)
