import streamlit as st
import psycopg2
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth

def init_session_state():
    if 'name' not in st.session_state:
        st.session_state['name'] = None
    if 'authentication_status' not in st.session_state:
        st.session_state['authentication_status'] = None
    if 'username' not in st.session_state:
        st.session_state['username'] = None

def authenticate():
    with open('.streamlit/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['preauthorized']
    )

    name, authentication_status, username = authenticator.login('Login', 'main')
    return name, authentication_status, username, authenticator  # Return the authenticator object

def sidebar_logout(authentication_status, authenticator):
    with st.sidebar:
        if st.button('Logout', key='logout_button'):
            if authentication_status:
                authenticator.logout('Logout', 'main')
                st.write(f'Welcome *{st.session_state["name"]}*')  # Get name from session state
                st.title('Some content')
            elif authentication_status == False:
                st.error('Username/password is incorrect')
            elif authentication_status == None:
                st.warning('Please enter your username and password')
            st.experimental_rerun()






