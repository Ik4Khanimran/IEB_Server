import psycopg2
from psycopg2 import sql


# Function to duplicate a table
# after that run in pgsdmin, below sqlquerry set
# GRANT ALL PRIVILEGES ON TABLE public."ATP_engresultaudit" TO postgres;
def duplicate_table(conn, schema_name, table_name, new_table_name):
    cursor = conn.cursor()

    try:
        # Check if the original table exists
        cursor.execute(sql.SQL(
            "SELECT EXISTS(SELECT 1 FROM information_schema.tables WHERE table_schema = %s AND table_name = %s)"),
                       (schema_name, table_name,))
        if not cursor.fetchone()[0]:
            raise ValueError(f"Table {schema_name}.{table_name} does not exist.")

        # Create new table as a copy of existing table
        query = sql.SQL("CREATE TABLE {}.{} AS TABLE {}.{} WITH NO DATA;").format(
            sql.Identifier(schema_name), sql.Identifier(new_table_name),
            sql.Identifier(schema_name), sql.Identifier(table_name)
        )
        cursor.execute(query)

        conn.commit()
        print(f"Table {schema_name}.{new_table_name} duplicated successfully.")

    except psycopg2.Error as e:
        conn.rollback()
        print(f"Error: {e}")

    finally:
        cursor.close()


# Database connection parameters
db_params = {
    'host': 'localhost',
    'database': 'IEB',
    'user': 'postgres',
    'password': 'root',
    'port': '5432'
}

# Table details
schema_name = 'public'  # Replace with your schema name
table_name = 'ATP_engresultheader'  # Replace with your existing table name
new_table_name = 'ATP_engresultaudit'  # Replace with the name for the new table

# Connect to PostgreSQL
try:
    conn = psycopg2.connect(**db_params)
    duplicate_table(conn, schema_name, table_name, new_table_name)

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")

finally:
    if conn:
        conn.close()
