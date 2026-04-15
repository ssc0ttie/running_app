# SUNBURST

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


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
            "RPE (1–10 scale)": "count",
        }
    )

    bubble_data["Count"] = clean_data.groupby("Activity").size().values
    # ---label ---#
    bubble_data["Label"] = (
        bubble_data["Activity"]
        + "<br>Avg HR: "
        + bubble_data["HR (bpm)"].round(0).astype(str)
        + "<br> Freq: "
        + bubble_data["Count"].round(0).astype(str)
    )

    bubble_data["Pace (min)"] = bubble_data["Pace"].dt.total_seconds() / 60
    # Create the bubble chart
    fig = px.scatter(
        bubble_data,
        x="Distance",
        y="Pace (min)",
        size="Count",
        color="HR (bpm)",
        # hover_name="HR (bpm)",
        text="Label",
        size_max=40,
        color_continuous_scale="Bluered",
        title="Intensity: HR (color), Pace (Y-axis), Frequency (size)",
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(line=dict(width=1, color="DarkSlateGrey")),
    )

    fig.update_coloraxes(showscale=False)
    fig.update_layout(showlegend=False, height=450)
    fig.update_yaxes(autorange="reversed")

    st.plotly_chart(fig)


def generate_bubble_chart_new(data):
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
        ["Activity"],
        as_index=False,
    ).agg(
        {
            "RPE (1–10 scale)": "mean",
            "HR (bpm)": "mean",
            "Distance": "mean",
            "Pace": "mean",
        }
    )

    bubble_data["Count"] = clean_data.groupby("Activity").size().values

    # ---label ---#
    bubble_data["Label"] = (
        bubble_data["Activity"]
        + "<br>Avg HR: "
        + bubble_data["HR (bpm)"].round(0).astype(str)
        + "<br> Freq: "
        + bubble_data["Count"].round(0).astype(str)
    )

    bubble_data["Pace (min)"] = bubble_data["Pace"].dt.total_seconds() / 60

    # Create the bubble chart
    fig = px.scatter(
        bubble_data,
        x="Distance",
        y="Pace (min)",
        size="Count",
        color="HR (bpm)",
        text="Label",
        size_max=40,
        color_continuous_scale="Bluered",
        title="Intensity: HR (color), Pace (Y-axis), Frequency (size)",
    )

    fig.update_traces(
        textposition="top center",
        marker=dict(line=dict(width=1, color="DarkSlateGrey")),
    )

    fig.update_coloraxes(showscale=False)
    fig.update_layout(
        showlegend=False,
        height=400,
        title_font=dict(color="#2b2b2b", size=14),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis=dict(
            title_font=dict(color="#2b2b2b"),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
        ),
        yaxis=dict(
            title_font=dict(color="#2b2b2b"),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
        ),
    )
    fig.update_yaxes(autorange="reversed")

    return fig
