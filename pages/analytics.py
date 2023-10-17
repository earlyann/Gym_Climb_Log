import streamlit as st

def app():
    st.title("Analytics Dashboard")
    
    # Embed Tableau Dashboard
    tableau_dashboard_link = "YOUR_TABLEAU_PUBLIC_URL_HERE"
    st.components.v1.html(f'<iframe src="{tableau_dashboard_link}" width="800" height="600"></iframe>', width=800, height=600)
