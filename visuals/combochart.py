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
    # nonrun_data["Week"] = [week[:1] + week[-2:] for week in data["Week"]]

    # ##GROUP BY
    # data["Week"] = [
    #     week[:1] + week[-2:] for week in data["Week"]
    # ]  # shorten weekname before groupby

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
    filtered_data = filtered_data.sort_values(by="Date_of_Activity")

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
    # dist_data = df.sort_values(by="")

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
        + nonrun_data["Duration_Pct_Change_Label"].astype(str)
    )
    # # Create combo plot
    # fig = make_subplots(specs=[[{"secondary_y": True}]])

    # # Add bar chart for Distance
    # fig_bar = go.Figure()
    # fig_bar.add_trace(
    #     go.Bar(
    #         x=dist_data["Week"],
    #         y=dist_data["Distance"],
    #         name="Distance (km)",
    #         text=dist_labels,
    #         textposition="auto",
    #         marker=dict(color="#f3d2b2"),  # earthy clay — was "mediumaquamarine"
    #     ),
    # )
    # # Add bar chart for Distance
    # fig_bar.update_layout(
    #     title="Weekly Distance (km)",
    #     title_font=dict(color="#2b2b2b"),
    #     plot_bgcolor="#faf7f2",  # soft paper background
    #     paper_bgcolor="#faf7f2",
    #     yaxis=dict(
    #         showticklabels=False,
    #         ticks="",
    #         showgrid=False,
    #         title="",
    #         gridcolor="#efe6dc",  # faint trail color for any grid
    #     ),
    #     xaxis_title="Week",
    #     xaxis=dict(
    #         title_font=dict(color="#2b2b2b"),
    #         tickfont=dict(color="#4a3729"),
    #     ),
    #     height=400,
    #     margin=dict(l=20, r=20, t=40, b=20),
    #     showlegend=False,
    # )

    # st.plotly_chart(fig_bar, use_container_width=True, key="distance_chart")

    # # ==============================================
    # # CHART 1: STACKED BAR CHART (Absolute Values)
    # # ==============================================

    # # Group data by Week and Activity to get distances per activity per week
    # stacked_data = filtered_data.groupby(["Week", "Activity"], as_index=False)[
    #     "Distance"
    # ].sum()

    # # Get unique weeks in order
    # weeks_order = sorted(stacked_data["Week"].unique())

    # # Get unique activities
    # activities = stacked_data["Activity"].unique()

    # # Create a color palette for activities
    # colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel

    # # Create the stacked bar chart
    # fig_stacked = go.Figure()

    # # Loop through each activity and add a trace
    # for i, activity_name in enumerate(activities):
    #     subset = stacked_data[stacked_data["Activity"] == activity_name]

    #     fig_stacked.add_trace(
    #         go.Bar(
    #             x=subset["Week"],
    #             y=subset["Distance"],
    #             name=activity_name,
    #             text=subset["Distance"].round(1),
    #             textposition="inside",
    #             textfont=dict(size=10, color="white"),
    #             marker_color=colors[i % len(colors)],
    #             hovertemplate=(
    #                 f"<b>{activity_name}</b><br>"
    #                 + "Week: %{x}<br>"
    #                 + "Distance: %{y:.1f} km<br>"
    #                 + "<extra></extra>"
    #             ),
    #         )
    #     )

    # # Calculate total distance per week for labels
    # week_totals = stacked_data.groupby("Week")["Distance"].sum().reset_index()
    # week_totals.columns = ["Week", "Total_Distance"]

    # # Update x-axis to maintain week order
    # fig_stacked.update_xaxes(categoryorder="array", categoryarray=weeks_order)

    # fig_stacked.update_layout(
    #     title="<b>Weekly Running Distance by Activity</b><br><sub>Stacked bars show distance per activity type</sub>",
    #     title_font=dict(color="#2b2b2b", size=16),
    #     plot_bgcolor="#faf7f2",
    #     paper_bgcolor="#faf7f2",
    #     xaxis_title="Week",
    #     xaxis=dict(
    #         title_font=dict(color="#2b2b2b", size=12),
    #         tickfont=dict(color="#4a3729"),
    #         gridcolor="#efe6dc",
    #         gridwidth=1,
    #     ),
    #     yaxis_title="Distance (km)",
    #     yaxis=dict(
    #         title_font=dict(color="#2b2b2b", size=12),
    #         gridcolor="#efe6dc",
    #         gridwidth=1,
    #     ),
    #     barmode="stack",
    #     height=500,
    #     margin=dict(l=20, r=20, t=60, b=20),
    #     showlegend=True,
    #     legend=dict(
    #         orientation="h",
    #         yanchor="bottom",
    #         y=1.02,
    #         xanchor="right",
    #         x=1,
    #         font=dict(color="#2b2b2b", size=10),
    #         bgcolor="rgba(255, 255, 255, 0.8)",
    #     ),
    # )

    # # Add total distance labels on top of each stack
    # fig_stacked.add_trace(
    #     go.Scatter(
    #         x=week_totals["Week"],
    #         y=week_totals["Total_Distance"],
    #         text=[f"<b>Total: {d:.1f} km</b>" for d in week_totals["Total_Distance"]],
    #         mode="text",
    #         textposition="top center",
    #         showlegend=False,
    #         textfont=dict(size=11, color="#4a3729"),
    #         hoverinfo="skip",
    #     )
    # )

    # st.plotly_chart(fig_stacked, use_container_width=True, key="distance_stacked_chart")

    # Add a separator
    st.markdown("---")

    # ==============================================
    # SISYPHUS THEME COLOR PALETTE
    # ==============================================
    # MEDITERRANEAN MORNING THEME
    # GREEK ISLES THEME (Best balance of contrast & theme)
    sisyphus_colors = [
        "#E8956A",  # Sun-dried Terracotta 🧱
        "#4A9B9B",  # Aegean Blue 🌊
        "#F0B87A",  # Golden Honey 🍯
        "#6B9B6A",  # Olive Branch
        "#D4855A",  # Clay Pot 🏺
        "#5B8B8B",  # Deep Sea 🐟
        "#E8B08A",  # Beach Sand 🏖️
        "#4A8B6E",  # Cypress Tree 🌲
        "#D49A6A",  # Wheat Field 🌾
        "#8B9B6A",  # Faded Sage 🌿
    ]
    # ==============================================
    # CHART 1: STACKED BAR CHART (Absolute Values)
    # ==============================================

    stacked_data = filtered_data.groupby(["Week", "Activity"], as_index=False)[
        "Distance"
    ].sum()
    weeks_order = sorted(stacked_data["Week"].unique())
    activities = stacked_data["Activity"].unique()

    fig_stacked = go.Figure()

    for i, activity_name in enumerate(activities):
        subset = stacked_data[stacked_data["Activity"] == activity_name]

        fig_stacked.add_trace(
            go.Bar(
                x=subset["Week"],
                y=subset["Distance"],
                name=activity_name,
                text=subset["Distance"].round(1),
                textposition="inside",
                textfont=dict(
                    size=10, color="#FAF7F2"
                ),  # Light like sun-bleached stone
                marker_color=sisyphus_colors[i % len(sisyphus_colors)],
                hovertemplate=(
                    f"<b>{activity_name}</b><br>"
                    + "Week: %{x}<br>"
                    + "Distance: %{y:.1f} km<br>"
                    + "<extra></extra>"
                ),
            )
        )

    week_totals = stacked_data.groupby("Week")["Distance"].sum().reset_index()
    week_totals.columns = ["Week", "Total_Distance"]

    fig_stacked.update_xaxes(categoryorder="array", categoryarray=weeks_order)

    fig_stacked.update_layout(
        title="<b>Weekly Running Distance by Activity</b><br><sub>Stacked bars show distance per activity type</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        yaxis_title="Distance (km)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        barmode="stack",
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#2b2b2b", size=10),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )

    fig_stacked.add_trace(
        go.Scatter(
            x=week_totals["Week"],
            y=week_totals["Total_Distance"],
            text=[f"<b>Total: {d:.1f} km</b>" for d in week_totals["Total_Distance"]],
            mode="text",
            textposition="top center",
            showlegend=False,
            textfont=dict(size=11, color="#4a3729"),
            hoverinfo="skip",
        )
    )

    st.plotly_chart(fig_stacked, use_container_width=True, key="distance_stacked_chart")

    st.markdown("---")

    # ==============================================
    # CHART 2: PERCENTAGE STACKED BAR CHART
    # ==============================================

    percentage_data = filtered_data.groupby(["Week", "Activity"], as_index=False)[
        "Distance"
    ].sum()
    week_totals_pct = percentage_data.groupby("Week")["Distance"].sum().reset_index()
    week_totals_pct.columns = ["Week", "Total_Distance"]
    percentage_data = percentage_data.merge(week_totals_pct, on="Week")
    percentage_data["Percentage"] = (
        percentage_data["Distance"] / percentage_data["Total_Distance"]
    ) * 100

    fig_pct_stacked = go.Figure()

    for i, activity_name in enumerate(activities):
        subset = percentage_data[percentage_data["Activity"] == activity_name]

        fig_pct_stacked.add_trace(
            go.Bar(
                x=subset["Week"],
                y=subset["Percentage"],
                name=activity_name,
                text=subset["Percentage"].round(1).astype(str) + "%",
                textposition="inside",
                textfont=dict(size=10, color="#FAF7F2"),
                marker_color=sisyphus_colors[i % len(sisyphus_colors)],
                hovertemplate=(
                    f"<b>{activity_name}</b><br>"
                    + "Week: %{x}<br>"
                    + "Percentage: %{y:.1f}%<br>"
                    + "<extra></extra>"
                ),
            )
        )

    fig_pct_stacked.update_xaxes(categoryorder="array", categoryarray=weeks_order)

    fig_pct_stacked.update_layout(
        title="<b>Weekly Activity Distribution (%)</b><br><sub>How your training focus shifts week to week</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        yaxis_title="Percentage of Weekly Distance (%)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            gridcolor="#efe6dc",
            gridwidth=1,
            range=[0, 100],
            ticksuffix="%",
        ),
        barmode="stack",
        height=500,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#2b2b2b", size=10),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )

    st.plotly_chart(
        fig_pct_stacked, use_container_width=True, key="percentage_stacked_chart"
    )

    # ---------- 📈 Pace Line Chart ----------
    # Create total distance data for dual-axis if desired
    total_distance = filtered_data.groupby("Week")["Distance"].sum().reset_index()

    fig_line = go.Figure()

    # Add pace line
    fig_line.add_trace(
        go.Scatter(
            x=pace_data["Week"],
            y=pace_data["Pace_Mins"],
            mode="lines+markers+text",
            text=pace_labels,
            textposition="top center",
            name="Pace",
            line=dict(color="#6b4c3a", width=3),  # earthy brown
            marker=dict(
                size=8,
                color="#9b7b5c",  # earthy clay
                line=dict(width=2, color="#4a3729"),  # deep soil border
            ),
        )
    )

    fig_line.update_layout(
        title="<b>Weekly Average Pace</b><br><sub>Faster = better (lower is faster)</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",  # soft paper background
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        yaxis_title="Pace (min/km)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
            tickformat=".2f",  # Show as decimal minutes
        ),
        height=450,  # Slightly taller to match other charts
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
        hovermode="x unified",  # Better tooltip experience
    )

    # Reverse y-axis since lower pace is better
    fig_line.update_yaxes(autorange="reversed")

    # Add a horizontal line for goal pace (optional - customize as needed)
    # fig_line.add_hline(y=5.0, line_dash="dash", line_color="#c0a080", line_width=1.5, opacity=0.5)

    st.plotly_chart(fig_line, use_container_width=True, key="pace_chart")

    # Add a separator
    st.markdown("---")

    # ---------- 📈 Cadence Area Chart ----------
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
            line=dict(color="#6b4c3a", width=3),  # earthy brown
            marker=dict(
                size=8,
                color="#9b7b5c",  # earthy clay
                line=dict(width=1.5, color="#4a3729"),
            ),
            fillcolor="rgba(107, 76, 58, 0.15)",  # subtle boulder tint
        )
    )

    fig_area.update_layout(
        title="<b>Weekly Average Cadence</b><br><sub>Steps per minute - higher is typically more efficient</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        yaxis_title="Cadence (steps/min)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
            zeroline=False,
        ),
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
        hovermode="x unified",
    )

    # Set y-axis range with some padding
    cadence_min = cadence_data["Cadence (steps/min)"].min()
    cadence_max = cadence_data["Cadence (steps/min)"].max()
    padding = (cadence_max - cadence_min) * 0.1
    fig_area.update_yaxes(
        range=[
            max(120, cadence_min - padding),  # Don't go below 120
            cadence_max + padding,
        ]
    )

    # Add a reference line for optimal cadence (180 spm is often cited as ideal)
    fig_area.add_hline(
        y=180,
        line_dash="dash",
        line_color="#c0a080",
        line_width=1.5,
        opacity=0.6,
        annotation_text="Optimal (180 spm)",
        annotation_position="right",
        annotation_font_size=10,
    )

    st.plotly_chart(fig_area, use_container_width=True, key="cadence_chart")

    # ---------- 📉 HR Chart ----------

    # Sample data
    weeks = hr_data["Week"]
    avg_hr = hr_data["HR (bpm)"]

    # Your original HR zones with YOUR colors (preserved exactly)
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

    # Draw stacked HR zones (YOUR colors preserved)
    for zone in zones:
        fig_bullet.add_trace(
            go.Bar(
                x=weeks,
                y=[zone["end"] - zone["start"]] * len(weeks),
                base=[zone["start"]] * len(weeks),
                name=zone["name"],
                marker_color=zone["color"],  # Your original colors
                hoverinfo="skip",
                opacity=0.5,
            )
        )

    # Overlay actual HR values
    fig_bullet.add_trace(
        go.Bar(
            x=weeks,
            y=avg_hr,
            name="Avg HR",
            marker=dict(
                color="rgba(107, 76, 58, 0.7)",  # boulder with opacity
                line=dict(color="#4a3729", width=2),  # deep soil border
            ),
            text=hr_labels,
            textposition="outside",
            textfont=dict(size=12, color="#4a3729"),  # Slightly reduced for consistency
            hovertemplate="Week: %{x}<br>Avg HR: %{y} bpm<br><extra></extra>",
        )
    )

    fig_bullet.update_layout(
        barmode="overlay",
        title="<b>Weekly Average Heart Rate vs HR Zones</b><br><sub>Track which zone you're training in</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        yaxis_title="Heart Rate (bpm)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
            range=[100, 195],  # Slightly extended for better visibility
            ticks="outside",
            tickmode="linear",
            tick0=100,
            dtick=10,
        ),
        height=450,  # Match other charts
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,  # Keep legend off for cleaner look
        hovermode="x unified",
    )

    # Optional: Add a subtle legend that appears on hover (uncomment if desired)
    fig_bullet.update_layout(
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#2b2b2b", size=10),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )

    st.plotly_chart(fig_bullet, use_container_width=True, key="hr_chart")


def generate_combo_supplimentary(data):
    # ----Activity Filter ---#

    st.markdown("---")

    activity = sorted(data["Activity"].dropna().unique())
    activity.insert(0, "All")

    nonrun_data = data
    # nonrun_data["Week"] = [week[:1] + week[-2:] for week in data["Week"]]

    # ##GROUP BY
    # data["Week"] = [
    #     week[:1] + week[-2:] for week in data["Week"]
    # ]  # shorten weekname before groupby

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
        title="Weekly Duration Supplementary Activity",
        title_font=dict(color="#2b2b2b"),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b"),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
        ),
        yaxis_title="Duration (Mins)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b"),
            gridcolor="#efe6dc",
        ),
        barmode="stack",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#2b2b2b"),
        ),
    )

    # Add total duration labels
    fig_bar.add_trace(
        go.Scatter(
            x=weekly_totals.index,
            y=weekly_totals_mins,
            text=weekly_totals_str,
            mode="text",
            textposition="top center",
            showlegend=False,
            textfont=dict(size=14, color="#4a3729"),
        )
    )
    st.plotly_chart(fig_bar, use_container_width=True, key="nonrun_chart_2")


