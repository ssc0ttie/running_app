import streamlit as st
from supabase import create_client, Client


# Initialize connection to Supabase
@st.cache_resource
def init_connection():
    try:
        supabase_url  = st.secrets["supabase"]["SUPABASE_URL"]
        supabase_key  = st.secrets["supabase"]["SUPABASE_KEY"]
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None



