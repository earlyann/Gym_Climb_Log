import streamlit as st
from datetime import datetime
from db_singleton import get_db, create_tables_if_not_exist, close_db

# Function to initialize session state variables
def initialize_session_state():
    st.session_state.setdefault('username', None)
    st.session_state.setdefault('gym_name', '')
    st.session_state.setdefault('session_page', 'choose_gym')
    st.session_state.setdefault('session_id', None)
    st.session_state.setdefault('grade', '5.9')
    st.session_state.setdefault('climb_name', '')
    st.session_state.setdefault('grade_judgment', 'On')
    st.session_state.setdefault('num_attempts', 1)
    st.session_state.setdefault('star_rating', 0) 
    st.session_state.setdefault('notes', '')
    st.session_state.setdefault('sent', False)
    st.session_state.setdefault('start_time', datetime.now())
    st.session_state.setdefault('end_session', False)
     # Initialize star_rating

# Display the app here
def app(conn, c, username=None):
    initialize_session_state()
    custom_css()
    if username:
        st.session_state['username'] = username
    elif 'username' in st.session_state and st.session_state['username']:
        username = st.session_state['username']
    else:
        st.error("Username not found. Please log in again.")
        return
    
    if st.session_state['session_page'] == 'choose_gym':
        choose_gym(conn, c)
    elif st.session_state['session_page'] == 'enter_climbs':
        enter_climbs(conn, c)
    elif st.session_state['session_page'] == 'summary':
        session_summary(conn, c)

def choose_gym(conn, c):
    username = st.session_state['username']
    gym_options = ['VE Minneapolis', 'VE Bloomington', 'VE St.Paul', 'VE TCB', 'MBP']
    st.session_state['gym_name'] = st.selectbox("Choose a Gym", gym_options, index=0)
    
    if st.session_state['session_id'] is None:
        start_time = st.session_state['start_time']
        gym_name = st.session_state['gym_name']
        c.execute("INSERT INTO sessions (username, start_time, gym_name) VALUES (%s, %s, %s) RETURNING session_id",
                  (username, start_time, gym_name))
        conn.commit()
        result = c.fetchone()
        if result is not None:
            st.session_state['session_id'] = result[0]
        
    if st.button("Start Session"):
        st.session_state['session_page'] = 'enter_climbs'
        st.rerun()
        close_db()

