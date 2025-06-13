import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import datetime


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


def get_runner_data():
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    # USING "for streamlit" tab - for historical
    worksheet = sheet.get_worksheet_by_id(1508007696)  # or use get_worksheet_by_id(gid)
    data = worksheet.get_all_values()

    df = pd.DataFrame(data)

    # RENAME HEADERS#
    df.rename(
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

    # WEEK LOOKUP
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    week_lookup_worksheet = sheet.get_worksheet_by_id(
        336401596
    )  # or use get_worksheet_by_id(gid)
    week_lookup_data = week_lookup_worksheet.get_all_records()

    # streamlit_new_source - for new logs
    newsource_worksheet = sheet.get_worksheet_by_id(1611308583)
    new_source_data = newsource_worksheet.get_all_records()

    ################################################################
    df2 = pd.DataFrame(week_lookup_data)
    df3 = pd.DataFrame(new_source_data)

    # filter only first 3 columns
    df2 = df2.iloc[:, 0:3]
    # rename columns
    df2.rename(
        columns={"Dates": "Date", "WEEK": "Week", "Activity": "Scheduled_Activity"},
        inplace=True,
    )

    df2["Date"] = pd.to_datetime(df2["Date"])

    # CONCAT HISTORICAL AND NEWLOG
    df["Pace"] = pd.to_timedelta(df["Pace"])
    df3["Pace"] = pd.to_timedelta(df3["Pace"])

    df["Distance"] = pd.to_numeric(df["Distance"])
    df3["Distance"] = pd.to_numeric(df3["Distance"])

    # APPEND
    df = pd.concat([df, df3], ignore_index=True)
    # cleanup main df
    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"], errors="coerce")
    df["Pace"] = pd.to_timedelta(df["Pace"])

    def pace_str_to_minutes(pace_str):
        # """Convert a pace string 'MM:SS' to minutes as float."""
        try:
            minutes, seconds = map(int, pace_str.split(":"))
            return minutes + seconds / 60
        except:
            return None

    df["Pace"] = df["Pace"].apply(pace_str_to_minutes)
    df["Distance"] = pd.to_numeric(df["Distance"])

    # lookup of weekname
    df = df.merge(df2, left_on="Date_of_Activity", right_on="Date", how="left")
    # Apply to column

    # CALCULATE MOVING TIME
    df["Moving_Time"] = df["Pace"] * df["Distance"]

    return pd.DataFrame(df)


def get_runner_data_dev():
    df = pd.read_excel(
        r"C:/Users/king.m/Python/2025/DS Proj/running_app/data/runner_data.xlsx",
        sheet_name="for streamlit",
        header=None,
        names=[
            "TimeStamp",
            "Date_of_Activity",
            "Activity",
            "Distance",
            "Pace",
            "HR (bpm)",
            "Cadence (steps/min)",
            "RPE (1–10 scale)",
            "Shoe",
            "Remarks",
            "Member Name",
        ],
    )
    # RENAME HEADERS#
    df.rename(
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
    # WEEK LOOKUP
    df2 = pd.read_excel(
        r"C:/Users/king.m/Python/2025/DS Proj/running_app/data/runner_data.xlsx",
        sheet_name="Log Test",
        header=0,
    )

    ################################################################

    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    week_lookup_worksheet = sheet.get_worksheet_by_id(
        336401596
    )  # or use get_worksheet_by_id(gid)

    # streamlit_new_source - for new logs
    newsource_worksheet = sheet.get_worksheet_by_id(1611308583)
    new_source_data = newsource_worksheet.get_all_records()

    ################################################################

    # df3 = pd.DataFrame(new_source_data)

    # filter only first 3 columns
    df2 = df2.iloc[:, 0:3]
    # rename columns
    df2.rename(
        columns={"Dates": "Date", "WEEK": "Week", "Activity": "Scheduled_Activity"},
        inplace=True,
    )

    df2["Date"] = pd.to_datetime(df2["Date"])

    def time_to_timedelta(t):
        if isinstance(t, datetime.time):
            return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return pd.NaT  # or handle differently if needed

    df["Pace"] = df["Pace"].apply(time_to_timedelta)

    # CONCAT HISTORICAL AND NEWLOG
    # df = pd.concat([df, df3], ignore_index=True)
    # cleanup main df
    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"], errors="coerce")

    df["Distance"] = pd.to_numeric(df["Distance"])

    # lookup of weekname
    df = df.merge(df2, left_on="Date_of_Activity", right_on="Date", how="left")
    # Apply to column

    # CALCULATE MOVING TIME
    df["Moving_Time"] = df["Pace"] * df["Distance"]

    return pd.DataFrame(df)
