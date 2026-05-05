# data/push_data_simple.py - Completely independent of Streamlit
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import json
import os


def get_google_sheets_creds():
    """Get Google Sheets credentials from environment variable"""
    creds_json = os.environ.get("GOOGLE_SHEETS_CREDENTIALS")
    if creds_json:
        return json.loads(creds_json)
    raise Exception("GOOGLE_SHEETS_CREDENTIALS environment variable not set")


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
    sheet_data = worksheet.get_all_values()
    return sheet_data


def get_existing_uniquekeys_from_sheet():
    sheet_data = get_runner_data()
    if not sheet_data or len(sheet_data) < 2:
        return set()

    header = sheet_data[0]
    try:
        uniquekey_idx = header.index("UniqueKey")
    except ValueError:
        raise ValueError("UniqueKey column not found in sheet")

    existing_keys = {
        row[uniquekey_idx] for row in sheet_data[1:] if len(row) > uniquekey_idx
    }
    return existing_keys


def push_runner_data(data):
    """Append row to sheet"""
    gsclient = get_gsheet_client()
    sheet = gsclient.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    newsource_worksheet = sheet.get_worksheet_by_id(1611308583)
    newsource_worksheet.append_row(data)


def push_strava_data_to_sheet(strava_df):
    """Push Strava data to Google Sheets"""
    print(f"📤 Pushing {len(strava_df)} activities to Google Sheets...")

    success_count = 0
    error_count = 0

    existing_keys = get_existing_uniquekeys_from_sheet()
    print(f"ℹ️ Found {len(existing_keys)} existing activities in sheet")

    for index, row in strava_df.iterrows():
        try:
            unique_key = str(row["UniqueKey"])

            if unique_key in existing_keys:
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
                0,
                None,
                None,
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

            if success_count % 10 == 0:
                print(f"📊 Progress: {success_count} activities pushed...")

        except Exception as e:
            print(f"❌ Error pushing row {index}: {e}")
            error_count += 1

    print(f"✅ Pushed {success_count} new activities. Errors: {error_count}")
    return success_count, error_count