def enter_climbs(conn, c):
    # Check if 'start_time' is initialized in session_state
    if 'start_time' not in st.session_state:
        st.error("Session start time not initialized. Please start a new session.")
        return
    username = st.session_state['username']
    if st.session_state.gym_name in ['VE Minneapolis', 'VE Bloomington', 'VE St.Paul']:
        grade_options = ['5.6', '5.7', '5.8', '5.9', '5.10-', '5.10+', '5.11-', '5.11+', '5.12-', '5.12+', 'VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
    elif st.session_state.gym_name == 'VE TCB':
        grade_options = ['VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
    elif st.session_state.gym_name == 'MBP':
        grade_options = ['Yellow', 'Red', 'Green', 'Purple', 'Orange', 'Black', 'Blue', 'Pink', 'White']

    if st.session_state.grade not in grade_options:
        st.session_state.grade = grade_options[0]

    uploaded_file = st.file_uploader("Upload a photo of your climb (Optional)", type=["jpg", "png", "jpeg"])
    file_bytes = uploaded_file.read() if uploaded_file else None
    st.session_state.climb_name = st.text_input("Climb name", value=st.session_state.climb_name)
    st.session_state.grade = st.selectbox("Grade", grade_options, index=grade_options.index(st.session_state.grade))
    st.session_state.grade_judgment = st.selectbox("Grade Judgment", ["Soft", "On", "Hard"], index=["Soft", "On", "Hard"].index(st.session_state.grade_judgment))
    st.session_state.num_attempts = st.number_input("Number of Attempts", min_value=1, max_value=100, step=1, value=st.session_state.num_attempts)
    st.session_state.star_rating = st.slider("Star Rating", min_value=0, max_value=5, step=1, value=st.session_state.star_rating)
    st.session_state.notes = st.text_input("Notes", value=st.session_state.notes)
    # st.session_state.star_rating = st.number_input("Star Rating", min_value=0, max_value=5, step=1, value=st.session_state.star_rating)
    climb_date = st.session_state.start_time.date()

    st.session_state.sent = st.checkbox("Sent", value=st.session_state.sent)

    # Determine the type based on the grade
    climb_type = 'Sport' if st.session_state.grade.startswith('5') else 'Boulder'

    if st.button("Submit", key='submit_button'):
        try:
            # Execute the SQL query
            c.execute("INSERT INTO climbs (session_id, photo, climb_date, climb_name, gym_name, grade, grade_judgment, num_attempts, sent, notes, star_rating, type) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (st.session_state.session_id, file_bytes, climb_date, st.session_state.climb_name, st.session_state.gym_name, st.session_state.grade, st.session_state.grade_judgment, st.session_state.num_attempts, st.session_state.sent, st.session_state.notes, st.session_state.star_rating, climb_type))
            conn.commit()

            # Reset session state variables
            st.session_state.climb_name = ""
            st.session_state.grade = grade_options[0]
            st.session_state.grade_judgment = "On"
            st.session_state.num_attempts = 1
            st.session_state.notes = ""
            st.session_state.sent = False
            st.session_state.star_rating = 0
            st.rerun()
        except Exception as e:
            # Debugging Step 2: Print exception details
            st.error(f"An error occurred: {e}")


    st.session_state.end_session = st.checkbox("End Session", value=st.session_state.end_session)
    if st.session_state.end_session:
        end_time = datetime.now()
        start_time = st.session_state.start_time
        duration = (end_time - start_time).seconds
        c.execute("UPDATE sessions SET end_time = %s, duration = %s WHERE session_id = %s", (end_time, duration, st.session_state.session_id))
        conn.commit()
        st.session_state['session_page'] = 'summary'
        st.session_state.end_session = False
        st.rerun()
        close_db()

def session_summary(conn, c):
    username = st.session_state['username']
    st.header("Session Summary")

    # Create columns for better layout
    col1, col2 = st.columns(2)

    # Query and display the total number of climbs
    c.execute("SELECT COUNT(*) FROM climbs WHERE session_id = %s", (st.session_state.session_id,))
    count_of_climbs = c.fetchone()[0]
    col1.markdown(f"**Total Climbs:** {count_of_climbs}")

    # Query and display the most frequent grade
    c.execute("SELECT grade, COUNT(grade) FROM climbs WHERE session_id = %s GROUP BY grade ORDER BY COUNT(grade) DESC LIMIT 1", (st.session_state.session_id,))
    most_frequent_grade = c.fetchone()
    if most_frequent_grade:
        col1.markdown(f"**Most Frequent Grade:** {most_frequent_grade[0]} (Count: {most_frequent_grade[1]})")
    else:
        col1.markdown("**Most Frequent Grade:** N/A")
    
    # Query and display the average number of attempts
    c.execute("SELECT AVG(num_attempts) FROM climbs WHERE session_id = %s", (st.session_state.session_id,))
    avg_attempts = c.fetchone()[0]
    if avg_attempts:
        col1.markdown(f"**Average Attempts:** {round(avg_attempts, 2)}")
    else:
        col1.markdown("**Average Attempts:** N/A")

    # Query and display the session length
    c.execute("SELECT start_time, end_time FROM sessions WHERE session_id = %s", (st.session_state.session_id,))
    times = c.fetchone()
    if times and times[0] and times[1]:
        start_time = times[0]
        end_time = times[1]
        duration = (end_time - start_time).seconds
        col1.markdown(f"**Session Length:** {duration//60} minutes {duration%60} seconds")
    else:
        col1.markdown("**Session Length:** N/A")

    # Query and display the list of climbs with star ratings
    c.execute("SELECT climb_name, grade, grade_judgment, star_rating FROM climbs WHERE session_id = %s", (st.session_state.session_id,))
    climbs = c.fetchall()
    st.subheader("List of Climbs")
    for climb in climbs:
        st.markdown(f"- **Climb Name:** {climb[0]}, **Grade:** {climb[1]}, **Judgment:** {climb[2]}, **Star Rating:** {climb[3]}")
    # Button to go back to the start
    if st.button("Go Back to Start", key='go_back_button'):
        st.session_state['session_id'] = None
        st.session_state['session_page'] = 'choose_gym'
        st.rerun()
        close_db()

def custom_css():
    st.markdown(
        """
        <style>
            /* Change the slider line thickness and color */
            div[data-baseweb="slider"] > div > div {
                height: 8px !important;
                background-color: yellow !important;
            }
            /* Change the slider thumb size and color */
            div[role="slider"] {
                width: 20px !important;
                height: 20px !important;
                background-color: yellow !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
