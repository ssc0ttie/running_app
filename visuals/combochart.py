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

    # for plotting
    pace_data["Pace"] = pd.to_timedelta(pace_data["Pace"], errors="coerce")
    pace_data["Pace_Mins"] = pace_data["Pace"].dt.total_seconds() / 60

    pace_data["Pace_Str"] = pace_data["Pace"].apply(
        lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    )

    # Calculate week-over-week percent change for Distance and Pace
    dist_data["Distance_Pct_Change"] = dist_data["Distance"].pct_change() * 100
    pace_data["Pace_Pct_Change"] = pace_data["Pace_Mins"].pct_change() * 100

    # Create delta labels with colored arrows (Unicode) and % with 1 decimal
    def format_delta(val):
        if pd.isna(val):
            return ""
        arrow = "<span style='color:green'>&#9650;</span>" if val > 0 else "🔻"
        color = "green" if val > 0 else "red"
        return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    dist_data["Distance_Pct_Change_Label"] = dist_data["Distance_Pct_Change"].apply(
        format_delta
    )
    pace_data["Pace_Pct_Change_Label"] = pace_data["Pace_Pct_Change"].apply(
        format_delta
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
            marker=dict(size=5, line=dict(width=2, color="crimson")),
        ),
    )

    # Add line chart for Pace % change (secondary y axis)
    fig.add_trace(
        go.Scatter(
            x=dist_data["Week"],
            y=pace_data["Pace_Mins"] + 0.5,  # position slightly above pace points
            mode="text",
            text=dist_data["Distance_Pct_Change_Label"],
            textposition="bottom center",
            showlegend=False,
            yaxis="y2",
            hoverinfo="skip",
        )
    )

    # Add second y-axis for Pace
    # fig.update_layout(title="Distance x Pace")
    fig.update_xaxes(title_text="Week")
    fig.update_yaxes(title_text="KMS", secondary_y=False)
    fig.update_yaxes(title_text="Pace (min/km)", secondary_y=True)
    fig.update_layout(
        autosize=True,
        width=380,  # for mobile
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=30),
    )
    st.plotly_chart(fig, use_container_width=True, key="combo_chart")


def generate_combo_daily(data):
    ##GROUP BY
    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]  # filter non running activity
    act_date_group = filtered_data.groupby("Date", as_index=False)
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
            x=dist_data["Date"],
            y=dist_data["Distance"],
            name="Distance (km)",
            text=dist_data["Distance"].astype(int),
            marker=dict(color="mediumaquamarine"),
        )
    )

    # Add line chart for Pace
    fig.add_trace(
        go.Scatter(
            x=dist_data["Date"],
            y=pace_data["Pace_Mins"],
            name="Pace (min/km)",
            yaxis="y2",
            text=pace_data["Pace_Str"].astype(str),
            textposition="top center",
            mode="lines+markers+text",
            marker=dict(size=5, line=dict(width=2, color="crimson")),
        ),
    )

    # Add second y-axis for Pace
    # fig.update_layout(title="Distance x Pace")
    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text="KMS", secondary_y=False)
    fig.update_yaxes(title_text="Pace (min/km)", secondary_y=True)
    fig.update_layout(
        autosize=True,
        width=380,  # for mobile
        height=300,
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=30),
    )
    st.plotly_chart(fig, use_container_width=True, key="combo_chart_daily")
