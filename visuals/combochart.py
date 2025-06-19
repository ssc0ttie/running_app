import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_combo(data):
    ##GROUP BY
    data["Pace"] = pd.to_timedelta(data["Pace"], errors="coerce")
    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]  # filter non running activity
    act_date_group = filtered_data.groupby("Week", as_index=False)
    dist_data = act_date_group["Distance"].sum()
    pace_data = act_date_group["Pace"].mean()
    cadence_data = act_date_group["Cadence (steps/min)"].mean()

    # Convert pace to minutes
    pace_data["Pace"] = pd.to_timedelta(pace_data["Pace"], errors="coerce")
    pace_data["Pace_Mins"] = pace_data["Pace"].dt.total_seconds() / 60

    # Format pace as mm:ss
    pace_data["Pace_Str"] = pace_data["Pace"].apply(
        lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    )

    # Calculate week-over-week percent change for Distance, Cadence and Pace
    dist_data["Distance_Pct_Change"] = dist_data["Distance"].pct_change() * 100
    pace_data["Pace_Pct_Change"] = pace_data["Pace_Mins"].pct_change() * 100
    cadence_data["Cadence_Pct_Change"] = (
        cadence_data["Cadence (steps/min)"].pct_change() * 100
    )

    #  Create delta labels
    def format_delta(val):
        if pd.isna(val):
            return ""
        arrow = "<span style='color:green'>&#9650;</span>" if val > 0 else "🔻"
        color = "green" if val > 0 else "red"
        return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    def format_delta_rev(val):
        if pd.isna(val):
            return ""
        arrow = "🔻" if val > 0 else "<span style='color:green'>&#9650;</span>"
        color = "red" if val > 0 else "green"
        return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    dist_data["Distance_Pct_Change_Label"] = dist_data["Distance_Pct_Change"].apply(
        format_delta
    )
    pace_data["Pace_Pct_Change_Label"] = pace_data["Pace_Pct_Change"].apply(
        format_delta_rev
    )
    cadence_data["Cadence_Pct_Change_Label"] = cadence_data["Cadence_Pct_Change"].apply(
        format_delta
    )

    # Combine labels
    dist_labels = (
        dist_data["Distance"].round(1).astype(str)
        + " km<br>"
        + dist_data["Distance_Pct_Change_Label"]
    )
    pace_labels = pace_data["Pace_Str"] + "<br>" + pace_data["Pace_Pct_Change_Label"]
    cadence_labels = (
        cadence_data["Cadence (steps/min)"].round(1).astype(str)
        + " spm<br>"
        + cadence_data["Cadence_Pct_Change_Label"]
    )

    # Create combo plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar chart for Distance
    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(
            x=dist_data["Week"],
            y=dist_data["Distance"],
            name="Distance (km)",
            text=dist_labels,
            textposition="auto",
            marker=dict(color="mediumaquamarine"),
        ),
    )

    fig_bar.update_layout(
        title="Weekly Distance (km)",
        yaxis_title="KM",
        xaxis_title="Week",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )

    st.plotly_chart(fig_bar, use_container_width=True, key="distance_chart")

    # ---------- 📈 Pace Line Chart ----------
    fig_line = go.Figure()
    fig_line.add_trace(
        go.Scatter(
            x=pace_data["Week"],
            y=pace_data["Pace_Mins"],
            mode="lines+markers+text",
            text=pace_labels,
            textposition="top center",
            name="Pace",
            line=dict(color="#986868", width=2),
            marker=dict(size=5, line=dict(width=2, color="crimson")),
        )
    )
    fig_line.update_layout(
        title="Weekly Average Pace (min/km)",
        yaxis_title="Pace (min/km)",
        xaxis_title="Week",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )

    fig_line.update_yaxes(autorange="reversed")

    st.plotly_chart(fig_line, use_container_width=True, key="pace_chart")

    # ---------- 📉 Cadence Area Chart ----------
    fig_area = go.Figure()
    fig_area.add_trace(
        go.Scatter(
            x=cadence_data["Week"],
            y=cadence_data["Cadence (steps/min)"],
            mode="lines+markers+text",
            fill="tozeroy",
            text=cadence_labels,
            textposition="top center",
            name="Cadence",
            line=dict(color="royalblue", width=2),
            marker=dict(size=6),
        )
    )
    fig_area.update_layout(
        title="Weekly Average Cadence (spm)",
        yaxis_title="Steps per Minute",
        xaxis_title="Week",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig_area, use_container_width=True, key="cadence_chart")


