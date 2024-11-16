import pandas as pd
import psycopg2
from datetime import datetime
import pytz

# Define the timezone
timezone = pytz.timezone('Asia/Kolkata')  # Change to your desired timezone
now = datetime.now(timezone)    # Get the current time in the specified timezone
timestamp = now.strftime('%Y-%m-%d %H:%M:%S%z') # Format the datetime object as a string
current_timestamp = timestamp[:-2] + ':' + timestamp[-2:] # Adjust the timezone offset to match the required format # +05:30 formatting

# Database connection details
DB_NAME = 'IEB1'
DB_USER = 'postgres'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_SCHEMA = 'public'
DB_TABLE = 'ATP_bomlist'
file_path = 'C:/Users/AD1-DT-280/Desktop/DB/ATP_bomlist.xlsx'

# Database connection
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

# Read data from the new Excel file
df = pd.read_excel(file_path)

# Define the SQL query for the new table
insert_query = """
INSERT INTO public."ATP_bomlist" (
    srno, bom, description, model, type, series
) VALUES (%s, %s, %s, %s, %s, %s)
"""

# Insert data into the new table
for index, row in df.iterrows():
    try:
        if row['import done'] == 0:
            data = (
                row['srno'], row['bom'], row['description'], row['model'], row['type'], row['series']
            )
            cursor.execute(insert_query, data)
            df.at[index, 'import done'] = 1  # Update the 'Import Done' column to 1
            print(row['bom'], "import completed")
        else:
            print(row['bom'], "import not required, as available in database")
    except KeyError as e:
        print(f"Error processing row {index}: Missing column {e}")

conn.commit()       # Commit the transaction
cursor.close()      # Close the cursor and connection
conn.close()

# Save the updated DataFrame back to the Excel file
df.to_excel(file_path, index=False)

print("Data inserted successfully and Excel file updated.")
