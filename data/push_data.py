import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
from data import read_data_uncached as rd
from data import strava as strav
import numpy as np


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
    worksheet = sheet.get_worksheet_by_id(1611308583)
    sheet_data = worksheet.get_all_values()

    return sheet_data


def get_existing_uniquekeys_from_sheet():
    """Get existing UniqueKeys from main activities sheet"""
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


def get_existing_zone_keys_from_sheet_original():
    """Get existing Zone_UniqueKeys to avoid duplicates"""
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

    try:
        try:
            zone_worksheet = sheet.get_worksheet_by_id(2080759221)
        except gspread.WorksheetNotFound:
            # Create new worksheet with your schema
            zone_worksheet = sheet.add_worksheet(
                title="Zone_Data", rows="10000", cols="20"
            )
            # Add headers matching your pattern
            headers = [
                "Zone_UniqueKey",
                "Parent_UniqueKey",
                "Date_of_Activity",
                "Member Name",
                "Activity",
                "Avg_HR",
                "Zone_Type",
                "Zone",
                "Zone_Name",
                "Min_Value",
                "Max_Value",
                "Time_In_Zone",
                "Percentage",
            ]
            zone_worksheet.append_row(headers)
            return set()

        existing_data = zone_worksheet.get_all_values()
        if len(existing_data) > 1:
            header = existing_data[0]
            try:
                key_idx = header.index("Zone_UniqueKey")
                return {row[key_idx] for row in existing_data[1:] if len(row) > key_idx}
            except ValueError:
                return set()
        return set()

    except Exception as e:
        st.warning(f"Could not access zone worksheet: {e}")
        return set()


def push_runner_data(data, worksheet_name="main"):
    """Push data to specified worksheet"""
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

    if worksheet_name == "main":
        worksheet = sheet.get_worksheet_by_id(1611308583)
    else:
        worksheet = sheet.worksheet(worksheet_name)

    worksheet.append_row(data)


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

        existing_keys = get_existing_uniquekeys_from_sheet()

        for index, row in strava_df.iterrows():
            try:
                unique_key = str(row["UniqueKey"])

                if unique_key in existing_keys:
                    st.warning(f"Skipping duplicate row with UniqueKey: {unique_key}")
                    continue

                row_data = [
                    unique_key,
                    str(row["TimeStamp"]),
                    str(row["Date_of_Activity"]),
                    str(row.get("Activity", "")),
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
                    str(row.get("Map_Polyline", "")),
                    str(row.get("Max_Pace", None)),
                    int(row.get("Max_HR", None)),
                    int(row.get("Elevation_Gained", None)),
                ]

                push_runner_data(row_data, worksheet_name="main")
                success_count += 1
                existing_keys.add(unique_key)

            except Exception as e:
                st.error(f"Error pushing row {index}: {e}")
                error_count += 1
                continue

        return success_count, error_count

    except Exception as e:
        st.error(f"Error in push process: {e}")
        return 0, len(strava_df)


def push_zone_data_to_sheet_original(zones_df, parent_unique_key, activity_row_data):
    """
    Push zone distribution data to Google Sheets with proper linking.

    Args:
        zones_df: DataFrame with zone data
        parent_unique_key: The UniqueKey from main activities sheet
        activity_row_data: Dict with Date, Member Name, Activity, Avg_HR
    """
    try:
        success_count = 0
        error_count = 0

        existing_zone_keys = get_existing_zone_keys_from_sheet()

        for index, row in zones_df.iterrows():
            try:
                # Convert all values to native Python types
                zone_key = f"{parent_unique_key}_{row['Type']}_{row['Zone']}"

                if zone_key in existing_zone_keys:
                    continue

                # Helper function to convert any value to native Python type
                def to_native(val):
                    if pd.isna(val):
                        return ""
                    if isinstance(val, (np.int64, np.int32, np.int16, np.int8)):
                        return int(val)
                    if isinstance(val, (np.float64, np.float32)):
                        return float(val)
                    if isinstance(val, pd.Timestamp):
                        return str(val)
                    return val

                # Prepare row data with converted types
                row_data = [
                    str(zone_key),  # Zone_UniqueKey
                    str(parent_unique_key),  # Parent_UniqueKey
                    str(activity_row_data["Date"]),  # Date_of_Activity
                    str(activity_row_data["Member Name"]),  # Member Name
                    str(activity_row_data["Activity"]),  # Activity
                    (
                        int(activity_row_data["Avg_HR"])
                        if activity_row_data["Avg_HR"]
                        else ""
                    ),  # Avg_HR
                    str(row["Type"]),  # Zone_Type (HR or Pace)
                    str(row["Zone"]),  # Zone (Z1, Z2, etc.)
                    str(row["Zone Name"]),  # Zone_Name
                    str(to_native(row.get("Min", ""))),  # Min_Value
                    str(to_native(row.get("Max", ""))),  # Max_Value
                    str(row.get("Time", "")),  # Time_In_Zone
                    str(row.get("Percentage", "")),  # Percentage
                ]

                push_runner_data(row_data, worksheet_name="Zone_Data")
                success_count += 1
                existing_zone_keys.add(zone_key)

            except Exception as e:
                st.error(f"Error pushing zone row {index}: {e}")
                error_count += 1
                continue

        return success_count, error_count

    except Exception as e:
        st.error(f"Error in zone push process: {e}")
        return 0, len(zones_df) if zones_df is not None else 0


