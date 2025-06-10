import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd


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
    # """
    # https://docs.google.com/spreadsheets/d/1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM/edit?usp=sharing

    # """

    ##last version before 06102025##
    # sheet_id = "1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM"
    # historical_log_gid = "1508007696"
    # week_lookup_gid = "336401596"
    # prog_gid = 0
    # url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid="

    # pd.set_option("display.max_colum", 50)

    # # Read Historical Data and adding header names

    # df = pd.read_csv(
    #     f"{url}{historical_log_gid}",
    #     header=None,
    #     names=[
    #         "TimeStamp",
    #         "Date_of_Activity",
    #         "Activity",
    #         "Distance",
    #         "Pace",
    #         "Time (moving time)",
    #         "HR (bpm)",
    #         "Cadence (steps/min)",
    #         "RPE (1–10 scale)",
    #         "Shoe",
    #         "Remarks",
    #         "Member Name",
    #     ],
    # )

    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    # USING for streamlit tab
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
            5: "Time (moving time)",
            6: "HR (bpm)",
            7: "Cadence (steps/min)",
            8: "RPE (1–10 scale)",
            9: "Shoe",
            10: "Remarks",
            11: "Member Name",
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
    df2 = pd.DataFrame(week_lookup_data)

    # filter only first 3 columns
    df2 = df2.iloc[:, 0:3]
    # rename columns
    df2.rename(
        columns={"Dates": "Date", "WEEK": "Week", "Activity": "Scheduled_Activity"},
        inplace=True,
    )

    df2["Date"] = pd.to_datetime(df2["Date"])
    # cleanup main df
    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"], errors="coerce")
    df["Pace"] = pd.to_timedelta(df["Pace"])
    df["Distance"] = pd.to_numeric(df["Distance"])

    # lookup of weekname
    df = df.merge(df2, left_on="Date_of_Activity", right_on="Date", how="left")
    # Apply to column

    # CALCULATE MOVING TIME
    df["Moving_Time"] = df["Pace"] * df["Distance"]

    return pd.DataFrame(df)
