import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_matrix_member(data):
    from datetime import datetime, timedelta

    # Filter running-only activities
    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]

    # Group by member
    grouped = filtered_data.groupby("Member Name", as_index=False).agg(
        {
            "Distance": "sum",
            "Moving_Time": "sum",
            "Activity": "count",
            "Pace": "mean",  # timedelta
        }
    )

    # Format timedelta values
    def format_timedelta(td):
        if pd.isnull(td):
            return "00:00:00"
        seconds = int(td.total_seconds())
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    # Add formatted columns
    grouped["Pace_Str"] = grouped["Pace"].apply(format_timedelta)
    grouped["MovingTime_Str"] = grouped["Moving_Time"].apply(format_timedelta)

    # Create pace trend history (last 30 days)
    pace_trend = (
        filtered_data[["Member Name", "Date_of_Activity", "Pace"]].copy().dropna()
    )
    pace_trend["Pace_Minutes"] = pace_trend["Pace"].dt.total_seconds() / 60

    recent_30_days = pd.Timestamp.now() - pd.Timedelta(days=30)
    trend_grouped = (
        pace_trend[pace_trend["Date_of_Activity"] >= recent_30_days]
        .groupby("Member Name")
        .agg({"Pace_Minutes": lambda x: list(x.tail(30))})
        .reset_index()
    )

    # Merge trend data with main summary
    final_df = pd.merge(grouped, trend_grouped, on="Member Name", how="left")

    # Display in Streamlit
    st.dataframe(
        final_df,
        column_config={
            "Pace_Str": st.column_config.TextColumn("Avg Pace"),
            "Distance": st.column_config.ProgressColumn(
                "Distance (km)",
                min_value=0,
                max_value=final_df["Distance"].max(),
                format="%.1f",
            ),
            "MovingTime_Str": st.column_config.TextColumn("Moving Time"),
            "Pace_Minutes": st.column_config.LineChartColumn(
                "Pace Trend",
                y_min=final_df["Pace_Minutes"]
                .apply(lambda x: min(x) if isinstance(x, list) else None)
                .min(),
                y_max=final_df["Pace_Minutes"]
                .apply(lambda x: max(x) if isinstance(x, list) else None)
                .max(),
            ),
            "Member Name": st.column_config.TextColumn("Runner"),
        },
        column_order=[
            "Member Name",
            "Distance",
            "MovingTime_Str",
            "Pace_Str",
            "Pace_Minutes",
        ],
        use_container_width=True,
    )