def generate_combo_supplimentary_new(data):

    sisyphus_colors = [
        "#E8956A",  # Sun-dried Terracotta 🧱
        "#4A9B9B",  # Aegean Blue 🌊
        "#F0B87A",  # Golden Honey 🍯
        "#6B9B6A",  # Olive Branch
        "#D4855A",  # Clay Pot 🏺
        "#5B8B8B",  # Deep Sea 🐟
        "#E8B08A",  # Beach Sand 🏖️
        "#4A8B6E",  # Cypress Tree 🌲
        "#D49A6A",  # Wheat Field 🌾
        "#8B9B6A",  # Faded Sage 🌿
    ]
    st.markdown("---")
    # ----Activity Filter ---#
    activity = sorted(data["Activity"].dropna().unique())
    activity.insert(0, "All")
    selected_activity = st.multiselect(
        "Select Supplementary Activities",
        activity,
        default=["All"],
        key="supp_activity_filter",
    )

    # Filter data
    if not selected_activity or "All" in selected_activity:
        filtered_data = data.copy()
    else:
        filtered_data = data[data["Activity"].isin(selected_activity)].copy()

    # Convert duration to timedelta
    filtered_data["Duration_Other"] = pd.to_timedelta(
        filtered_data["Duration_Other"], errors="coerce"
    )

    # Remove any rows with null duration
    filtered_data = filtered_data[filtered_data["Duration_Other"].notnull()]

    if filtered_data.empty:
        st.warning("No supplementary activities found for the selected filters")
        return

    # Group by Week and Activity
    nonrun_data = filtered_data.groupby(["Week", "Activity"], as_index=False)[
        "Duration_Other"
    ].sum()

    # Sort weeks properly
    nonrun_data["Week_Num"] = nonrun_data["Week"].str.extract(r"(\d+)").astype(int)
    nonrun_data = nonrun_data.sort_values("Week_Num")
    weeks_order = sorted(nonrun_data["Week"].unique())

    # Convert to minutes and format strings
    nonrun_data["Duration_Mins"] = nonrun_data["Duration_Other"].dt.total_seconds() / 60
    nonrun_data["Duration_Str"] = nonrun_data["Duration_Other"].apply(
        lambda td: f"{int(td.total_seconds() // 3600)}h {int((td.total_seconds() % 3600) // 60):02d}m"
    )

    # Calculate weekly totals (sorted)
    weekly_totals = (
        nonrun_data.groupby("Week")["Duration_Other"].sum().reindex(weeks_order)
    )
    weekly_totals_mins = weekly_totals.dt.total_seconds() / 60
    weekly_totals_str = weekly_totals.apply(
        lambda td: f"{int(td.total_seconds() // 3600)}h {int((td.total_seconds() % 3600) // 60):02d}m"
    )

    # Calculate week-over-week percent change (sorted)
    weekly_totals_pct_change = weekly_totals_mins.pct_change() * 100

    # Create delta labels for weekly total
    def format_delta(val):
        if pd.isna(val):
            return ""
        arrow = "▲" if val > 0 else "▼"
        color = "green" if val > 0 else "red"
        return f"<span style='color:{color}'>{arrow} {abs(val):.1f}%</span>"

    weekly_delta_labels = weekly_totals_pct_change.apply(format_delta)

    # Create total duration labels with delta
    total_labels = [
        f"<b>Total: {total}</b><br>{delta}"
        for total, delta in zip(weekly_totals_str, weekly_delta_labels)
    ]

    # Color palette for activities
    colors = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel

    # ==============================================
    # SUMMARY STATISTICS (Without nested expander)
    # ==============================================

    # Use columns for metrics instead of expander to avoid nesting
    st.markdown("##### 📊 Supplementary Activity Summary")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_hours = weekly_totals_mins.sum() / 60
        st.metric("Total Time", f"{total_hours:.1f} hours")

    with col2:
        avg_weekly = weekly_totals_mins.mean() / 60
        st.metric("Avg Weekly", f"{avg_weekly:.1f} hours")

    with col3:
        unique_activities = len(nonrun_data["Activity"].unique())
        st.metric("Activities", unique_activities)

    with col4:
        most_frequent = nonrun_data.groupby("Activity")["Duration_Mins"].sum().idxmax()
        st.metric("Most Frequent", most_frequent)

    # Activity breakdown table (collapsible using markdown instead of expander)
    with st.container():
        st.markdown("#### Activity Breakdown")
        activity_summary = (
            nonrun_data.groupby("Activity")
            .agg({"Duration_Mins": ["sum", "mean", "count"]})
            .round(1)
        )
        activity_summary.columns = ["Total (min)", "Avg per session (min)", "Sessions"]
        activity_summary["Total (hours)"] = activity_summary["Total (min)"] / 60
        st.dataframe(activity_summary, use_container_width=True)
    # ==============================================
    # CHART 1: STACKED BAR CHART (Absolute Duration)
    # ==============================================

    fig_stacked = go.Figure()

    # Loop through each activity and add a trace
    for i, activity_name in enumerate(nonrun_data["Activity"].unique()):
        subset = nonrun_data[nonrun_data["Activity"] == activity_name]

        fig_stacked.add_trace(
            go.Bar(
                x=subset["Week"],
                y=subset["Duration_Mins"],
                name=activity_name,
                text=subset["Duration_Str"],
                textposition="inside",
                textfont=dict(size=9, color="white"),
                marker_color=sisyphus_colors[i % len(sisyphus_colors)],
                hovertemplate=(
                    f"<b>{activity_name}</b><br>"
                    + "Week: %{x}<br>"
                    + "Duration: %{customdata}<br>"
                    + "<extra></extra>"
                ),
                customdata=subset["Duration_Str"],
            )
        )

    fig_stacked.update_xaxes(categoryorder="array", categoryarray=weeks_order)

    fig_stacked.update_layout(
        title="<b>Weekly Supplementary Activity Duration</b><br><sub>Yoga, swimming, cycling, strength training, etc.</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        yaxis_title="Duration (minutes)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        barmode="stack",
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#2b2b2b", size=10),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )

    # Add total duration labels on top
    fig_stacked.add_trace(
        go.Scatter(
            x=weekly_totals.index,
            y=weekly_totals_mins,
            text=total_labels,
            mode="text",
            textposition="top center",
            showlegend=False,
            textfont=dict(size=11, color="#4a3729"),
            hoverinfo="skip",
        )
    )

    st.plotly_chart(fig_stacked, use_container_width=True, key="supp_stacked_chart")

    st.markdown("---")

    # ==============================================
    # CHART 2: PERCENTAGE STACKED BAR CHART
    # ==============================================

    # Calculate percentages
    percentage_data = nonrun_data.copy()
    week_totals_pct = (
        percentage_data.groupby("Week")["Duration_Mins"].sum().reset_index()
    )
    week_totals_pct.columns = ["Week", "Total_Mins"]
    percentage_data = percentage_data.merge(week_totals_pct, on="Week")
    percentage_data["Percentage"] = (
        percentage_data["Duration_Mins"] / percentage_data["Total_Mins"]
    ) * 100

    fig_pct = go.Figure()

    for i, activity_name in enumerate(percentage_data["Activity"].unique()):
        subset = percentage_data[percentage_data["Activity"] == activity_name]

        fig_pct.add_trace(
            go.Bar(
                x=subset["Week"],
                y=subset["Percentage"],
                name=activity_name,
                text=subset["Percentage"].round(1).astype(str) + "%",
                textposition="inside",
                textfont=dict(size=9, color="white"),
                marker_color=sisyphus_colors[i % len(sisyphus_colors)],
                hovertemplate=(
                    f"<b>{activity_name}</b><br>"
                    + "Week: %{x}<br>"
                    + "Share: %{y:.1f}%<br>"
                    + f"Duration: {{:.0f}} min<br>".format(
                        subset["Duration_Mins"].values[0] if len(subset) > 0 else 0
                    )
                    + "<extra></extra>"
                ),
            )
        )

    fig_pct.update_xaxes(categoryorder="array", categoryarray=weeks_order)

    fig_pct.update_layout(
        title="<b>Supplementary Activity Distribution (%)</b><br><sub>How your cross-training focus shifts week to week</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
            gridwidth=1,
        ),
        yaxis_title="Percentage of Weekly Supplementary Time (%)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            gridcolor="#efe6dc",
            gridwidth=1,
            range=[0, 100],
            ticksuffix="%",
        ),
        barmode="stack",
        height=450,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#2b2b2b", size=10),
            bgcolor="rgba(255, 255, 255, 0.8)",
        ),
    )

    st.plotly_chart(fig_pct, use_container_width=True, key="supp_pct_chart")


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
    # nonrun_data["Week"] = [week[:1] + week[-2:] for week in data["Week"]]

    # ##GROUP BY
    # data["Week"] = [
    #     week[:1] + week[-2:] for week in data["Week"]
    # ]  # shorten weekname before groupby

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
        title_font=dict(color="#2b2b2b"),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b"),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
        ),
        yaxis_title="Duration (Mins)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b"),
            gridcolor="#efe6dc",
        ),
        barmode="stack",
        height=400,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color="#2b2b2b"),
        ),
    )

    fig_bar.add_trace(
        go.Scatter(
            x=weekly_totals.index,
            y=weekly_totals_mins,
            text=weekly_totals_str,
            mode="text",
            textposition="top center",
            showlegend=False,
            textfont=dict(size=14, color="#4a3729"),
        )
    )

    st.plotly_chart(fig_bar, use_container_width=True, key="run_chart_2")


