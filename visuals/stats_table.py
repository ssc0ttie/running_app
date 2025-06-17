import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_matrix_member(data):
    ##GROUP BY
    filtered_data = data[
        ~data["Activity"].isin(
            [
                "Rest",
                "Cross Train",
                "Strength Training",
                0,
            ]
        )
    ]  # filter non running activity

    data = filtered_data.groupby("Member Name", as_index=False).agg(
        {
            "Distance": "sum",
            "Moving_Time": "sum",
            "Activity": "count",
            "Pace": "mean",  # timedelta format
        }
    )

    # cleanup
    data["Pace_Str"] = (
        data["Pace"]
        .apply(
            lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
        )
        .astype(str)
    )

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

    st.dataframe(
        data,
        # height=350,
        column_config={
            "Pace_Str": st.column_config.TextColumn("Pace"),
            "Date_of_Activity": st.column_config.DateColumn(
                "Date", format=("MMM DD, ddd")
            ),
            "Activity": st.column_config.TextColumn("Actvities"),
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
            "Member Name",
            "Activity",
            "Distance",
            "MovingTime_Str",
            "Pace_Str",
        ],
        use_container_width=True,
    )
