import streamlit as st
import sqlite3
from datetime import datetime, date
import uuid  # for generating unique identifiers

# Initialize SQLite database
conn = sqlite3.connect("climbing_data.db")
c = conn.cursor()

# Create tables if they don't exist
c.execute('''CREATE TABLE IF NOT EXISTS sessions
             (session_id INTEGER PRIMARY KEY AUTOINCREMENT,
             start_time DATETIME,
             end_time DATETIME,
             duration INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS climbs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             session_id INTEGER,
             photo BLOB,
             climb_date DATE,
             climb_name TEXT UNIQUE,
             gym_name TEXT,
             grade TEXT,
             grade_judgment TEXT,
             num_attempts INTEGER,
             sent BOOLEAN,
             notes TEXT,
             FOREIGN KEY(session_id) REFERENCES sessions(session_id))''')
conn.commit()

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'start'
    st.session_state.gym_name = None
    st.session_state.end_session = False  # Initialize 'end_session' state

# Streamlit UI
if st.session_state.page == 'start':
    st.title("Rock Climbing Tracker")
    gym_options = ['VE Minneapolis', 'VE Bloomington', 'VE St.Paul', 'VE TCB', 'MBP']
    st.session_state.gym_name = st.selectbox("Gym Name", gym_options)

    if st.button("Start Session"):
        start_time = datetime.now()
        c.execute("INSERT INTO sessions (start_time) VALUES (?)", (start_time,))
        conn.commit()
        st.session_state.page = 'enter_climbs'
        st.session_state.session_id = c.lastrowid
        st.session_state.start_time = start_time
        st.success(f"Session started at {start_time}")
        st.experimental_rerun()

elif st.session_state.page == 'enter_climbs':
    st.title(f"Rock Climbing Tracker - {st.session_state.gym_name} Session")
    if st.session_state.gym_name in ['VE Minneapolis', 'VE Bloomington', 'VE St.Paul']:
        grade_options = ['5.6', '5.7', '5.8', '5.9', '5.10-', '5.10+', '5.11-', '5.11+', '5.12-', '5.12+', 'VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
    elif st.session_state.gym_name == 'VE TCB':
        grade_options = ['VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
    elif st.session_state.gym_name == 'MBP':
        grade_options = ['Yellow', 'Red', 'Green', 'Purple', 'Orange', 'Black', 'Blue', 'Pink', 'White']

    uploaded_file = st.file_uploader("Upload a photo of your climb (Optional)", type=["jpg", "png", "jpeg"])
    file_bytes = uploaded_file.read() if uploaded_file else None
    climb_name = st.text_input("Climb name")
    grade = st.selectbox("Grade", grade_options)
    grade_judgment = st.selectbox("Grade Judgment", ["Soft", "On", "Hard"])
    num_attempts = st.number_input("Number of Attempts", min_value=1, max_value=100, step=1)
    notes = st.text_input("Notes")
    climb_date = st.session_state.start_time.date()  # Automatically capture the session start date

    # Initialize 'sent' in session_state if not already present
    if 'sent' not in st.session_state:
        st.session_state.sent = False

    # Use only one st.checkbox for "Sent (Completed)"
    st.session_state.sent = st.checkbox("Sent (Completed)", value=st.session_state.sent)


    if not climb_name:
        climb_name = str(uuid.uuid4())  # Generate a unique identifier

    if st.button("Submit"):
        try:
            c.execute("INSERT INTO climbs (session_id, photo, climb_date, climb_name, gym_name, grade, grade_judgment, num_attempts, sent, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                      (st.session_state.session_id, file_bytes, climb_date, climb_name, st.session_state.gym_name, grade, grade_judgment, num_attempts, st.session_state.sent, notes))
            conn.commit()
            st.success("Climb added successfully!")
            
            # Reset the relevant session state variables
            st.session_state.sent = False  # Reset the 'Sent' checkbox
            
            # Rerun the app to clear all widgets
            st.experimental_rerun()
        except Exception as e:
            st.error(f"An error occurred: {e}")

    # Use session_state for "End Session" checkbox
    st.session_state.end_session = st.checkbox("End Session", value=st.session_state.end_session)
    if st.session_state.end_session:
        end_time = datetime.now()
        start_time = st.session_state.start_time  # Retrieve start_time from session_state
        duration = (end_time - start_time).seconds
        c.execute("UPDATE sessions SET end_time = ?, duration = ? WHERE session_id = ?", (end_time, duration, st.session_state.session_id))
        conn.commit()
        st.session_state.page = 'summary'
        st.success(f"Session ended at {end_time}. Duration: {duration} seconds.")
        st.session_state.end_session = False  # Reset the 'End Session' checkbox
        st.experimental_rerun()


elif st.session_state.page == 'summary':
    st.header("Session Summary")

    # Count of climbs
    c.execute("SELECT COUNT(*) FROM climbs WHERE session_id = ?", (st.session_state.session_id,))
    count_of_climbs = c.fetchone()[0]
    st.write(f"Total Climbs: {count_of_climbs}")

    # Most frequent grade (mode)
    c.execute("SELECT grade, COUNT(grade) FROM climbs WHERE session_id = ? GROUP BY grade ORDER BY COUNT(grade) DESC LIMIT 1", (st.session_state.session_id,))
    most_frequent_grade = c.fetchone()
    if most_frequent_grade:
        st.write(f"Most Frequent Grade: {most_frequent_grade[0]} (Count: {most_frequent_grade[1]})")
    else:
        st.write("Most Frequent Grade: N/A")

    # Length of session
    c.execute("SELECT start_time, end_time FROM sessions WHERE session_id = ?", (st.session_state.session_id,))
    times = c.fetchone()
    if times and times[0] and times[1]:
        start_time = datetime.fromisoformat(times[0])
        end_time = datetime.fromisoformat(times[1])
        duration = (end_time - start_time).seconds
        st.write(f"Session Length: {duration} seconds")
    else:
        st.write("Session Length: N/A")

    # Display the summary here
    c.execute("SELECT climb_name, grade, grade_judgment FROM climbs WHERE session_id = ?", (st.session_state.session_id,))
    climbs = c.fetchall()
    for climb in climbs:
        st.write(climb)

    if st.button("Go Back to Start"):
        st.session_state.page = 'start'
        st.experimental_rerun()

conn.close()
