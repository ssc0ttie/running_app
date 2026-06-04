import streamlit as st
from supabase import create_client, Client


# Initialize connection to Supabase
@st.cache_resource
def init_connection():
    try:
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None



