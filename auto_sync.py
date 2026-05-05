#!/usr/bin/env python3
"""
Standalone sync script for GitHub Actions
This replicates the "Strava Sync" tab functionality without Streamlit UI
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import your existing modules
from data.fetch_strava_2 import fetch_all_activities
import data.push_data_2 as push


def clean_activity_data(act):
    """Clean and convert numeric values for a single activity (copied from main.py)"""

    def to_float(value, default=0):
        try:
            return float(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    def to_str(value, default=""):
        if value is None:
            return default
        try:
            return str(value)
        except:
            return default

    start_date = act.get("start_date_local")
    if start_date and "T" in start_date:
        date_part = start_date.split("T")[0]
    else:
        date_part = ""

    return {
        "TimeStamp": date_part,
        "Date_of_Activity": date_part,
        "Activity": to_str(act.get("sport_type")),
        "Distance": to_float(act.get("distance")) / 1000,
        "Pace": to_float(act.get("average_speed")),
        "HR (bpm)": to_float(act.get("average_heartrate")),
        "Cadence (steps/min)": to_float(act.get("average_cadence")) * 2,
        "Member Name": to_str(act.get("athlete_name", "Unknown")),
        "Duration": to_float(act.get("moving_time")),
        "Map_Polyline": act.get("map", {}).get("summary_polyline"),
        "Max_Pace": to_float(act.get("max_speed")),
        "Max_HR": to_float(act.get("max_heartrate")),
        "Elevation_Gained": to_float(act.get("total_elevation_gain")),
    }


def convert_speed_to_pace_string(speed_mps):
    """Convert meters per second to min/km pace format"""
    if speed_mps <= 0:
        return "00:00:00"

    pace_seconds_per_km = 1000 / speed_mps
    hours = int(pace_seconds_per_km // 3600)
    minutes = int((pace_seconds_per_km % 3600) // 60)
    seconds = int(pace_seconds_per_km % 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def convert_seconds_to_time_string(total_seconds):
    """Convert seconds to HH:MM:SS format"""
    if total_seconds <= 0:
        return "00:00:00"

    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def main():
    print(f"🚀 Auto Sync Started at {datetime.now()}")
    print("=" * 60)

    # Sync last 30 days (adjust as needed)
    days_back = int(os.environ.get("DAYS_BACK", "30"))
    print(f"📡 Fetching activities from the last {days_back} days...")

    # Fetch activities using your existing function
    activities = fetch_all_activities(days_back)

    if not activities:
        print("❌ No activities fetched")
        return

    print(f"✅ Fetched {len(activities)} raw activities")

    # Clean and convert activities (same as your main.py)
    print("🔄 Cleaning and converting data...")
    cleaned_activities = [clean_activity_data(act) for act in activities]
    strava_df = pd.DataFrame(cleaned_activities)

    # Apply all the same transformations as your main.py
    strava_df["TimeStamp"] = pd.to_datetime(strava_df["TimeStamp"]).dt.date
    strava_df["Date_of_Activity"] = pd.to_datetime(
        strava_df["Date_of_Activity"]
    ).dt.date
    strava_df["Distance"] = (strava_df["Distance"]).round(2)

    # Convert Pace
    strava_df["Pace"] = pd.to_numeric(strava_df["Pace"], errors="coerce").fillna(0)
    strava_df["Pace"] = strava_df["Pace"].apply(
        lambda x: convert_speed_to_pace_string(x) if x > 0 else "00:00:00"
    )

    # Convert Max Pace
    strava_df["Max_Pace"] = pd.to_numeric(
        strava_df["Max_Pace"], errors="coerce"
    ).fillna(0)
    strava_df["Max_Pace"] = strava_df["Max_Pace"].apply(
        lambda x: convert_speed_to_pace_string(x) if x > 0 else "00:00:00"
    )

    # Convert HR and Cadence
    strava_df["HR (bpm)"] = strava_df["HR (bpm)"].round().astype(int)
    strava_df["Max_HR"] = strava_df["Max_HR"].round().astype(int)
    strava_df["Cadence (steps/min)"] = (
        strava_df["Cadence (steps/min)"].round().astype(int)
    )

    # Convert Duration
    strava_df["Duration"] = pd.to_numeric(
        strava_df["Duration"], errors="coerce"
    ).fillna(0)
    strava_df["Duration"] = strava_df["Duration"].apply(convert_seconds_to_time_string)

    # Create UniqueKey
    strava_df["UniqueKey"] = (
        strava_df[["Date_of_Activity", "Member Name", "Activity", "HR (bpm)"]]
        .astype(str)
        .agg("|".join, axis=1)
    )

    print(f"📊 Processed {len(strava_df)} activities for sync")

    # Push to Google Sheets
    print("📤 Pushing to Google Sheets...")
    success_count, error_count = push.push_strava_data_to_sheet(strava_df)

    print("=" * 60)
    print(f"🏁 Sync Completed at {datetime.now()}")
    print(f"📈 Summary: {success_count} new activities added, {error_count} errors")

    if error_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
