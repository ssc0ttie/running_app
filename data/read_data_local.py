import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import datetime


def get_runner_data_dev():
    df_hist = pd.read_excel(
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
    # WEEK LOOKUP
    df_week = pd.read_excel(
        r"C:/Users/king.m/Python/2025/DS Proj/running_app/data/runner_data.xlsx",
        sheet_name="Log Test",
        header=0,
    )

    # filter only first 3 columns
    df_week = pd.DataFrame(df_week)[["Dates", "WEEK", "Activity"]]
    # rename columns
    df_week.rename(
        columns={"Dates": "Date", "WEEK": "Week", "Activity": "Scheduled_Activity"},
        inplace=True,
    )

    df_week["Date"] = pd.to_datetime(df_week["Date"])

    def time_to_timedelta(t):
        if isinstance(t, datetime.time):
            return datetime.timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        return pd.NaT  # or handle differently if needed

    df_hist["Pace"] = df_hist["Pace"].apply(time_to_timedelta)

    # CONCAT HISTORICAL AND NEWLOG
    # df = pd.concat([df, df3], ignore_index=True)
    # cleanup main df

    # Convert pace to timedelta
    for df in [df_hist]:
        df["Pace"] = pd.to_timedelta(df["Pace"], errors="coerce")
        df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")

    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"], errors="coerce")

    # lookup of weekname
    df = df.merge(df_week, left_on="Date_of_Activity", right_on="Date", how="left")
    # Apply to column

    # CALCULATE MOVING TIME
    df["Moving_Time"] = df["Pace"] * df["Distance"]

    return pd.DataFrame(df)
