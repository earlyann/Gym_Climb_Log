import hmac
import streamlit as st
from datetime import datetime
import base64
import yaml
from yaml.loader import SafeLoader
import session
from db_singleton import get_db, create_tables_if_not_exist, close_db

# Function to check password
def check_password():
    def login_form():
        with st.form("Credentials"):
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered)

    def password_entered():
        entered_password = st.session_state["password"]
        stored_password = st.secrets["passwords"].get(st.session_state["username"], "")
        
        # Use HMAC to verify the password
        if hmac.compare_digest(entered_password, stored_password):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False

# Stop if password is incorrect
if not check_password():
    st.stop()

# Get the database instance and cursor
db_instance = get_db()
conn, c = db_instance['conn'], db_instance['cursor']

# Create tables if they don't exist
create_tables_if_not_exist(c, conn)

# Function to initialize session state variables
def initialize_session_state():
    st.session_state.setdefault('page', 'Session')
    st.session_state.setdefault('climb_name', '')
    st.session_state.setdefault('grade', '5.6')
    st.session_state.setdefault('grade_judgment', 'On')
    st.session_state.setdefault('num_attempts', 1)
    st.session_state.setdefault('notes', '')
    st.session_state.setdefault('form_submitted', False)

# Initialize session state
initialize_session_state()

# Sidebar for Logout and Toggle between Start Session and Analytics
with st.sidebar:
    page_options = ['Session', 'Analytics']
    st.session_state['page'] = st.radio("Choose Page", page_options, index=page_options.index(st.session_state.get('page', 'Session')))

# Main Streamlit app starts here
if st.session_state['page'] == 'Session':
    username = st.session_state.get("username", None)  # Retrieve the username from session state
    if username:
        session.app(conn, c, username)  # Pass the username to the app function
    else:
        st.error("Username not found. Please log in again.")
elif st.session_state['page'] == 'Analytics':
    st.write("Analytics will be displayed here.")

# Function to set background image
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
