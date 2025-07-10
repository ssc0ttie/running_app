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

    data["Pace_Str"] = data["Pace"].apply(format_timedelta)
    data["MovingTime_Str"] = data["Moving_Time"].apply(format_timedelta)
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
                "Distance (km)",
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
        },
        column_order=[
            "Date_of_Activity",
            "Activity",
            "Distance",
            "MovingTime_Str",
            "Pace_Str",
            "HR (bpm)",
            "Cadence (steps/min)",
            "RPE (1–10 scale)",
            "Shoe",
            "Remarks",
            "Member Name",
        ],
        use_container_width=True,
    )
