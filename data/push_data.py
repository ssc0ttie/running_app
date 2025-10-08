import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from data import read_data_uncached as rd
from data import strava as strav


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

    # ---- Load main/historical worksheet (READS EVERYTHING AS STRING)---- #
    worksheet = sheet.get_worksheet_by_id(1611308583)  # or use get_worksheet_by_id(gid)
    sheet = worksheet.get_all_values()
    return sheet


def get_existing_uniquekeys_from_sheet():
    sheet_data = get_runner_data()  # returns list of lists
    if not sheet_data or len(sheet_data) < 2:
        return set()  # empty sheet

    header = sheet_data[0]
    try:
        uniquekey_idx = header.index("UniqueKey")  # find the column index
    except ValueError:
        raise ValueError("UniqueKey column not found in sheet")

    # Skip header row, collect all keys
    existing_keys = {row[uniquekey_idx] for row in sheet_data[1:]}
    return existing_keys


def push_runner_data(data):
    gsclient = get_gsheet_client()
    client = gsclient
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    newsource_worksheet = sheet.get_worksheet_by_id(
        1611308583
    )  # or use get_worksheet_by_id(gid)

    newsource_worksheet.append_row(data)


# 1611308583  the original sheet
# 805185830 the test sheet

# def push_runner_data_dev(hist_df, newlog_df):
#     path = r"C:/Users/king.m/Python/2025/DS Proj/running_app/data/runner_data.xlsx"

#     updated_df = pd.concat([hist_df, newlog_df], ignore_index=True)

#     # Optional cleanup (remove duplicates, sort, etc.)
#     updated_df.drop_duplicates(inplace=True)

#     # Write back to Excel (overwrites existing content in that sheet)
#     with pd.ExcelWriter(path, mode="w", engine="openpyxl") as writer:
#         updated_df.to_excel(writer, sheet_name="for streamlit", index=False)

#     return True


def format_activity_for_sheet(activity_dict):
    """Convert activity dictionary to the row format expected by your sheet"""
    return [
        activity_dict["TimeStamp"],
        activity_dict["Date_of_Activity"],
        activity_dict["Activity"],
        activity_dict["Distance"],
        activity_dict["Pace"],
        activity_dict["HR (bpm)"],
        activity_dict["Cadence (steps/min)"],
        activity_dict["Member Name"],
        activity_dict["Duration"],
    ]


def push_strava_data_to_sheet(strava_df):
    """Push Strava data to Google Sheets with comprehensive type handling"""
    try:
        success_count = 0
        error_count = 0

        # Load existing keys once
        existing_keys = get_existing_uniquekeys_from_sheet()

        for index, row in strava_df.iterrows():
            try:
                unique_key = str(row["UniqueKey"])

                # Skip if already exists
                if unique_key in existing_keys:
                    st.warning(f"Skipping duplicate row with UniqueKey: {unique_key}")
                    continue

                # Convert all values to gspread-compatible types
                row_data = [
                    unique_key,
                    str(row["TimeStamp"]),  # Date to string
                    str(row["Date_of_Activity"]),  # Date to string
                    str(row.get("Activity", "")),  # user defined Activity
                    float(row.get("Distance", 0)),
                    str(row.get("Pace", None)),
                    int(row.get("HR (bpm)", 0)),
                    int(row.get("Cadence (steps/min)", None)),
                    0,  # rpe
                    None,  # Shoe
                    None,  # Remarks
                    str(row.get("Member Name", "Unknown")),
                    str(row.get("Duration", "00:00:00")),
                    str(row.get("Activity", "")),
                ]

                push_runner_data(row_data)
                success_count += 1

                # Add to existing_keys set so the same run isn’t re-added
                existing_keys.add(unique_key)

            except Exception as e:
                st.error(f"Error pushing row {index}: {e}")
                error_count += 1
                continue

        return success_count, error_count

    except Exception as e:
        st.error(f"Error in push process: {e}")
        return 0, len(strava_df)
