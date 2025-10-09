import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_combo(data):
    # ----Activity Filter ---#

    activity = sorted(data["Activity"].dropna().unique())
    activity.insert(0, "All")
    selected_activity = st.multiselect("Select Activity(s)", activity, default=["All"])

    if not selected_activity or "All" in selected_activity:
        data = data
    else:
        data = data[data["Activity"].isin(selected_activity)]

    nonrun_data = data
    nonrun_data["Week"] = [week[:1] + week[-2:] for week in data["Week"]]

    ##GROUP BY
    data["Week"] = [
        week[:1] + week[-2:] for week in data["Week"]
    ]  # shorten weekname before groupby

    data = data[data["Distance"].notnull() & (data["Distance"] > 0)]

    data["Pace"] = pd.to_timedelta(data["Pace"], errors="coerce")
    data["Cadence (steps/min)"] = pd.to_numeric(
        data["Cadence (steps/min)"], errors="coerce"
    )
    data["HR (bpm)"] = pd.to_numeric(data["HR (bpm)"], errors="coerce")

    nonrun_data["Duration_Other"] = pd.to_timedelta(
        nonrun_data["Duration_Other"], errors="coerce"
    )
    filtered_data = data[
        ~data["Activity"].isin(
            ["Rest", "Cross Train", "Strength Training", "WeightTraining", 0]
        )
    ]  # filter non running activity

    ##NON- RUNNING ACITIVY###

    # data_others["Week"] = data_others["Week"].str.extract(r"(\d+)").astype(int)
    # data_others["Week"] = "Week " + data_others["Week"].astype(str).str.zfill(2)

    nonrun_filtered_data = nonrun_data[
        nonrun_data["Activity"].isin(
            [
                "Rest",
                "Cross Train",
                "Strength Training",
                "Yoga",
                "Pilates",
                "WeightTraining",
            ]
        )
    ]  # filter non running activity

    nonrun_data = nonrun_filtered_data.groupby(["Week", "Activity"], as_index=False)[
        "Duration_Other"
    ].sum()

    act_date_group = filtered_data.groupby("Week", as_index=False)
    dist_data = act_date_group["Distance"].sum()
    pace_data = act_date_group["Pace"].mean()
    cadence_data = act_date_group["Cadence (steps/min)"].mean()
    hr_data = act_date_group["HR (bpm)"].mean()

    # nonrun_data = nonrun_act_date_group["Duration_Other"].sum()

    # Convert Duration_Other to minutes
    nonrun_data["Duration_Other"] = pd.to_timedelta(
        nonrun_data["Duration_Other"], errors="coerce"
    )
    nonrun_data["Duration_Other_Mins"] = (
        nonrun_data["Duration_Other"].dt.total_seconds() / 60
    )

    # Format duration as mm:ss
    nonrun_data["Duration_Other_Str"] = nonrun_data["Duration_Other"].apply(
        lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    )

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
    nonrun_data["Duration_Pct_Change"] = (
        nonrun_data["Duration_Other"].pct_change() * 100
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
    hr_data["HR_Pct_Change_Label"] = hr_data["HR_Pct_Change"].apply(format_delta)

    nonrun_data["Duration_Pct_Change_Label"] = nonrun_data["Duration_Pct_Change"].apply(
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
    hr_labels = (
        hr_data["HR (bpm)"].round(1).astype(str)
        + " bpm<br>"
        + hr_data["HR_Pct_Change_Label"]
    )

    nonrun_labels = (
        nonrun_data["Duration_Other"].round(1).astype(str)
        + " spm<br>"
        + nonrun_data["Duration_Pct_Change_Label"]
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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",  # Removes Y-axis title
        ),
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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",  # Removes Y-axis title
        ),
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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",  # Removes Y-axis title
        ),
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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",
            range=[110, 190],  # Removes Y-axis title
        ),
        height=450,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig_bullet, use_container_width=True, key="hr_chart")


