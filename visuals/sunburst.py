# SUNBURST

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_sunburst(data):

    sunburst_data = data.groupby(["Member Name", "Week", "Activity"], as_index=False)[
        "Distance"
    ].sum()

    fig = px.treemap(
        sunburst_data,
        path=["Member Name", "Week", "Activity"],
        values="Distance",
        # title="Distance per Member per Week per Activity",
        color="Distance",
        color_continuous_scale="RdBu",
    )
    fig.update_layout(
        # margin=dict(t=50, l=0, r=0, b=0),
        showlegend=False,
        # legend=dict(
        #     orientation="h",  # Horizontal layout
        #     yanchor="top",
        #     y=-0.02,  # Push it further down
        #     xanchor="left",
        #     x=0.5,
        #     font=dict(size=10),
        # ),
        # font=dict(size=12),
        autosize=True,
        # width=380,  # for mobile
        height=300,
        # margin=dict(l=20, r=20, t=30, b=30),
    )

    st.plotly_chart(fig)


def generate_bubble_chart(data):
    # Ensure numeric types
    data["RPE (1–10 scale)"] = pd.to_numeric(data["RPE (1–10 scale)"], errors="coerce")
    data["HR (bpm)"] = pd.to_numeric(data["HR (bpm)"], errors="coerce")
    data["Distance"] = pd.to_numeric(data["Distance"], errors="coerce")
    data["Pace"] = pd.to_timedelta(data["Pace"], errors="coerce")

    # Drop rows with missing data
    clean_data = data.dropna(
        subset=["RPE (1–10 scale)", "HR (bpm)", "Distance", "Pace"]
    )

    # Group using the cleaned data
    bubble_data = clean_data.groupby(
        [
            "Activity",
        ],
        as_index=False,
    ).agg(
        {
            "RPE (1–10 scale)": "mean",
            "HR (bpm)": "mean",
            "Distance": "mean",
            "Pace": "mean",
        }
    )
    # ---label ---#
    bubble_data["Label"] = (
        bubble_data["Activity"]
        + "<br>HR: "
        + bubble_data["HR (bpm)"].round(0).astype(str)
    )

    bubble_data["Pace (min)"] = bubble_data["Pace"].dt.total_seconds() / 60
    # Create the bubble chart
    fig = px.scatter(
        bubble_data,
        x="Distance",
        y="Pace (min)",
        size="RPE (1–10 scale)",
        color="HR (bpm)",
        hover_name="HR (bpm)",
        text="Label",
        size_max=40,
        color_continuous_scale="Bluered",
        title="Intensity: HR (color), Pace (Y-axis), RPE (size)",
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(line=dict(width=1, color="DarkSlateGrey")),
    )

    fig.update_coloraxes(showscale=False)
    fig.update_layout(showlegend=False, height=450)
    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig)
