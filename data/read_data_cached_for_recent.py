import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import datetime
import numpy as np


# @st.cache_resource
def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(
        st.secrets["google_sheets"], scope
    )
    client = gspread.authorize(creds)
    return client


### -- CACHED: Load all runner data with TTL -- ###
# @st.cache_data(ttl=120)  # refresh every 5 minutes
def get_runner_data():
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

    #######DATA CLEANUP######

    # ---- Load week lookup ---- #
    week_lookup_data = sheet.get_worksheet_by_id(336401596).get_all_records()
    df_week = pd.DataFrame(week_lookup_data)[
        [
            "Dates",
            "WEEK_Streamlit",
            "Activity_Others",
            "Activity_Chona",
            "Event",
            "Activity_Scott",
        ]
    ]
    df_week.rename(
        columns={
            "Dates": "Date",
            "WEEK_Streamlit": "Week",
            "Activity_Others": "Menu_Other",
            "Activity_Chona": "Menu_Chona",
            "Event": "Event",
            "Activity_Scott": "Menu",
        },
        inplace=True,
    )
    df_week["Date"] = pd.to_datetime(df_week["Date"])

    # ---- Load main streamlit_new_source sheet---- #
    #new_logs_data = sheet.get_worksheet_by_id(1611308583).get_all_records()
    

    ##SUPABASE##
    new_logs_data = get_activities()
    df_new = pd.DataFrame(new_logs_data)

    df = df_new

    # # ------------clean lookup dates and merge -----------------#
    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"], errors="coerce")
    df_week["Date"] = pd.to_datetime(df_week["Date"])
    df = df.merge(df_week, left_on="Date_of_Activity", right_on="Date", how="left")

    # # CALCULATE MOVING TIME

    df["Moving_Time"] = pd.to_timedelta(df["Duration_Other"])

    return df


def get_worksheet_object():
    """Return the Google Sheets worksheet object for writing"""
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    worksheet = sheet.get_worksheet_by_id(1611308583)  # Your worksheet ID
    return worksheet



######### -- SUPA BASE ----- #################
# --- Database functions ---
import supabase_client
# @st.cache_data(ttl=600) 
def get_activities():
    
    try:
        supabase=supabase_client.init_connection()
        # response = supabase.table("activities").select("*").execute()
        # st.success(f"✅ Successfully extracted {len(response.data)} activities from Supabase")
        
        all_data = []
        page_size = 1000
        start = 0
        
        while True:
            response = supabase.table("activities")\
                .select("*")\
                .range(start, start + page_size - 1)\
                .execute()
            
            if not response.data:
                break
                
            all_data.extend(response.data)
            start += page_size
            
            # # Optional: Add a small delay to avoid rate limiting
            # time.sleep(0.1)
    
        return all_data
    
    except Exception as e:
        st.error(f"Error fetching activities: {e}")
        return []
        
def get_activities_hist():
    
    try:
        supabase=supabase_client.init_connection()
        # response = supabase.table("zones").select("*").execute()
        # st.success(f"✅ Successfully extracted {len(response.data)} act hist from Supabase")
        
        all_data = []
        page_size = 1000
        start = 0
        
        while True:
            response = supabase.table("activity_history")\
                .select("*")\
                .range(start, start + page_size - 1)\
                .execute()
            
            if not response.data:
                break
                
            all_data.extend(response.data)
            start += page_size
            
            # # Optional: Add a small delay to avoid rate limiting
            # time.sleep(0.1)
    
        return all_data
    
    except Exception as e:
        st.error(f"Error fetching activity history: {e}")
        return []
# --- Database functions ---
def get_zones():
    
    try:
        supabase=supabase_client.init_connection()
        # response = supabase.table("zones").select("*").execute()
        # st.success(f"✅ Successfully extracted {len(response.data)} zones from Supabase")
        
        all_data = []
        page_size = 1000
        start = 0
        
        while True:
            response = supabase.table("zones")\
                .select("*")\
                .range(start, start + page_size - 1)\
                .execute()
            
            if not response.data:
                break
                
            all_data.extend(response.data)
            start += page_size
            
            # # Optional: Add a small delay to avoid rate limiting
            # time.sleep(0.1)
    
        return all_data
    
    except Exception as e:
        st.error(f"Error fetching activities: {e}")
        return []