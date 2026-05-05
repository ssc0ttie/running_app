import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from data import read_data_uncached as rd
from data import strava as strav

# data/push_data.py
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os

# Try to import Streamlit, but don't fail if not available
try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

    # Create dummy functions
    def st_error(msg):
        print(f"❌ {msg}")

    def st_warning(msg):
        print(f"⚠️ {msg}")

    def st_info(msg):
        print(f"ℹ️ {msg}")

    def st_success(msg):
        print(f"✅ {msg}")


def get_google_sheets_creds():
    """Get Google Sheets credentials from either st.secrets or environment"""
    if HAS_STREAMLIT:
        try:
            return st.secrets["google_sheets"]
        except:
            pass

    # Fall back to environment variable
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if creds_json:
        return json.loads(creds_json)

    raise Exception("No Google Sheets credentials found")


def get_gsheet_client():
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive",
    ]
    creds_dict = get_google_sheets_creds()
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client


def get_runner_data():
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    worksheet = sheet.get_worksheet_by_id(1611308583)
    sheet = worksheet.get_all_values()
    return sheet


def get_existing_uniquekeys_from_sheet():
    sheet_data = get_runner_data()
    if not sheet_data or len(sheet_data) < 2:
        return set()

    header = sheet_data[0]
    try:
        uniquekey_idx = header.index("UniqueKey")
    except ValueError:
        raise ValueError("UniqueKey column not found in sheet")

    existing_keys = {row[uniquekey_idx] for row in sheet_data[1:]}
    return existing_keys


def push_runner_data(data):
    gsclient = get_gsheet_client()
    sheet = gsclient.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    newsource_worksheet = sheet.get_worksheet_by_id(1611308583)
    newsource_worksheet.append_row(data)


def push_strava_data_to_sheet(strava_df):
    """Push Strava data to Google Sheets"""
    try:
        success_count = 0
        error_count = 0

        existing_keys = get_existing_uniquekeys_from_sheet()

        if HAS_STREAMLIT:
            st.info(f"Found {len(existing_keys)} existing activities in sheet")
        else:
            print(f"ℹ️ Found {len(existing_keys)} existing activities in sheet")

        for index, row in strava_df.iterrows():
            try:
                unique_key = str(row["UniqueKey"])

                if unique_key in existing_keys:
                    if HAS_STREAMLIT:
                        st.warning(f"Skipping duplicate: {unique_key}")
                    else:
                        print(f"⚠️ Skipping duplicate: {unique_key}")
                    continue

                row_data = [
                    unique_key,
                    str(row["TimeStamp"]),
                    str(row["Date_of_Activity"]),
                    str(row.get("Activity", "")),
                    float(row.get("Distance", 0)),
                    str(row.get("Pace", None)),
                    int(row.get("HR (bpm)", 0)) if pd.notna(row.get("HR (bpm)")) else 0,
                    (
                        int(row.get("Cadence (steps/min)", 0))
                        if pd.notna(row.get("Cadence (steps/min)"))
                        else 0
                    ),
                    0,  # rpe
                    None,  # Shoe
                    None,  # Remarks
                    str(row.get("Member Name", "Unknown")),
                    str(row.get("Duration", "00:00:00")),
                    str(row.get("Activity", "")),
                    str(row.get("Map_Polyline", "")),
                    str(row.get("Max_Pace", None)),
                    int(row.get("Max_HR", 0)) if pd.notna(row.get("Max_HR")) else 0,
                    (
                        int(row.get("Elevation_Gained", 0))
                        if pd.notna(row.get("Elevation_Gained"))
                        else 0
                    ),
                ]

                push_runner_data(row_data)
                success_count += 1
                existing_keys.add(unique_key)

            except Exception as e:
                if HAS_STREAMLIT:
                    st.error(f"Error pushing row {index}: {e}")
                else:
                    print(f"❌ Error pushing row {index}: {e}")
                error_count += 1

        if HAS_STREAMLIT:
            st.success(f"Pushed {success_count} new activities. Errors: {error_count}")
        else:
            print(f"✅ Pushed {success_count} new activities. Errors: {error_count}")

        return success_count, error_count

    except Exception as e:
        if HAS_STREAMLIT:
            st.error(f"Error in push process: {e}")
        else:
            print(f"❌ Error in push process: {e}")
        return 0, len(strava_df)
