import pandas as pd
import os
import psycopg2

# Path to your Excel file
excel_file_path = 'Production_Report_2.xlsx'  # Replace with your actual file path

# Database connection details
conn = psycopg2.connect(
    host="localhost",  # Adjust this with your host details
    database="IEB1",  # Replace with your actual database name
    user="postgres",  # Replace with your PostgreSQL username
    password="root"  # Replace with your PostgreSQL password
)
cursor = conn.cursor()

# Check file extension
file_extension = os.path.splitext(excel_file_path)[1]

# Read the Excel file into a pandas DataFrame
df = pd.read_excel(excel_file_path, engine='openpyxl')  # Use 'openpyxl' for .xlsx files

# Iterate over each row and insert the data into the PostgreSQL table
try:
    for index, row in df.iterrows():
        if index < 9:
            continue  # Skip the first 10 rows

        machine_name = row['Unnamed: 1']
        cell_name = row['Unnamed: 2']
        shift = row['Unnamed: 3']
        timestamp_str = row['Unnamed: 4']
        partname = row['Unnamed: 5']
        produced_qty = row['Unnamed: 9']
        rejected_qty = row['Unnamed: 12']

        try:
            # Convert to datetime and extract the date
            date_str = pd.to_datetime(timestamp_str,
                                      format='%d/%m/%Y %I:%M:%S %p').date()  # Adjust the format if needed
            timestamp = pd.to_datetime(timestamp_str, format='%d/%m/%Y %I:%M:%S %p')  # Full timestamp

            # Check if timestamp is valid (not NaT)
            if pd.isna(timestamp):
                print(f"Row {index + 1}: Invalid timestamp '{timestamp_str}'. Skipping this row.")
                continue  # Skip this iteration

        except ValueError:
            # If conversion fails, print a message and continue to the next row
            print(f"Row {index + 1}: Date conversion failed for value '{timestamp_str}'. Skipping this row.")
            continue  # Skip this iteration

        # Prepare the SQL query to insert the data
        insert_query = """
            INSERT INTO public."MC_productiondata"(
                machine_name, cell_name, shift, part_name, date, "timestamp", produced_qty, rejected_qty
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Execute the insert query
        cursor.execute(insert_query,
                       (machine_name, cell_name, shift, partname, date_str, timestamp, produced_qty, rejected_qty))

    # Commit the transaction if all rows processed without errors
    conn.commit()
    print("Data inserted successfully.")

except Exception as e:
    # Roll back the transaction on error
    conn.rollback()
    print(f"Error occurred: {e}")

finally:
    # Close the cursor and connection
    cursor.close()
    conn.close()