def push_zone_data_to_sheet(zones_df, parent_unique_key, activity_row_data):
    """
    Push zone distribution data to Google Sheets with proper linking.
    """
    try:
        success_count = 0
        error_count = 0

        # DEBUG: Print input data
        # st.write(f"🔍 DEBUG: zones_df has {len(zones_df)} rows")
        # st.write(f"🔍 DEBUG: parent_unique_key = {parent_unique_key}")
        # st.write(f"🔍 DEBUG: activity_row_data = {activity_row_data}")

        # Check if zones_df is empty
        if zones_df is None or zones_df.empty:
            st.warning("zones_df is empty!")
            return 0, 0

        # Show first few rows of zones_df
        # st.write("🔍 DEBUG: First 3 rows of zones_df:")
        # st.dataframe(zones_df.head(3))

        existing_zone_keys = get_existing_zone_keys_from_sheet()
        # st.write(
        #     f"🔍 DEBUG: Found {len(existing_zone_keys)} existing zone keys from sheet"
        # )

        for index, row in zones_df.iterrows():
            try:
                zone_key = f"{parent_unique_key}_{row['Type']}_{row['Zone']}"
                # st.write(f"🔍 DEBUG: Processing row {index}: zone_key = {zone_key}")

                if zone_key in existing_zone_keys:
                    # st.write(f"⏭️ Skipping duplicate: {zone_key}")
                    continue

                st.write(f"✅ Pushing new: {zone_key}")

                # Helper function
                def to_native(val):
                    if pd.isna(val):
                        return ""
                    if isinstance(val, (np.int64, np.int32, np.int16, np.int8)):
                        return int(val)
                    if isinstance(val, (np.float64, np.float32)):
                        return float(val)
                    if isinstance(val, pd.Timestamp):
                        return str(val)
                    return val

                row_data = [
                    str(zone_key),
                    str(parent_unique_key),
                    str(activity_row_data["Date"]),
                    str(activity_row_data["Member Name"]),
                    str(activity_row_data["Activity"]),
                    (
                        int(activity_row_data["Avg_HR"])
                        if activity_row_data["Avg_HR"]
                        else ""
                    ),
                    str(row["Type"]),
                    str(row["Zone"]),
                    str(row["Zone Name"]),
                    str(to_native(row.get("Min", ""))),
                    str(to_native(row.get("Max", ""))),
                    str(row.get("Time", "")),
                    str(row.get("Percentage", "")),
                ]

                # st.write(f"📤 row_data: {row_data[:5]}...")  # First 5 items

                push_runner_data(row_data, worksheet_name="Zone_Data")
                success_count += 1
                existing_zone_keys.add(zone_key)

            except Exception as e:
                st.error(f"Error pushing row {index}: {e}")
                error_count += 1
                continue

        st.write(
            f"✅ FINAL: success_count = {success_count}, error_count = {error_count}"
        )
        return success_count, error_count

    except Exception as e:
        st.error(f"Error in zone push process: {e}")
        return 0, len(zones_df) if zones_df is not None else 0


def get_existing_zone_keys_from_sheet():
    """Get existing Zone_UniqueKeys to avoid duplicates"""
    client = get_gsheet_client()
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

    try:
        try:
            zone_worksheet = sheet.worksheet("Zone_Data")
            print(f"✅ Found Zone_Data worksheet")
        except gspread.WorksheetNotFound:
            print(f"❌ Zone_Data worksheet not found, creating new one")
            zone_worksheet = sheet.add_worksheet(
                title="Zone_Data", rows="10000", cols="20"
            )
            headers = [
                "Zone_UniqueKey",
                "Parent_UniqueKey",
                "Date_of_Activity",
                "Member Name",
                "Activity",
                "Avg_HR",
                "Zone_Type",
                "Zone",
                "Zone_Name",
                "Min_Value",
                "Max_Value",
                "Time_In_Zone",
                "Percentage",
            ]
            zone_worksheet.append_row(headers)
            return set()

        existing_data = zone_worksheet.get_all_values()
        # print(f"📊 Raw existing_data length: {len(existing_data)}")

        if len(existing_data) > 1:
            header = existing_data[0]
            # print(f"📊 Header: {header}")
            try:
                key_idx = header.index("Zone_UniqueKey")
                # print(f"📊 Zone_UniqueKey column index: {key_idx}")
                keys = {row[key_idx] for row in existing_data[1:] if len(row) > key_idx}
                # print(f"📊 Keys found: {keys}")
                return keys
            except ValueError as e:
                print(f"❌ 'Zone_UniqueKey' not in header: {e}")
                return set()
        else:
            # print(f"📊 No data rows, returning empty set")
            return set()

    except Exception as e:
        st.warning(f"Could not access zone worksheet: {e}")
        return set()
