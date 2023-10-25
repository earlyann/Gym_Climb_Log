import psycopg2
import streamlit as st
import atexit  

_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        # Retrieve database connection information from Streamlit secrets
        conn_info = st.secrets["postgres"]

        conn = psycopg2.connect(
            host=conn_info["host"],
            port=conn_info["port"],
            dbname=conn_info["dbname"],
            user=conn_info["user"],
            password=conn_info["password"],
        )
        c = conn.cursor()
        _db_instance = {'conn': conn, 'cursor': c}

        # Register close_db to be called when the application terminates
        atexit.register(close_db)
    return _db_instance

def create_tables_if_not_exist(cursor, connection):
    try:
        # Create new tables
        cursor.execute('''CREATE TABLE IF NOT EXISTS sessions
                        (session_id SERIAL PRIMARY KEY,
                        username TEXT,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        gym_name TEXT,
                        duration INTEGER)''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS climbs
                        (id SERIAL PRIMARY KEY,
                        session_id INTEGER,
                        photo BYTEA,
                        climb_date DATE,
                        climb_name TEXT,
                        gym_name TEXT,
                        grade TEXT,
                        grade_judgment TEXT,
                        num_attempts INTEGER,
                        sent BOOLEAN,
                        notes TEXT,
                        star_rating INT,
                        type TEXT,  -- New column
                        FOREIGN KEY(session_id) REFERENCES sessions(session_id))''')

        connection.commit()
    except Exception as e:
            # If an error occurs, rollback the transaction
        connection.rollback()
        print(f"An error occurred: {e}")

def drop_tables(cursor, connection):
    try:
        cursor.execute("DROP TABLE IF EXISTS climbs CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS sessions CASCADE;")
        connection.commit()
        print("Tables 'climbs' and 'sessions' dropped successfully.")
    except Exception as e:
        # If an error occurs, rollback the transaction
        connection.rollback()
        print(f"An error occurred while dropping tables: {e}")
            
def close_db():
    global _db_instance
    if _db_instance is not None:
        _db_instance['cursor'].close()
        _db_instance['conn'].close()
        _db_instance = None

