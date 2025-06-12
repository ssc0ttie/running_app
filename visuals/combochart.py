import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_combo(data):
    ##GROUP BY
    act_date_group = data.groupby("Week", as_index=False)
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
            y=dist_data["Week"],
            x=dist_data["Distance"],
            orientation="h",
            name="Distance (km)",
            text=dist_data["Distance"],
            marker=dict(color="mediumaquamarine"),
        ),
        secondary_y=False,
    )

    # Add line chart for Pace
    fig.add_trace(
        go.Scatter(
            y=dist_data["Week"],
            x=pace_data["Pace_Mins"],
            name="Pace (min/km)",
            orientation="h",
            mode="lines+markers+text",
            text=pace_data["Pace_Str"],
            marker=dict(size=12, line=dict(width=2, color="crimson")),
        ),
        secondary_y=True,
    )

    # Add second y-axis for Pace
    fig.update_layout(title="Distance x Pace")
    # fig.update_yaxes(title_text="Week", categoryorder ="category ascending", secondary_y=False)
    # fig.update_xaxes(title_text="Distance (km)")
    # fig.update_xaxes(title_text="Pace (min/km)", secondary_x=True)

    fig.update_xaxes(title_text="Distance (km) / Pace (min/km)", range=[0, 15])
    fig.update_yaxes(
        title_text="Week", categoryorder="category ascending", secondary_y=False
    )
    fig.update_yaxes(showgrid=False, secondary_y=True)
    fig.update_layout(width=500, height=800)

    st.plotly_chart(fig, use_container_width=True, key="combo_chart")
