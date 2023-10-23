import psycopg2
import streamlit as st
import boto3
import json
from botocore.exceptions import ClientError
import os  # Import the os module

# Moved get_secret function here to avoid circular import
def get_db_secret():
    secret_name = "deploy/gymlog"
    region_name = "us-east-2"

    aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")

    session = boto3.session.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=region_name
    )
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    secret = get_secret_value_response['SecretString']
    # st.write(secret)  # Comment this line out for production
    return json.loads(secret)

_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        conn_info = get_db_secret()  # Use get_db_secret() function here

        conn = psycopg2.connect(
            host=conn_info["host"],
            port=conn_info["port"],
            dbname=conn_info["dbname"],
            user=conn_info["user"],
            password=conn_info["password"],
        )
        c = conn.cursor()
        _db_instance = {'conn': conn, 'cursor': c}
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