def generate_combo_daily(data):
    ##GROUP BY
    data["Pace"] = pd.to_timedelta(data["Pace"], errors="coerce")
    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]  # filter non running activity
    act_date_group = filtered_data.groupby("Date", as_index=False)
    dist_data = act_date_group["Distance"].sum()
    pace_data = act_date_group["Pace"].mean()
    cadence_data = act_date_group["Cadence (steps/min)"].mean()

    # Convert pace to minutes
    pace_data["Pace"] = pd.to_timedelta(pace_data["Pace"], errors="coerce")
    pace_data["Pace_Mins"] = pace_data["Pace"].dt.total_seconds() / 60

    # Format pace as mm:ss
    pace_data["Pace_Str"] = pace_data["Pace"].apply(
        lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    )

    # Calculate Date-over-Date percent change for Distance, Cadence and Pace
    dist_data["Distance_Pct_Change"] = dist_data["Distance"].pct_change() * 100
    pace_data["Pace_Pct_Change"] = pace_data["Pace_Mins"].pct_change() * 100
    cadence_data["Cadence_Pct_Change"] = (
        cadence_data["Cadence (steps/min)"].pct_change() * 100
    )

    #  Create delta labels
    def format_delta(val):
        if pd.isna(val):
            return ""
        arrow = "<span style='color:green'>&#9650;</span>" if val > 0 else "🔻"
        color = "green" if val > 0 else "red"
        return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    def format_delta_rev(val):
        if pd.isna(val):
            return ""
        arrow = "🔻" if val > 0 else "<span style='color:green'>&#9650;</span>"
        color = "red" if val > 0 else "green"
        return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    dist_data["Distance_Pct_Change_Label"] = dist_data["Distance_Pct_Change"].apply(
        format_delta
    )
    pace_data["Pace_Pct_Change_Label"] = pace_data["Pace_Pct_Change"].apply(
        format_delta_rev
    )
    cadence_data["Cadence_Pct_Change_Label"] = cadence_data["Cadence_Pct_Change"].apply(
        format_delta
    )

    # Combine labels
    dist_labels = (
        dist_data["Distance"].round(1).astype(str)
        + " km<br>"
        + dist_data["Distance_Pct_Change_Label"]
    )
    pace_labels = pace_data["Pace_Str"] + "<br>" + pace_data["Pace_Pct_Change_Label"]
    cadence_labels = (
        cadence_data["Cadence (steps/min)"].round(1).astype(str)
        + " spm<br>"
        + cadence_data["Cadence_Pct_Change_Label"]
    )

    # Create combo plot
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar chart for Distance
    fig_bar = go.Figure()
    fig_bar.add_trace(
        go.Bar(
            x=dist_data["Date"],
            y=dist_data["Distance"],
            name="Distance (km)",
            text=dist_labels,
            textposition="auto",
            marker=dict(color="mediumaquamarine"),
        ),
    )

    fig_bar.update_layout(
        title="Daily Distance (km)",
        yaxis_title="KM",
        xaxis_title="Date",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )

    st.plotly_chart(fig_bar, use_container_width=True, key="distance_chart_daily")

    # ---------- 📈 Pace Line Chart ----------
    fig_line = go.Figure()
    fig_line.add_trace(
        go.Scatter(
            x=pace_data["Date"],
            y=pace_data["Pace_Mins"],
            mode="lines+markers+text",
            text=pace_labels,
            textposition="top center",
            name="Pace",
            line=dict(color="#986868", width=2),
            marker=dict(size=5, line=dict(width=2, color="crimson")),
        )
    )
    fig_line.update_layout(
        title="Daily Average Pace (min/km)",
        yaxis_title="Pace (min/km)",
        xaxis_title="Date",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )
    fig_line.update_yaxes(autorange="reversed")

    st.plotly_chart(fig_line, use_container_width=True, key="pace_chart_daily")

    # ---------- 📉 Cadence Area Chart ----------
    fig_area = go.Figure()
    fig_area.add_trace(
        go.Scatter(
            x=cadence_data["Date"],
            y=cadence_data["Cadence (steps/min)"],
            mode="lines+markers+text",
            fill="tozeroy",
            text=cadence_labels,
            textposition="top center",
            name="Cadence",
            line=dict(color="royalblue", width=2),
            marker=dict(size=6),
        )
    )
    fig_area.update_layout(
        title="Daily Average Cadence (spm)",
        yaxis_title="Steps per Minute",
        xaxis_title="Date",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False,
    )
    st.plotly_chart(fig_area, use_container_width=True, key="cadence_chart_daily")
