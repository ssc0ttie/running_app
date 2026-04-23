import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_matrix(data):

    def format_timedelta(td):
        try:
            total_seconds = (
                td.total_seconds() if hasattr(td, "total_seconds") else float(td)
            )
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            secs = int(total_seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        except (TypeError, ValueError):
            return ""

        # Then apply:

    def get_combined_duration(row):
        # First, define what constitutes running vs non-running activities
        running_activities = [
            "Easy Run",
            "Aerobic Run",
            "Tempo Run",
            "Cooldown",
            "Warm up",
            "Speed Work (Zone 4-5 x400M)",
            "LSD Road@ Zone 2 Pace",
            "LSD Trail@ Zone 2 Pace",
            "RACE DAY",
            "Run",
        ]
        non_running_activities = [
            "Strength Training",
            "WeightTraining",
            "Yoga",
            "Cross Train",
            "Rest",
            "Pilates",
        ]
        if row["Activity"] in running_activities:
            # return row["Moving_Time"]
            return row["Duration_Other"]

        elif row["Activity"] in non_running_activities:
            return row["Duration_Other"]
        else:
            return pd.NaT

    data["Pace_Str"] = data["Pace"].apply(format_timedelta)
    data["MovingTime_Str"] = data["Moving_Time"].apply(format_timedelta)
    data["Duration_Str"] = data["Duration_Other"].apply(format_timedelta)

    # data["Combined_Duration"] = data.apply(get_combined_duration, axis=1)
    # data["Combined_Duration_Str"] = data["Combined_Duration"].apply(format_timedelta)

    data = data.sort_values(by="Date", ascending=False)
    # drop columns
    data.drop(["TimeStamp", "Date", "Pace", "Shoe"], axis=1, inplace=True)

    st.dataframe(
        data,
        height=350,
        column_config={
            "Pace_Str": st.column_config.TextColumn("Pace"),
            "Date_of_Activity": st.column_config.DateColumn(
                "Date", format=("MMM DD, ddd")
            ),
            "Activity": st.column_config.TextColumn("Actvity"),
            "Distance": st.column_config.ProgressColumn(
                "Distance",
                min_value=0,
                max_value=data["Distance"].max(),
                format="%.1f",
            ),
            "MovingTime_Str": st.column_config.TextColumn("Duration"),
            "HR (bpm)": st.column_config.NumberColumn(
                "HR",
                format="%d",
            ),
            "Cadence (steps/min)": st.column_config.NumberColumn(
                "Cadence (spm)",
                format="%d",
            ),
            "RPE (1–10 scale)": st.column_config.NumberColumn(
                "RPE",
                min_value=1,
                max_value=10,
                step=1,
            ),
            "Shoe": st.column_config.TextColumn("Shoes"),
            "Remarks": st.column_config.TextColumn("Remarks", width="large"),
            "Member Name": st.column_config.TextColumn("Runner"),
            # "Combined_Duration_Str": st.column_config.TextColumn("Duration"),
            # "Duration_Str": st.column_config.TextColumn("Duration"),
            # "MovingTime_Str": st.column_config.TextColumn("Duration"),
            "Week": st.column_config.TextColumn("Week"),
        },
        column_order=[
            "Date_of_Activity",
            "Activity",
            "Distance",
            # "Combined_Duration_Str",
            "Pace_Str",
            # "Duration_Str",
            "MovingTime_Str",
            "HR (bpm)",
            "Cadence (steps/min)",
            "RPE (1–10 scale)",
            "Shoe",
            "Remarks",
            "Member Name",
            "Week",
        ],
        use_container_width=True,
    )


def generate_matrix_simple(data):
    """Simpler matrix generation with basic formatting"""

    def format_timedelta(td):
        try:
            total_seconds = (
                td.total_seconds() if hasattr(td, "total_seconds") else float(td)
            )
            hours = int(total_seconds // 3600)
            minutes = int((total_seconds % 3600) // 60)
            secs = int(total_seconds % 60)
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        except (TypeError, ValueError):
            return ""

    if data.empty:
        st.info("No data available")
        return

    # Format time columns
    for col in ["Duration", "Duration_Other", "Pace"]:
        if col in data.columns:
            data[col] = data[col].apply(format_timedelta)

    # Select and rename columns for display
    display_cols = {
        "Date_of_Activity": "Date",
        "Activity": "Activity",
        "Distance": "Distance (km)",
        "Duration": "Duration",
        "Pace": "Pace (min/km)",
        "HR (bpm)": "HR",
        "Cadence (steps/min)": "Cadence",
        "Remarks": "Notes",
    }

    # Filter available columns
    available_cols = {k: v for k, v in display_cols.items() if k in data.columns}

    # Create display dataframe
    display_df = data[list(available_cols.keys())].copy()
    display_df = display_df.rename(columns=available_cols)

    # Round numeric columns
    for col in ["Distance (km)", "HR", "Cadence"]:
        if col in display_df.columns:
            display_df[col] = pd.to_numeric(display_df[col], errors="coerce").round(1)

    # Sort by date
    if "Date" in display_df.columns:
        display_df["Date"] = pd.to_datetime(display_df["Date"])
        display_df = display_df.sort_values("Date", ascending=False)
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )


def generate_matrix_new(data, title=""):
    """Generate a styled matrix/dataframe for activity details"""

    if data.empty:
        st.info(f"No {title} data available")
        return

    # Format timedelta columns if they exist
    time_columns = ["Duration", "Duration_Other", "Pace"]
    for col in time_columns:
        if col in data.columns:
            data[col] = data[col].apply(format_timedelta)

    # Select relevant columns for display
    display_columns = [
        "Date_of_Activity",
        "Activity",
        "Distance",
        "Duration",
        "Pace",
        "HR (bpm)",
        "Cadence (steps/min)",
        "Remarks",
        "Member Name",
        "Week",
        "Map_Polyline",
    ]

    # Filter to only columns that exist in the data
    available_columns = [col for col in display_columns if col in data.columns]

    # Create display dataframe
    display_df = data[available_columns].copy()

    # Round numeric columns
    numeric_columns = ["Distance", "HR (bpm)", "Cadence (steps/min)"]
    for col in numeric_columns:
        if col in display_df.columns:
            display_df[col] = pd.to_numeric(display_df[col], errors="coerce").round(1)

    # Sort by date (most recent first)
    if "Date_of_Activity" in display_df.columns:
        display_df["Date_of_Activity"] = pd.to_datetime(
            display_df["Date_of_Activity"], errors="coerce"
        )
        display_df = display_df.sort_values("Date_of_Activity", ascending=False)

    # Display with custom styling
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date_of_Activity": st.column_config.DateColumn(
                "Date", format="YYYY-MM-DD"
            ),
            "Distance": st.column_config.NumberColumn("Distance (km)", format="%.1f"),
            "Duration": st.column_config.TextColumn("Duration"),
            "Pace": st.column_config.TextColumn("Pace (min/km)"),
            "HR (bpm)": st.column_config.NumberColumn("HR (bpm)", format="%.0f"),
            "Cadence (steps/min)": st.column_config.NumberColumn(
                "Cadence", format="%.0f"
            ),
            "Remarks": st.column_config.TextColumn("Notes", width="medium"),
            "Week": st.column_config.TextColumn("Week"),
        },
    )


def format_timedelta(td):
    """Format timedelta objects or numeric values to HH:MM:SS"""
    try:
        if pd.isna(td):
            return ""

        # Handle timedelta objects
        if hasattr(td, "total_seconds"):
            total_seconds = td.total_seconds()
        # Handle numeric values (assuming minutes or seconds)
        elif isinstance(td, (int, float)):
            # Check if it's likely pace format (e.g., 6.5 min/km)
            if td < 60 and td > 0:
                # Treat as minutes (pace)
                minutes = int(td)
                seconds = int((td % 1) * 60)
                return f"{minutes:02d}:{seconds:02d}"
            else:
                total_seconds = td
        else:
            return str(td)

        # Handle negative or zero
        if total_seconds <= 0:
            return ""

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    except (TypeError, ValueError, AttributeError):
        return str(td) if td else ""