def generate_running_duration_chart_new(data):
    """
    Optional: Show running duration as a complementary metric to distance.
    Useful for time-based training analysis.
    """
    # Filter for running activities only
    running_data = data[
        ~data["Activity"].isin(
            [
                "Rest",
                "Cross Train",
                "Strength Training",
                "WeightTraining",
                "Yoga",
                "Pilates",
                "Swim",
                "Ride",
                "Cycle",
            ]
        )
    ].copy()

    if running_data.empty:
        st.info("No running activities found")
        return

    # Calculate duration from Distance and Pace (if available)
    # Or use existing Duration column if you have it
    if "Duration" in running_data.columns:
        running_data["Duration_Mins"] = (
            pd.to_timedelta(
                running_data["Duration"], errors="coerce"
            ).dt.total_seconds()
            / 60
        )
    else:
        # Calculate from Distance and Pace if Duration not available
        running_data["Pace_Mins"] = (
            pd.to_timedelta(running_data["Pace"], errors="coerce").dt.total_seconds()
            / 60
        )
        running_data["Duration_Mins"] = (
            running_data["Distance"] * running_data["Pace_Mins"]
        )

    # Group by week
    weekly_duration = running_data.groupby("Week")["Duration_Mins"].sum().reset_index()

    # Sort weeks
    weekly_duration["Week_Num"] = (
        weekly_duration["Week"].str.extract(r"(\d+)").astype(int)
    )
    weekly_duration = weekly_duration.sort_values("Week_Num")

    # Format duration as hours:minutes
    weekly_duration["Duration_Str"] = weekly_duration["Duration_Mins"].apply(
        lambda x: f"{int(x // 60)}h {int(x % 60):02d}m"
    )

    # Create bar chart
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=weekly_duration["Week"],
            y=weekly_duration["Duration_Mins"],
            text=weekly_duration["Duration_Str"],
            textposition="auto",
            marker=dict(color="#f3d2b2", line=dict(color="#4a3729", width=1)),
            hovertemplate="Week: %{x}<br>Duration: %{text}<extra></extra>",
        )
    )

    fig.update_layout(
        title="<b>Weekly Running Duration</b><br><sub>Total time spent running per week</sub>",
        title_font=dict(color="#2b2b2b", size=16),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        xaxis_title="Week",
        xaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            tickfont=dict(color="#4a3729"),
            gridcolor="#efe6dc",
        ),
        yaxis_title="Duration (minutes)",
        yaxis=dict(
            title_font=dict(color="#2b2b2b", size=12),
            gridcolor="#efe6dc",
        ),
        height=400,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=False,
    )

    st.plotly_chart(fig, use_container_width=True, key="running_duration_chart")
