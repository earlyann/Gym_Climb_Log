import streamlit as st
import sqlite3
from datetime import date

# Initialize SQLite database
conn = sqlite3.connect("climbing_data.db")
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS climbs
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             photo BLOB,
             climb_date DATE,
             climb_name TEXT,
             gym_name TEXT,
             grade TEXT,
             grade_judgment TEXT,
             num_sessions INTEGER,
             notes TEXT)''')
conn.commit()

# Function to add a new climb to the database
def add_climb(photo, climb_date, climb_name, gym_name, grade, grade_judgment, num_sessions, notes):
    c.execute("INSERT INTO climbs (photo, climb_date, climb_name, gym_name, grade, grade_judgment, num_sessions, notes) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (photo, climb_date, climb_name, gym_name, grade, grade_judgment, num_sessions, notes))
    conn.commit()   

# Streamlit UI
st.title("Rock Climbing Tracker")

uploaded_file = st.file_uploader("Upload a photo of your climb (Optional)", type=["jpg", "png", "jpeg"])
file_bytes = uploaded_file.read() if uploaded_file else None
climb_date = st.date_input("Climb Date", min_value=date.today())
gym_options = ['VE Minneapolis', 'VE Bloomington', 'VE St.Paul', 'VE TCB', 'MBP']
gym_name = st.selectbox("Gym Name", gym_options)

if gym_name in ['VE Minneapolis', 'VE Bloomington', 'VE St.Paul']:
    grade_options = ['5.6', '5.7', '5.8', '5.9', '5.10-', '5.10+', '5.11-', '5.11+', '5.12-', '5.12+', 'VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
elif gym_name == 'VE TCB':
    grade_options = ['VB', 'V1-2', 'V2-3', 'V4-5', 'V5-6', 'V7-8', 'V9-10', 'V11']
elif gym_name == 'MBP':
    grade_options = ['Yellow', 'Red', 'Green', 'Purple', 'Orange', 'Black', 'Blue', 'Pink', 'White']

climb_name = st.text_input("Climb name")

grade = st.selectbox("Grade", grade_options)
grade_judgment = st.selectbox("Grade Judgment", ["Soft", "On", "Hard"])
num_sessions = st.number_input("Number of Sessions to Send", min_value=1, max_value=100, step=1)
notes = st.text_input("Notes")
  

if st.button("Submit"):
    try:
        add_climb(file_bytes, climb_date, climb_name, gym_name, grade, grade_judgment, num_sessions, notes)  # Include climb_date
        st.success("Climb added successfully!")
    except Exception as e:
        st.error(f"An error occurred: {e}")

# Optional: Display existing climbs (for debugging)
if st.checkbox("Show existing climbs"):
    c.execute("SELECT * FROM climbs")
    climbs = c.fetchall()
    for climb in climbs:
        st.write(climb)

conn.close()
