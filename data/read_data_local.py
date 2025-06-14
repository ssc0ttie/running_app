import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import datetime


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