def generate_combo_supplimentary(data):
    # ----Activity Filter ---#

    activity = sorted(data["Activity"].dropna().unique())
    activity.insert(0, "All")

    nonrun_data = data
    nonrun_data["Week"] = [week[:1] + week[-2:] for week in data["Week"]]

    ##GROUP BY
    data["Week"] = [
        week[:1] + week[-2:] for week in data["Week"]
    ]  # shorten weekname before groupby

    nonrun_data["Duration_Other"] = pd.to_timedelta(
        nonrun_data["Duration_Other"], errors="coerce"
    )

    ##NON- RUNNING ACITIVY###

    nonrun_data = nonrun_data.groupby(["Week", "Activity"], as_index=False)[
        "Duration_Other"
    ].sum()

    # Convert Duration_Other to minutes
    nonrun_data["Duration_Other"] = pd.to_timedelta(
        nonrun_data["Duration_Other"], errors="coerce"
    )
    nonrun_data["Duration_Other_Mins"] = (
        nonrun_data["Duration_Other"].dt.total_seconds() / 60
    )

    # Format duration as mm:ss
    nonrun_data["Duration_Other_Str"] = nonrun_data["Duration_Other"].apply(
        lambda td: f"{int(td.total_seconds() // 3600):01d}h {int((td.total_seconds() % 3600) // 60):02d}m"
    )
    nonrun_data["Duration_Pct_Change"] = (
        nonrun_data["Duration_Other"].pct_change() * 100
    )

    weekly_totals = nonrun_data.groupby("Week")["Duration_Other"].sum()
    weekly_totals_mins = weekly_totals.dt.total_seconds() / 60
    weekly_totals_str = weekly_totals.apply(
        lambda td: f"{int(td.total_seconds() // 3600):01d}h {int((td.total_seconds() % 3600) // 60):02d}m"
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

    nonrun_data["Duration_Pct_Change_Label"] = nonrun_data["Duration_Pct_Change"].apply(
        format_delta
    )

    # Combine labels

    nonrun_labels = (
        nonrun_data["Duration_Other"].round(1).astype(str)
        + " spm<br>"
        + nonrun_data["Duration_Pct_Change_Label"]
    )

    # Add stack bar chart for nonrun activity
    fig_bar = go.Figure()
    # Loop through each activity and add a trace
    for activity in nonrun_data["Activity"].unique():
        subset = nonrun_data[nonrun_data["Activity"] == activity]
        fig_bar.add_trace(
            go.Bar(
                x=subset["Week"],
                y=subset["Duration_Other_Mins"],
                name=activity,
                text=subset["Duration_Other_Str"],
                textposition="auto",
            )
        )

    fig_bar.update_xaxes(
        categoryorder="array", categoryarray=sorted(nonrun_data["Week"].unique())
    )

    fig_bar.update_layout(
        title="Weekly Duration Supplimentary Activity",
        xaxis_title="Week",
        yaxis_title="Duration (Mins)",
        barmode="stack",  # key for stacking
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,  # show legend for activity breakdown
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    fig_bar.add_trace(
        go.Scatter(
            x=weekly_totals.index,
            y=weekly_totals_mins,
            text=weekly_totals_str,
            mode="text",
            textposition="top center",
            showlegend=False,
            textfont=dict(size=14, color="black"),
        )
    )

    st.plotly_chart(fig_bar, use_container_width=True, key="nonrun_chart_2")


def generate_combo_daily(data):

    # ----Activity Filter ---#

    activity = sorted(data["Activity"].dropna().unique())
    activity.insert(0, "All")
    selected_activity = st.multiselect(
        "Select Activity(s)", activity, default=["All"], key="user_selector_daily"
    )

    if not selected_activity or "All" in selected_activity:
        data = data
    else:
        data = data[data["Activity"].isin(selected_activity)]

    ##GROUP BY
    data = data[
        data["Distance"].notnull() & (data["Distance"] > 0) & data["Date"].notnull()
    ]

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
    dist_data["Date_Label"] = dist_data["Date"].dt.strftime("%d %b %a")

    pace_data = act_date_group["Pace"].mean()
    pace_data["Date_Label"] = pace_data["Date"].dt.strftime("%d %b %a")

    cadence_data = act_date_group["Cadence (steps/min)"].mean()
    cadence_data["Date_Label"] = cadence_data["Date"].dt.strftime("%d %b %a")

    hr_data = act_date_group["HR (bpm)"].mean()
    hr_data["Date_Label"] = hr_data["Date"].dt.strftime("%d %b %a")

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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",  # Removes Y-axis title
        ),
        # xaxis_title="Date",
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=dist_data["Date"],
            ticktext=dist_data["Date_Label"],
        ),
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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",  # Removes Y-axis title
        ),
        xaxis_title="Date",
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=pace_data["Date"],
            ticktext=pace_data["Date_Label"],
        ),
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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",  # Removes Y-axis title
        ),
        xaxis_title="Date",
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=cadence_data["Date"],
            ticktext=cadence_data["Date_Label"],
        ),
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
        yaxis=dict(
            showticklabels=False,
            ticks="",
            showgrid=False,
            title="",
            range=[110, 190],  # Removes Y-axis title
        ),
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=hr_data["Date"],
            ticktext=hr_data["Date_Label"],
        ),
        height=450,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    st.plotly_chart(fig_bullet, use_container_width=True, key="hr_chart_2")


