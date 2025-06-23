import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_combo(data):
    ##GROUP BY
    data = data[data["Distance"].notnull() & (data["Distance"] > 0)]

    data["Pace"] = pd.to_timedelta(data["Pace"], errors="coerce")
    data["Cadence (steps/min)"] = pd.to_numeric(
        data["Cadence (steps/min)"], errors="coerce"
    )
    data["HR (bpm)"] = pd.to_numeric(data["HR (bpm)"], errors="coerce")

    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]  # filter non running activity
    act_date_group = filtered_data.groupby("Week", as_index=False)
    dist_data = act_date_group["Distance"].sum()
    pace_data = act_date_group["Pace"].mean()
    cadence_data = act_date_group["Cadence (steps/min)"].mean()
    hr_data = act_date_group["HR (bpm)"].mean()

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
    hr_data["HR_Pct_Change"] = hr_data["HR (bpm)"].pct_change() * 100

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
    hr_data["HR_Pct_Change_Label"] = hr_data["HR_Pct_Change"].apply(format_delta)

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
    hr_labels = (
        hr_data["HR (bpm)"].round(1).astype(str)
        + " bpm<br>"
        + hr_data["HR_Pct_Change_Label"]
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

    fig_area.update_yaxes(range=[120, cadence_data["Cadence (steps/min)"].max() + 30])
    st.plotly_chart(fig_area, use_container_width=True, key="cadence_chart")

    # ---------- 📉 HR  Chart ----------

    # Sample data
    weeks = hr_data["Week"]
    avg_hr = hr_data["HR (bpm)"]

    # Heart rate zone boundaries
    zones = [
        {"name": "Zone 1: Easy", "start": 110, "end": 129, "color": "#A3A8A3"},  # Green
        {
            "name": "Zone 2: Steady",
            "start": 130,
            "end": 150,
            "color": "#7FFF00",
        },  # Yellow-Green
        {
            "name": "Zone 3: Mid Hard",
            "start": 151,
            "end": 164,
            "color": "#FFFF00",
        },  # Yellow
        {
            "name": "Zone 4: Hard",
            "start": 165,
            "end": 175,
            "color": "#FFA500",
        },  # Orange
        {
            "name": "Zone 5: V. Hard",
            "start": 176,
            "end": 187,
            "color": "#FF0000",
        },  # Red
    ]

    fig_bullet = go.Figure()

    # Draw stacked HR zones for each week
    for zone in zones:
        fig_bullet.add_trace(
            go.Bar(
                x=weeks,
                y=[zone["end"] - zone["start"]] * len(weeks),
                base=[zone["start"]] * len(weeks),
                name=zone["name"],
                marker_color=zone["color"],
                # width=0.6,
                hoverinfo="skip",
                opacity=0.6,
            )
        )

        # Overlay the actual HR value as a thin black bar
    fig_bullet.add_trace(
        go.Bar(
            x=weeks,
            y=avg_hr,  # Directly use avg_hr as bar height
            name="Avg HR",
            marker=dict(
                color="rgba(65, 105, 225, 0.6)",
                line=dict(
                    color="rgba(112, 128, 144, 0.6)", width=3
                ),  # Adjust border width and color
            ),
            # width=0.4,
            text=hr_labels,
            textposition="outside",
            textfont=dict(size=14),
            hovertemplate="Week: %{x}<br>Avg HR: %{y} bpm",
        )
    )

    fig_bullet.update_layout(
        barmode="overlay",  # overlay to show thin bar on top
        title="Weekly Avg Heart Rate vs HR Zones",
        xaxis_title="Week",
        yaxis_title="Heart Rate (bpm)",
        yaxis=dict(range=[110, 190]),  # 👈 Set axis limits
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig_bullet, use_container_width=True, key="hr_chart")


def generate_combo_daily(data):
    #     ##GROUP BY
    #     data["Pace"] = pd.to_timedelta(data["Pace"], errors="coerce")
    #     data["Cadence (steps/min)"] = pd.to_numeric(
    #         data["Cadence (steps/min)"], errors="coerce"
    #     )
    #     filtered_data = data[
    #         ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    #     ]  # filter non running activity
    #     act_date_group = filtered_data.groupby("Date", as_index=False)
    #     dist_data = act_date_group["Distance"].sum()
    #     hr_data = act_date_group["HR (bpm)"].mean()
    #     pace_data = act_date_group["Pace"].mean()
    #     cadence_data = act_date_group["Cadence (steps/min)"].mean()

    #     # Convert pace to minutes
    #     pace_data["Pace"] = pd.to_timedelta(pace_data["Pace"], errors="coerce")
    #     pace_data["Pace_Mins"] = pace_data["Pace"].dt.total_seconds() / 60

    #     # Format pace as mm:ss
    #     pace_data["Pace_Str"] = pace_data["Pace"].apply(
    #         lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    #     )

    #     # Calculate Date-over-Date percent change for Distance, Cadence and Pace
    #     dist_data["Distance_Pct_Change"] = dist_data["Distance"].pct_change() * 100
    #     pace_data["Pace_Pct_Change"] = pace_data["Pace_Mins"].pct_change() * 100
    #     cadence_data["Cadence_Pct_Change"] = (
    #         cadence_data["Cadence (steps/min)"].pct_change() * 100
    #     )

    #     #  Create delta labels
    #     def format_delta(val):
    #         if pd.isna(val):
    #             return ""
    #         arrow = "<span style='color:green'>&#9650;</span>" if val > 0 else "🔻"
    #         color = "green" if val > 0 else "red"
    #         return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    #     def format_delta_rev(val):
    #         if pd.isna(val):
    #             return ""
    #         arrow = "🔻" if val > 0 else "<span style='color:green'>&#9650;</span>"
    #         color = "red" if val > 0 else "green"
    #         return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    #     dist_data["Distance_Pct_Change_Label"] = dist_data["Distance_Pct_Change"].apply(
    #         format_delta
    #     )
    #     pace_data["Pace_Pct_Change_Label"] = pace_data["Pace_Pct_Change"].apply(
    #         format_delta_rev
    #     )
    #     cadence_data["Cadence_Pct_Change_Label"] = cadence_data["Cadence_Pct_Change"].apply(
    #         format_delta
    #     )

    #     # Combine labels
    #     dist_labels = (
    #         dist_data["Distance"].round(1).astype(str)
    #         + " km<br>"
    #         + dist_data["Distance_Pct_Change_Label"]
    #     )
    #     pace_labels = pace_data["Pace_Str"] + "<br>" + pace_data["Pace_Pct_Change_Label"]
    #     cadence_labels = (
    #         cadence_data["Cadence (steps/min)"].round(1).astype(str)
    #         + " spm<br>"
    #         + cadence_data["Cadence_Pct_Change_Label"]
    #     )

    #     # Create combo plot
    #     fig = make_subplots(specs=[[{"secondary_y": True}]])

    #     # Add bar chart for Distance
    #     fig_bar = go.Figure()
    #     fig_bar.add_trace(
    #         go.Bar(
    #             x=dist_data["Date"],
    #             y=dist_data["Distance"],
    #             name="Distance (km)",
    #             text=dist_labels,
    #             textposition="auto",
    #             marker=dict(color="mediumaquamarine"),
    #         ),
    #     )

    #     fig_bar.update_layout(
    #         title="Daily Distance (km)",
    #         yaxis_title="KM",
    #         xaxis_title="Date",
    #         height=400,
    #         margin=dict(l=20, r=20, t=40, b=20),
    #         showlegend=False,
    #     )

    #     st.plotly_chart(fig_bar, use_container_width=True, key="distance_chart_daily")

    #     # ---------- 📈 Pace Line Chart ----------
    #     fig_line = go.Figure()
    #     fig_line.add_trace(
    #         go.Scatter(
    #             x=pace_data["Date"],
    #             y=pace_data["Pace_Mins"],
    #             mode="lines+markers+text",
    #             text=pace_labels,
    #             textposition="top center",
    #             name="Pace",
    #             line=dict(color="#986868", width=2),
    #             marker=dict(size=5, line=dict(width=2, color="crimson")),
    #         )
    #     )
    #     fig_line.update_layout(
    #         title="Daily Average Pace (min/km)",
    #         yaxis_title="Pace (min/km)",
    #         xaxis_title="Date",
    #         height=400,
    #         margin=dict(l=20, r=20, t=40, b=20),
    #         showlegend=False,
    #     )
    #     fig_line.update_yaxes(autorange="reversed")

    #     st.plotly_chart(fig_line, use_container_width=True, key="pace_chart_daily")

    #     # ---------- 📉 Cadence Area Chart ----------
    #     fig_area = go.Figure()
    #     fig_area.add_trace(
    #         go.Scatter(
    #             x=cadence_data["Date"],
    #             y=cadence_data["Cadence (steps/min)"],
    #             mode="lines+markers+text",
    #             fill="tozeroy",
    #             text=cadence_labels,
    #             textposition="top center",
    #             name="Cadence",
    #             line=dict(color="royalblue", width=2),
    #             marker=dict(size=6),
    #         )
    #     )
    #     fig_area.update_layout(
    #         title="Daily Average Cadence (spm)",
    #         yaxis_title="Steps per Minute",
    #         xaxis_title="Date",
    #         height=400,
    #         margin=dict(l=20, r=20, t=40, b=20),
    #         showlegend=False,
    #     )
    #     fig_area.update_yaxes(range=[120, cadence_data["Cadence (steps/min)"].max() + 30])
    #     st.plotly_chart(fig_area, use_container_width=True, key="cadence_chart_daily")
    ##GROUP BY
    data = data[data["Distance"].notnull() & (data["Distance"] > 0)]
    data["Pace"] = pd.to_timedelta(data["Pace"], errors="coerce")
    data["Cadence (steps/min)"] = pd.to_numeric(
        data["Cadence (steps/min)"], errors="coerce"
    )
    data["HR (bpm)"] = pd.to_numeric(data["HR (bpm)"], errors="coerce")

    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]  # filter non running activity
    act_date_group = filtered_data.groupby("Date", as_index=False)
    dist_data = act_date_group["Distance"].sum()
    pace_data = act_date_group["Pace"].mean()
    cadence_data = act_date_group["Cadence (steps/min)"].mean()
    hr_data = act_date_group["HR (bpm)"].mean()

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
    hr_data["HR_Pct_Change"] = hr_data["HR (bpm)"].pct_change() * 100

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
    hr_data["HR_Pct_Change_Label"] = hr_data["HR_Pct_Change"].apply(format_delta)

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
    hr_labels = (
        hr_data["HR (bpm)"].round(1).astype(str)
        + " bpm<br>"
        + hr_data["HR_Pct_Change_Label"]
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

    st.plotly_chart(fig_bar, use_container_width=True, key="distance_chart_2")

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

    st.plotly_chart(fig_line, use_container_width=True, key="pace_chart_2")

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

    fig_area.update_yaxes(range=[120, cadence_data["Cadence (steps/min)"].max() + 30])
    st.plotly_chart(fig_area, use_container_width=True, key="cadence_chart_2")

    # ---------- 📉 HR  Chart ----------

    # Sample data
    weeks = hr_data["Date"]
    avg_hr = hr_data["HR (bpm)"]

    # Heart rate zone boundaries
    zones = [
        {"name": "Zone 1: Easy", "start": 110, "end": 129, "color": "#A3A8A3"},  # Green
        {
            "name": "Zone 2: Steady",
            "start": 130,
            "end": 150,
            "color": "#7FFF00",
        },  # Yellow-Green
        {
            "name": "Zone 3: Mid Hard",
            "start": 151,
            "end": 164,
            "color": "#FFFF00",
        },  # Yellow
        {
            "name": "Zone 4: Hard",
            "start": 165,
            "end": 175,
            "color": "#FFA500",
        },  # Orange
        {
            "name": "Zone 5: V. Hard",
            "start": 176,
            "end": 187,
            "color": "#FF0000",
        },  # Red
    ]

    fig_bullet = go.Figure()

    # Draw stacked HR zones for each week
    for zone in zones:
        fig_bullet.add_trace(
            go.Bar(
                x=weeks,
                y=[zone["end"] - zone["start"]] * len(weeks),
                base=[zone["start"]] * len(weeks),
                name=zone["name"],
                marker_color=zone["color"],
                # width=0.6,
                hoverinfo="skip",
                opacity=0.8,
            )
        )

        # Overlay the actual HR value as a thin black bar
    fig_bullet.add_trace(
        go.Bar(
            x=weeks,
            y=avg_hr,  # Directly use avg_hr as bar height
            name="Avg HR",
            marker=dict(
                color="rgba(65, 105, 225, 0.6)",
                line=dict(
                    color="rgba(112, 128, 144, 0.6)", width=3
                ),  # Adjust border width and color
            ),
            # opacity=0.6,
            # width=0.4,
            text=hr_labels,
            textposition="outside",
            textfont=dict(size=14),
            hovertemplate="Date: %{x}<br>Avg HR: %{y} bpm",
        )
    )

    fig_bullet.update_layout(
        barmode="overlay",  # overlay to show thin bar on top
        title="Daily Avg Heart Rate vs HR Zones",
        xaxis_title="Date",
        yaxis_title="Heart Rate (bpm)",
        yaxis=dict(range=[110, 190]),  # 👈 Set axis limits
        height=450,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig_bullet, use_container_width=True, key="hr_chart_2")
