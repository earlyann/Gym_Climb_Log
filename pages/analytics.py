import streamlit as st
import plotly.express as px
import pandas as pd
from db_singleton import get_db, create_tables_if_not_exist, close_db

st.set_page_config(
    page_title="Climbing Analytics Dashboard",
    page_icon="🧗",
    layout="wide",
)

# Function to fetch session data from the database
def get_session_data(username, cursor):
    cursor.execute("""
        SELECT 
            sessions.session_id,
            CONCAT(sessions.gym_name, ' (', start_time::date, ')') as session_name,
            start_time,
            end_time,
            COUNT(climbs.id) as num_climbs,
            MODE() WITHIN GROUP (ORDER BY climbs.grade) as most_frequent_grade
        FROM sessions
        LEFT JOIN climbs ON sessions.session_id = climbs.session_id
        WHERE username = %s
        GROUP BY sessions.session_id, start_time, end_time
        ORDER BY start_time DESC
    """, (username,))
    return cursor.fetchall()

# Function to show the analytics page
def show_analytics_page():
    # Initialize database connection
    db = get_db()
    conn = db['conn']
    c = db['cursor']

    # Check if 'username' exists and is not None
    if 'username' in st.session_state and st.session_state['username'] is not None:
        username = st.session_state['username']
        st.session_state['username'] = username  # Explicitly set username
 
        # Fetch session data
        session_data = get_session_data(username, c)
        
        # Convert to DataFrame
        df_sessions = pd.DataFrame(session_data, columns=['session_id', 'session_name', 'start_time', 'end_time', 'num_climbs', 'most_frequent_grade'])
        
        # Convert 'start_time' and 'end_time' to datetime and extract the week number
        df_sessions['start_time'] = pd.to_datetime(df_sessions['start_time'])
        df_sessions['end_time'] = pd.to_datetime(df_sessions['end_time'])
        df_sessions['week_num'] = df_sessions['start_time'].dt.strftime('%U')
        
        # Sort the DataFrame by week_num in ascending order
        df_sessions.sort_values(by='week_num', inplace=True)
        
        # Calculate session length in minutes
        df_sessions['session_length'] = (df_sessions['end_time'] - df_sessions['start_time']).dt.total_seconds() / 60
        
        if not df_sessions.empty:
            # Create a high-level Plotly bar chart to show the total session time per week
            fig_weekly_sessions = px.bar(df_sessions, 
                                         x='week_num', 
                                         y='session_length', 
                                         color='session_name', 
                                         title='Total Session Time per Week (Minutes)',
                                         hover_data=['num_climbs', 'most_frequent_grade'])  # Add num_climbs and most_frequent_grade to hover data
            
            # Update x-axis to display only whole integers
            fig_weekly_sessions.update_xaxes(type='category')
            
            st.plotly_chart(fig_weekly_sessions)
