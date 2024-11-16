import psycopg2
import csv

# Database connection parameters
db_params = {
    'host': 'localhost',
    'database': 'IEB1',
    'user': 'postgres',
    'password': 'root'
}

# File path to save the backup CSV
backup_file = 'D:/Projects/IEB Assembly/Server/Database_Backup/ATP_englocation_backup.csv'

# Connect to the database
try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    # Query to select all rows from ATP_englocation table in IEB1 schema
    query = "SELECT * FROM ATP_englocation"

    # Execute the query
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Write rows to CSV
    with open(backup_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([desc[0] for desc in cursor.description])  # Write header
        csv_writer.writerows(rows)

    print(f"Backup of ATP_englocation table saved to {backup_file}")

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")

finally:
    if conn is not None:
        cursor.close()
        conn.close()
