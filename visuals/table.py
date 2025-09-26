import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_matrix(data):

    def format_timedelta(td):
        if pd.isnull(td):
            return "00:00:00"
        seconds = int(td.total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

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
            return row["Moving_Time"]
        elif row["Activity"] in non_running_activities:
            return row["Duration_Other"]
        else:
            return pd.NaT

    data["Pace_Str"] = data["Pace"].apply(format_timedelta)
    data["MovingTime_Str"] = data["Moving_Time"].apply(format_timedelta)
    data["Duration_Str"] = data["Duration_Other"].apply(format_timedelta)

    data["Combined_Duration"] = data.apply(get_combined_duration, axis=1)
    data["Combined_Duration_Str"] = data["Combined_Duration"].apply(format_timedelta)

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
            "MovingTime_Str": st.column_config.TextColumn("Moving Time"),
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
            "Combined_Duration_Str": st.column_config.TextColumn("Duration"),
            "Week": st.column_config.TextColumn("Week"),
        },
        column_order=[
            "Date_of_Activity",
            "Activity",
            "Distance",
            "Combined_Duration_Str",
            "Pace_Str",
            # "Duration_Str",
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
