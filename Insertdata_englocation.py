import pandas as pd
import psycopg2
from datetime import datetime
import pytz

# Define the timezone
timezone = pytz.timezone('Asia/Kolkata')  # Change to your desired timezone
now = datetime.now(timezone)    # Get the current time in the specified timezone
timestamp = now.strftime('%Y-%m-%d %H:%M:%S%z') # Format the datetime object as a string
current_timestamp = timestamp[:-2] + ':' + timestamp[-2:]# Adjust the timezone offset to match the required format # +05:30 formatting

# Database connection details
DB_NAME = 'IEB1'
DB_USER = 'postgres'
DB_PASSWORD = 'root'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_SCHEMA = 'public'
DB_TABLE = 'ATP_englocation'
file_path = 'C:/Users/AD1-DT-280/Desktop/DB/ESN_IEB_PPC2STORE.xlsx'

# Database connection
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)

cursor = conn.cursor()

df = pd.read_excel(file_path)

# Define the SQL query
insert_query = """
INSERT INTO public."ATP_englocation" (
    esn, bom, insp_type, for_conversion, cur_loc, 
    st01_status, st01_date, st02_status, st02_date, st05_status, st05_date, st10_status, st10_date,
    st12_status, st12_date, st14_status, st14_date, st20_status, st20_date, st22_status, st22_date,
    st24_status, st24_date, st30_status, st30_date, st32_status, st32_date, st35_status, st35_date,
    st40_status, st40_date, st42_status, st42_date, st50_status, st50_date
) VALUES (
    %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s, %s, %s, 
    %s, %s, %s, %s, %s, %s
)
"""

# Insert data into the table
for index, row in df.iterrows():
    try:
        if row['import done'] == 0:
            data = (
                row['esn'], row['bom'],  None, None,  30,
                True, current_timestamp, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None, None, None,
                None, None, None, None, None, None
            )
            cursor.execute(insert_query, data)
            df.at[index, 'import done'] = 1  # Update the 'Import Done' column to 1
            print(row['esn'], "import completed")
        else:
            print(row['esn'], "import not required, as available in database")
    except KeyError as e:
        print(f"Error processing row {index}: Missing column {e}")

conn.commit()       # Commit the transaction
cursor.close()      # Close the cursor and connection
conn.close()

# Save the updated DataFrame back to the Excel file
df.to_excel(file_path, index=False)

print("Data inserted successfully and Excel file updated.")