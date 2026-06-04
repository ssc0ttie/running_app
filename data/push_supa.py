# New supabase_push.py
import streamlit as st
from supabase import create_client
import pandas as pd
import numpy as np

@st.cache_resource
def init_supabase():
    try:
        supabase_url  = st.secrets["supabase"]["SUPABASE_URL"]
        supabase_key  = st.secrets["supabase"]["SUPABASE_KEY"]
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        st.error(f"Connection error: {e}")
        return None

# ============================================================
# STEP 1: Get existing UniqueKeys (like get_existing_uniquekeys_from_sheet)
# ============================================================
def get_existing_activity_keys():
    """
    Fetch all existing UniqueKeys from Supabase activities table.
    Returns a set of UniqueKeys for duplicate checking.
    """
    supabase = init_supabase()
    
    try:
        # Select only the UniqueKey column to minimize data transfer
        response = supabase.table("activities")\
            .select("UniqueKey")\
            .execute()
        
        if response.data:
            return {row["UniqueKey"] for row in response.data}
        return set()
        
    except Exception as e:
        st.error(f"Error fetching existing activity keys: {e}")
        return set()

# ============================================================
# STEP 2: Get existing Zone keys (like get_existing_zone_keys_from_sheet)
# ============================================================
def get_existing_zone_keys():
    """
    Fetch all existing Zone_UniqueKeys from Supabase zones table.
    Returns a set of Zone_UniqueKeys for duplicate checking.
    """
    supabase = init_supabase()
    
    try:
        response = supabase.table("zones")\
            .select("Zone_UniqueKey")\
            .execute()
        
        if response.data:
            return {row["Zone_UniqueKey"] for row in response.data}
        return set()
        
    except Exception as e:
        st.error(f"Error fetching existing zone keys: {e}")
        return set()

# ============================================================
# STEP 3: Push activity data (replaces push_strava_data_to_sheet)
# ============================================================
def push_activity_data_to_supabase(df):
    """Push Strava activity data to Supabase."""
    supabase = init_supabase()
    
    try:
        existing_keys = get_existing_activity_keys()
        
        new_rows = []
        for _, row in df.iterrows():
            unique_key = str(row["UniqueKey"])
            
            if unique_key in existing_keys:
                st.warning(f"Skipping duplicate: {unique_key}")
                continue
            
            # Convert row to dict and fix date types
            row_dict = row.to_dict()
            
            # Convert date objects to strings (JSON serializable)
            for key, value in row_dict.items():
                if hasattr(value, 'isoformat'):  # datetime/date objects
                    row_dict[key] = value.isoformat()
                elif pd.isna(value):  # Handle NaN/None
                    row_dict[key] = None
            
            new_rows.append(row_dict)
        
        if not new_rows:
            st.info("No new activities to push")
            return 0, 0
        
        # Bulk insert
        # response = supabase.table("activities").insert(new_rows).execute()
        
        response = supabase.table("activities")\
            .upsert(new_rows, on_conflict="UniqueKey", ignore_duplicates=True)\
            .execute()
        
        success_count = len(response.data) if response.data else 0
        error_count = len(new_rows) - success_count
        
        return success_count, error_count
        
    except Exception as e:
        st.error(f"Error pushing - supa activities: {e}")
        return 0, len(df)
# ============================================================
# STEP 4: Push zone data (replaces push_zone_data_to_sheet)
# ============================================================
def push_zone_data_to_supabase(zones_df, parent_unique_key, activity_row_data):
    """Push zone distribution data to Supabase."""
    supabase = init_supabase()
    
    try:
        existing_keys = get_existing_zone_keys()
        
        new_rows = []
        for _, row in zones_df.iterrows():
            zone_key = f"{parent_unique_key}_{row['Type']}_{row['Zone']}"
            
            if zone_key in existing_keys:
                continue
            
            new_row = {
                "Zone_UniqueKey": str(zone_key),
                "Parent_UniqueKey": str(parent_unique_key),
                "Date_of_Activity": str(activity_row_data["Date"]),  # Convert to string
                "Member Name": str(activity_row_data["Member Name"]),
                "Activity": str(activity_row_data["Activity"]),
                "Avg_HR": int(activity_row_data["Avg_HR"]) if activity_row_data["Avg_HR"] else None,
                "Zone_Type": str(row["Type"]),
                "Zone": str(row["Zone"]),
                "Zone_Name": str(row["Zone Name"]),
                "Min_Value": str(row.get("Min", "")),
                "Max_Value": str(row.get("Max", "")),
                "Time_In_Zone": str(row.get("Time", "")),
                "Percentage": str(row.get("Percentage", ""))
            }
            new_rows.append(new_row)
        
        if not new_rows:
            return 0, 0
        
        # response = supabase.table("zones").insert(new_rows).execute()

        response = supabase.table("zones")\
            .upsert(new_rows, on_conflict="Zone_UniqueKey", ignore_duplicates=True)\
            .execute()
        
        success_count = len(response.data) if response.data else 0
        error_count = len(new_rows) - success_count
        
        return success_count, error_count
        
    except Exception as e:
        st.error(f"Error pushing - supa zones: {e}")
        return 0, len(zones_df) if zones_df is not None else 0
    




def update_activity_in_supabase(unique_key, updated_data):
    """
    Update an existing activity in Supabase based on UniqueKey.
    
    Args:
        unique_key: The UniqueKey of the entry to update
        updated_data: Dictionary containing the updated values
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        supabase = init_supabase()
        
        # First, find the row with matching UniqueKey
        response = supabase.table("activities")\
            .select("*")\
            .eq("UniqueKey", unique_key)\
            .execute()
        
        if not response.data:
            print(f"❌ Entry with UniqueKey {unique_key} not found")
            return False
        
        # Get the record ID (primary key)
        record_id = response.data[0]["id"]
        
        # Prepare update data (only the fields we want to change)
        update_payload = {
            "Activity": updated_data.get("Activity"),
            "RPE (1–10 scale)": updated_data.get("RPE (1–10 scale)"),
            "Shoe": updated_data.get("Shoe"),
            "Remarks": updated_data.get("Remarks"),
            # "updated_at": datetime.now().isoformat()  # optional timestamp
        }
        
        # Remove None values to avoid overwriting with null
        update_payload = {k: v for k, v in update_payload.items() if v is not None}
        
        # Update the record
        update_response = supabase.table("activities")\
            .update(update_payload)\
            .eq("id", record_id)\
            .execute()
        
        if update_response.data:
            st.success(f"✅ Successfully updated activity: {unique_key}")

        else:
            print(f"❌ Update failed for: {unique_key}")
            return False
        
        
    except Exception as e:
        print(f"❌ Error updating activity: {e}")
        return False