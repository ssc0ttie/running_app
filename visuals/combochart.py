import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_combo(data):
    ##GROUP BY
    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]  # filter non running activity
    act_date_group = filtered_data.groupby("Week", as_index=False)
    dist_data = act_date_group["Distance"].sum()
    pace_data = act_date_group["Pace"].mean()

    # for plotting
    pace_data["Pace_Mins"] = pace_data["Pace"].dt.total_seconds() / 60

    pace_data["Pace_Str"] = pace_data["Pace"].apply(
        lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    )
    # create subplot
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar chart for Distance
    fig.add_trace(
        go.Bar(
            x=dist_data["Week"],
            y=dist_data["Distance"],
            name="Distance (km)",
            text=dist_data["Distance"].astype(int),
            marker=dict(color="mediumaquamarine"),
        )
    )

    # Add line chart for Pace
    fig.add_trace(
        go.Scatter(
            x=dist_data["Week"],
            y=pace_data["Pace_Mins"],
            name="Pace (min/km)",
            yaxis="y2",
            text=pace_data["Pace_Str"].astype(str),
            textposition="top center",
            mode="lines+markers+text",
            marker=dict(size=12, line=dict(width=2, color="crimson")),
        ),
    )

    # Add second y-axis for Pace
    # fig.update_layout(title="Distance x Pace")
    fig.update_xaxes(title_text="Week")
    fig.update_yaxes(title_text="KMS", secondary_y=False)
    fig.update_yaxes(title_text="Pace (min/km)", secondary_y=True)
    fig.update_layout(
        width=500,  # Set the desired width in pixels
        height=700,  # Set the desired height in pixels
    )
    st.plotly_chart(fig, use_container_width=True, key="combo_chart")
