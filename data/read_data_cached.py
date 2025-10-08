import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import datetime
import numpy as np


@st.cache_resource
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
@st.cache_data(ttl=300)  # refresh every 5 minutes
def get_runner_data():
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

    # ---- Load main/historical worksheet (READS EVERYTHING AS STRING)---- #
    worksheet = sheet.get_worksheet_by_id(1508007696)  # or use get_worksheet_by_id(gid)
    data = worksheet.get_all_values()

    df_hist = pd.DataFrame(data)

    # RENAME HEADERS#
    df_hist.rename(
        columns={
            0: "UniqueKey",
            1: "TimeStamp",
            2: "Date_of_Activity",
            3: "Activity",
            4: "Distance",
            5: "Pace",
            6: "HR (bpm)",
            7: "Cadence (steps/min)",
            8: "RPE (1–10 scale)",
            9: "Shoe",
            10: "Remarks",
            11: "Member Name",
            12: "Activity_ref",
            13: "Duration_Other",
        },
        inplace=True,
    )

    #######DATA CLEANUP######

    # ---- Load week lookup ---- #
    week_lookup_data = sheet.get_worksheet_by_id(336401596).get_all_records()
    df_week = pd.DataFrame(week_lookup_data)[["Dates", "WEEK", "Activity"]]
    df_week.rename(
        columns={
            "Dates": "Date",
            "WEEK": "Week",
            "Activity": "Scheduled_Activity",
        },
        inplace=True,
    )
    df_week["Date"] = pd.to_datetime(df_week["Date"])

    # ---- Load week lookup ---- #
    new_logs_data = sheet.get_worksheet_by_id(1611308583).get_all_records()
    df_new = pd.DataFrame(new_logs_data)

    # Convert pace to timedelta
    for df in [df_hist, df_new]:
        df["Pace"] = pd.to_timedelta(df["Pace"], errors="coerce")
        df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")
        # df["RPE (1–10 scale)"] = pd.to_numeric(df["RPE (1–10 scale)"], errors="coerce")

    ## ------------------  Combine historical + new  --------------#
    common_cols = list(set(df_hist.columns) | set(df_new.columns))
    df_hist = df_hist.reindex(columns=common_cols)
    df_new = df_new.reindex(columns=common_cols)

    df = pd.concat([df_hist, df_new], ignore_index=True)

    # Helper function to convert 'MM:SS' pace string to total minutes as float (if needed elsewhere)
    def pace_str_to_minutes(pace_str):
        try:
            minutes, seconds = map(int, pace_str.split(":"))
            return minutes + seconds / 60
        except Exception:
            return None

    # ------------pace str for metrics -----------------#
    # Create a display-friendly pace string column 'Pace_Str' from the timedelta 'Pace'
    def format_timedelta_to_pace_str(td):
        if pd.isna(td):
            return ""
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"

    df["Pace_Str"] = df["Pace"].apply(format_timedelta_to_pace_str)

    # ------------clean lookup dates and merge -----------------#
    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"], errors="coerce")
    df_week["Date"] = pd.to_datetime(df_week["Date"])
    df = df.merge(df_week, left_on="Date_of_Activity", right_on="Date", how="left")

    # CALCULATE MOVING TIME

    # df["Moving_Time"] = df["Pace"] * df["Distance"]
    # df["Moving_Time"] = pd.to_timedelta(df["Moving_Time"])

    df["Moving_Time"] = pd.to_timedelta(df["Duration_Other"])

    # create uniquekey
    df["UniqueKey"] = (
        df["Date_of_Activity"].astype(str)
        + "|"
        + df["Member Name"].astype(str)
        + "|"
        + df["Activity"].astype(str)
    )

    return df


def get_worksheet_object():
    """Return the Google Sheets worksheet object for writing"""
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    worksheet = sheet.get_worksheet_by_id(1611308583)  # Your worksheet ID
    return worksheet
