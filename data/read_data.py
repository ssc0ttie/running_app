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
@st.cache_data(ttl=600)  # refresh every 5 minutes
def get_runner_data():
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

    # ---- Load main/historical worksheet ---- #
    worksheet = sheet.get_worksheet_by_id(1508007696)  # or use get_worksheet_by_id(gid)
    data = worksheet.get_all_values()

    df_hist = pd.DataFrame(data)

    # RENAME HEADERS#
    df_hist.rename(
        columns={
            0: "TimeStamp",
            1: "Date_of_Activity",
            2: "Activity",
            3: "Distance",
            4: "Pace",
            5: "HR (bpm)",
            6: "Cadence (steps/min)",
            7: "RPE (1–10 scale)",
            8: "Shoe",
            9: "Remarks",
            10: "Member Name",
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

    # -----measure to fix pace having NAT-----#
    def time_to_timedelta(t):
        if isinstance(t, datetime.time):
            return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return pd.NaT  # or handle differently if needed

    df_new["Pace"] = df_new["Pace"].apply(time_to_timedelta)

    # Convert pace to timedelta
    for df in [df_hist, df_new]:
        # df["Pace"] = pd.to_timedelta(df["Pace"], errors="coerce")
        df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")

    ## ------------------  Combine historical + new  --------------#
    df = pd.concat([df_hist, df_new], ignore_index=True)

    def pace_str_to_minutes(pace_str):
        # """Convert a pace string 'MM:SS' to minutes as float."""
        try:
            minutes, seconds = map(int, pace_str.split(":"))
            return minutes + seconds / 60
        except:
            return None

    # ------------pace str for metrics -----------------#

    df["Pace"] = pd.to_timedelta(df["Pace"], errors="coerce")
    df["Distance"] = pd.to_numeric(df["Distance"])
    # df["Pace_Str"] = df["Pace"].apply(
    #     lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    # )
    # lookup of weekname
    # ------------clean lookup dates and merge -----------------#
    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"])
    df_week["Date"] = pd.to_datetime(df_week["Date"])
    df = df.merge(df_week, left_on="Date_of_Activity", right_on="Date", how="left")

    # CALCULATE MOVING TIME
    df["Moving_Time"] = df["Pace"] * df["Distance"]

    return df