def generate_combo_supplimentary_run(data):
    # ----Activity Filter ---#

    activity = sorted(data["Activity"].dropna().unique())
    activity.insert(0, "All")

    nonrun_data = data
    nonrun_data["Week"] = [week[:1] + week[-2:] for week in data["Week"]]

    ##GROUP BY
    data["Week"] = [
        week[:1] + week[-2:] for week in data["Week"]
    ]  # shorten weekname before groupby

    nonrun_data["Duration_Other"] = pd.to_timedelta(
        nonrun_data["Duration_Other"], errors="coerce"
    )

    ##NON- RUNNING ACITIVY###

    nonrun_data = nonrun_data.groupby(["Week", "Activity"], as_index=False)[
        "Duration_Other"
    ].sum()

    # Convert Duration_Other to minutes
    nonrun_data["Duration_Other"] = pd.to_timedelta(
        nonrun_data["Duration_Other"], errors="coerce"
    )
    nonrun_data["Duration_Other_Mins"] = (
        nonrun_data["Duration_Other"].dt.total_seconds() / 60
    )

    # Format duration as mm:ss
    nonrun_data["Duration_Other_Str"] = nonrun_data["Duration_Other"].apply(
        lambda td: f"{int(td.total_seconds() // 3600):01d}h {int((td.total_seconds() % 3600) // 60):02d}m"
    )
    nonrun_data["Duration_Pct_Change"] = (
        nonrun_data["Duration_Other"].pct_change() * 100
    )

    weekly_totals = nonrun_data.groupby("Week")["Duration_Other"].sum()
    weekly_totals_mins = weekly_totals.dt.total_seconds() / 60
    weekly_totals_str = weekly_totals.apply(
        lambda td: f"{int(td.total_seconds() // 3600):01d}h {int((td.total_seconds() % 3600) // 60):02d}m"
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

    nonrun_data["Duration_Pct_Change_Label"] = nonrun_data["Duration_Pct_Change"].apply(
        format_delta
    )

    # Combine labels

    nonrun_labels = (
        nonrun_data["Duration_Other"].round(1).astype(str)
        + " spm<br>"
        + nonrun_data["Duration_Pct_Change_Label"]
    )

    # Add stack bar chart for nonrun activity
    fig_bar = go.Figure()
    # Loop through each activity and add a trace
    for activity in nonrun_data["Activity"].unique():
        subset = nonrun_data[nonrun_data["Activity"] == activity]
        fig_bar.add_trace(
            go.Bar(
                x=subset["Week"],
                y=subset["Duration_Other_Mins"],
                name=activity,
                text=subset["Duration_Other_Str"],
                textposition="auto",
            )
        )

    fig_bar.update_xaxes(
        categoryorder="array", categoryarray=sorted(nonrun_data["Week"].unique())
    )

    fig_bar.update_layout(
        title="Weekly Duration Runs",
        xaxis_title="Week",
        yaxis_title="Duration (Mins)",
        barmode="stack",  # key for stacking
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,  # show legend for activity breakdown
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    fig_bar.add_trace(
        go.Scatter(
            x=weekly_totals.index,
            y=weekly_totals_mins,
            text=weekly_totals_str,
            mode="text",
            textposition="top center",
            showlegend=False,
            textfont=dict(size=14, color="black"),
        )
    )

    st.plotly_chart(fig_bar, use_container_width=True, key="run_chart_2")
