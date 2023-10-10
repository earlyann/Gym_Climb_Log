import streamlit as st
import sqlite3
from datetime import datetime, date
import uuid  # for generating unique identifiers
import base64

def set_background_image(image_path, image_extension):
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode()
    
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: url(data:image/{image_extension};base64,{base64_image});
            background-size: cover;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
# Set the background image
set_background_image("background.jpg", "jpg")

# Initialize session state for form inputs
if 'climb_name' not in st.session_state:
    st.session_state.climb_name = ""
if 'grade' not in st.session_state:
    st.session_state.grade = '5.6'  # Default value, you can change this
if 'grade_judgment' not in st.session_state:
    st.session_state.grade_judgment = 'Soft'  # Default value
if 'num_attempts' not in st.session_state:
    st.session_state.num_attempts = 1  # Default value
if 'notes' not in st.session_state:
    st.session_state.notes = ""  # Default value

# Initialize a new session state variable for form submission
if 'form_submitted' not in st.session_state:
    st.session_state.form_submitted = False

# Initialize a new session state variable for hiding the flash message
if 'hide_flash_message' not in st.session_state:
    st.session_state.hide_flash_message = False

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

if 'show_flash_message' not in st.session_state:
    st.session_state.show_flash_message = False

# Streamlit UI
if st.session_state.page == 'start':
    st.title("Climb Tracker")
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
    st.title(f"Climb Tracker - {st.session_state.gym_name} Session")
    if st.session_state.gym_name in ['VE Minneapolis', 'VE Bloomington', 'VE St.Paul']:
        grade_options = ['5.6', '5.7', '5.8', '5.9', '5.10-', '5.10+', '5.11-', '5.11+', '5.12-', '5.12+', 'VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
    elif st.session_state.gym_name == 'VE TCB':
        grade_options = ['VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
    elif st.session_state.gym_name == 'MBP':
        grade_options = ['Yellow', 'Red', 'Green', 'Purple', 'Orange', 'Black', 'Blue', 'Pink', 'White']

    # Reset st.session_state.grade if it's not in grade_options
    if st.session_state.grade not in grade_options:
        st.session_state.grade = grade_options[0]

    # Use session state variables for form inputs
    uploaded_file = st.file_uploader("Upload a photo of your climb (Optional)", type=["jpg", "png", "jpeg"])
    file_bytes = uploaded_file.read() if uploaded_file else None
    st.session_state.climb_name = st.text_input("Climb name", value=st.session_state.climb_name)
    st.session_state.grade = st.selectbox("Grade", grade_options, index=grade_options.index(st.session_state.grade))
    st.session_state.grade_judgment = st.selectbox("Grade Judgment", ["Soft", "On", "Hard"], index=["Soft", "On", "Hard"].index(st.session_state.grade_judgment))
    st.session_state.num_attempts = st.number_input("Number of Attempts", min_value=1, max_value=100, step=1, value=st.session_state.num_attempts)
    st.session_state.notes = st.text_input("Notes", value=st.session_state.notes)
    climb_date = st.session_state.start_time.date()  # Automatically capture the session start date

    # Initialize 'sent' in session_state if not already present
    if 'sent' not in st.session_state:
        st.session_state.sent = False

    # Use only one st.checkbox for "Sent (Completed)"
    st.session_state.sent = st.checkbox("Sent (Completed)", value=st.session_state.sent)


    if not st.session_state.climb_name:
        st.session_state.climb_name = str(uuid.uuid4())  # Generate a unique identifier

    # Show flash message if needed
    if st.session_state.show_flash_message and not st.session_state.hide_flash_message:
        elapsed_time = datetime.now() - st.session_state.flash_message_time
        if elapsed_time.total_seconds() < 3:  # Show for 3 seconds
            st.success("Climb added successfully!")
        else:
            st.session_state.show_flash_message = False  # Reset for the next run
            st.session_state.hide_flash_message = True  # Hide the flash message

    

    if st.button("Submit"):
        try:
            c.execute("INSERT INTO climbs (session_id, photo, climb_date, climb_name, gym_name, grade, grade_judgment, num_attempts, sent, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (st.session_state.session_id, file_bytes, climb_date, st.session_state.climb_name, st.session_state.gym_name, st.session_state.grade, st.session_state.grade_judgment, st.session_state.num_attempts, st.session_state.sent, st.session_state.notes))
            conn.commit()
            
            # Only update the flash message time if a new climb is successfully added
            if not st.session_state.show_flash_message:
                st.session_state.flash_message_time = datetime.now()
            
            # Show the flash message
            st.session_state.show_flash_message = True
            
            # Reset the form
            st.session_state.climb_name = ""
            st.session_state.grade = grade_options[0]
            st.session_state.grade_judgment = "Soft"
            st.session_state.num_attempts = 1
            st.session_state.notes = ""
            st.session_state.sent = False  # Reset the 'Sent' checkbox
            st.session_state.form_submitted = True  # Indicate that the form has been submitted
            st.session_state.hide_flash_message = False  # Reset the flag to show the flash message again

            # Rerun the app to hide the flash message after 3 seconds
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
