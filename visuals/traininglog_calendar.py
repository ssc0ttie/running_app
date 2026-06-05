import plotly.graph_objects as go
import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta


def create_strava_training_log(df_activities, metric="Distance"):
    """
    Create a Strava-style training log calendar with bubble chart.
    """
    # Make a copy to avoid modifying original
    data = df_activities.copy()

    if data.empty:
        st.warning("No activities to display in training log")
        return go.Figure()

    # Ensure Date_of_Activity is datetime
    data["Date_of_Activity"] = pd.to_datetime(data["Date_of_Activity"])

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
                0,
            ]
        )
    ].copy()

    if running_data.empty:
        st.info("No running activities found for the selected filters")
        return go.Figure()

    # Prepare duration values if needed
    if metric == "Duration":
        if "Duration" in running_data.columns:
            if pd.api.types.is_timedelta64_dtype(running_data["Duration"]):
                running_data["Metric_Value"] = (
                    running_data["Duration"].dt.total_seconds() / 60
                )
            else:
                running_data["Metric_Value"] = (
                    pd.to_timedelta(
                        running_data["Duration"], errors="coerce"
                    ).dt.total_seconds()
                    / 60
                )
        elif "Duration_Other" in running_data.columns:
            running_data["Metric_Value"] = (
                pd.to_timedelta(
                    running_data["Duration_Other"], errors="coerce"
                ).dt.total_seconds()
                / 60
            )
        else:
            if "Pace" in running_data.columns:
                running_data["Pace_Mins"] = (
                    pd.to_timedelta(
                        running_data["Pace"], errors="coerce"
                    ).dt.total_seconds()
                    / 60
                )
                running_data["Metric_Value"] = (
                    running_data["Distance"] * running_data["Pace_Mins"]
                )
            else:
                st.warning("Duration data not available. Using Distance instead.")
                metric = "Distance"
                running_data["Metric_Value"] = running_data["Distance"]
    else:
        running_data["Metric_Value"] = running_data["Distance"]

    # Format the label text
    def format_duration(minutes):
        if pd.isna(minutes):
            return "0m"
        if minutes >= 60:
            hours = int(minutes // 60)
            mins = int(minutes % 60)
            if mins > 0:
                return f"{hours}h{mins}m"
            else:
                return f"{hours}h"
        else:
            return f"{int(minutes)}m"

    if metric == "Distance":
        running_data["Metric_Label"] = (
            running_data["Metric_Value"].round(1).astype(str) + "km"
        )
    else:
        running_data["Metric_Label"] = running_data["Metric_Value"].apply(
            format_duration
        )

    # Get date range
    min_date = running_data["Date_of_Activity"].min()
    max_date = running_data["Date_of_Activity"].max()

    # Generate calendar grid starting from Monday
    start_date = min_date - pd.Timedelta(days=min_date.weekday())
    end_date = max_date + pd.Timedelta(days=(6 - max_date.weekday()))
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")

    # Create dictionary for activities by date
    activities_by_date = {}
    for date, group in running_data.groupby(running_data["Date_of_Activity"].dt.date):
        activities_by_date[date] = group

    # Get unique weeks
    weeks = sorted(
        running_data["Week"].unique(),
        key=lambda x: int(str(x).replace("W", "")) if str(x).startswith("W") else 0,
    )

    if not weeks:
        weeks = []
        current_week = None
        for date in date_range:
            week_num = date.isocalendar().week
            if current_week != week_num:
                weeks.append(f"W{week_num:02d}")
                current_week = week_num

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    # Get min and max for bubble sizing and coloring
    max_metric = running_data["Metric_Value"].max()
    min_metric = running_data["Metric_Value"].min()

    # MUCH LARGER bubble size range - aggressive sizing to fill gaps
    min_bubble_size = 30  # Minimum bubble size
    max_bubble_size = 60  # Maximum bubble size

    # Choose colorscale based on metric - single hue gradients
    if metric == "Distance":
        colorscale = "Viridis"
        color_title = "Distance (km)"
    else:
        colorscale = "thermal"
        color_title = "Duration (minutes)"

    # COLLECT ALL BUBBLE DATA IN LISTS
    x_positions = []
    y_positions = []
    sizes = []
    colors = []
    texts = []  # This will be the metric inside bubbles
    hover_texts = []
    text_sizes = []

    # For activity labels below bubbles
    label_x_positions = []
    label_y_positions = []
    label_texts = []
    label_sizes = []

    for week_idx, week_label in enumerate(weeks):
        week_activities = running_data[running_data["Week"] == week_label]

        for day_idx, day in enumerate(days):
            matching_date = None
            for _, activity in week_activities.iterrows():
                act_date = activity["Date_of_Activity"]
                if act_date.weekday() == day_idx:
                    matching_date = act_date
                    break

            if matching_date is None:
                continue

            date_key = matching_date.date()
            day_activities = activities_by_date.get(date_key, pd.DataFrame())

            if day_activities.empty:
                continue

            num_activities = len(day_activities)
            base_y = -week_idx * 7.0

            for act_idx, (_, activity) in enumerate(day_activities.iterrows()):
                metric_value = activity["Metric_Value"]
                metric_label = activity["Metric_Label"]  # This stays inside bubble
                activity_name = activity["Activity"]
                hr_value = activity.get("HR (bpm)", None)

                # Calculate bubble size
                if max_metric > min_metric:
                    scale = (metric_value - min_metric) / (max_metric - min_metric)
                    scale = scale**0.6
                    bubble_size = min_bubble_size + (
                        scale * (max_bubble_size - min_bubble_size)
                    )
                else:
                    bubble_size = (min_bubble_size + max_bubble_size) / 2

                # Calculate y position
                if num_activities > 1:
                    spacing = 2.2
                    total_height = (num_activities - 1) * spacing
                    start_y = base_y - (total_height / 2)
                    y_pos = start_y + (act_idx * spacing)
                    text_size = 11
                else:
                    y_pos = base_y
                    text_size = 12

                # ALWAYS add activity name and day below bubble (for all activities)
                day_name = matching_date.strftime("%a")
                # Truncate activity name if too long (max 12 chars)
                short_name = (
                    activity_name[:12] + ".."
                    if len(activity_name) > 12
                    else activity_name
                )
                label_text = f"{short_name}<br>{day_name}"
                label_x_positions.append(day_idx)
                label_y_positions.append(y_pos - 1.0)  # Position below bubble
                label_texts.append(label_text)
                label_sizes.append(9)

                # Build hover text
                hover_text = f"<b>{matching_date.strftime('%A, %B %d, %Y')}</b><br>"
                hover_text += f"<b>{activity_name}</b><br>"
                hover_text += f"{metric}: {metric_label}<br>"

                # if hr_value and pd.notna(hr_value):
                #     hover_text += f"❤️ HR: {hr_value:.0f} bpm"
                
                # Handle HR value safely
                if hr_value and pd.notna(hr_value):
                    try:
                        hr_float = float(hr_value)
                        hover_text += f"❤️ HR: {hr_float:.0f} bpm"
                    except (ValueError, TypeError):
                        hover_text += f"❤️ HR: {hr_value} bpm"
                # Append bubble data (metric stays inside)
                x_positions.append(day_idx)
                y_positions.append(y_pos)
                sizes.append(bubble_size)
                colors.append(metric_value)
                texts.append(metric_label)  # Only metric inside bubble
                text_sizes.append(text_size)
                hover_texts.append(hover_text)

    # Create figure
    fig = go.Figure()

    # Add main bubbles trace (metric inside)
    fig.add_trace(
        go.Scatter(
            x=x_positions,
            y=y_positions,
            mode="markers+text",
            marker=dict(
                size=sizes,
                color=colors,
                colorscale=colorscale,
                showscale=False,
                colorbar=dict(
                    title=color_title,
                    thickness=15,
                    len=0.5,
                    x=1.02,
                    tickformat=".0f",
                ),
                line=dict(width=1.5, color="white"),
                sizemode="diameter",
                sizeref=1.0,
                sizemin=4,
                opacity=0.9,
            ),
            text=texts,  # Metric label inside bubble
            textposition="middle center",
            textfont=dict(
                size=10,
                color="white",
                weight="bold",
                family="Arial",
            ),
            hoverinfo="text",
            hovertext=hover_texts,
            name="Activities",
            showlegend=False,
        )
    )

    # Add second trace for activity name and day below bubbles
    if label_x_positions:
        fig.add_trace(
            go.Scatter(
                x=label_x_positions,
                y=label_y_positions,
                mode="text",
                text=label_texts,
                textposition="middle center",
                textfont=dict(
                    size=10,
                    color="#555",
                    family="Arial",
                ),
                hoverinfo="none",
                showlegend=False,
            )
        )

    # Update layout
    fig.update_layout(
        # title=dict(
        #     text=f" Training Log : {metric}",
        #     font=dict(size=18, weight="bold", color="#2b2b2b"),
        # ),
        xaxis=dict(
            title="",
            tickmode="array",
            tickvals=list(range(7)),
            ticktext=days,
            gridcolor="#e0e0e0",
            showgrid=True,
            gridwidth=1,
            showline=True,
            linecolor="#ccc",
            range=[-0.5, 6.5],
            tickfont=dict(size=14, weight="bold"),
            fixedrange=False,
        ),
        yaxis=dict(
            title="",
            tickmode="array",
            tickvals=[-i * 7.0 - 3.5 for i in range(len(weeks))],
            ticktext=weeks,
            autorange="reversed",
            gridcolor="#e0e0e0",
            showgrid=True,
            gridwidth=1,
            showline=True,
            linecolor="#ccc",
            tickfont=dict(size=10),
            fixedrange=False,
        ),
        plot_bgcolor="#faf7f2",
        paper_bgcolor="#faf7f2",
        height=max(600, len(weeks) * 160),
        margin=dict(l=50, r=50, t=50, b=60),  # Increased bottom margin for labels
        hoverlabel=dict(bgcolor="white", font_size=12, font_family="Arial"),

    )

    return fig


def create_training_log_section(data):
    """Training log with view selector for Distance vs Duration"""
    # st.markdown("---")
    col1, col2 = st.columns([1,3])
    # with col1:
    #     st.markdown(
    #         """
    #         <div style="
    #             color:#3a3939;
    #             font-size: 20px;
    #             font-weight: 600;
    #             border-bottom: 1px solid #ccc;
    #             padding-bottom: 4px;
    #             margin-top: 20px;
    #             margin-bottom: 10px;">
    #             📅 Training Calendar
    #         </div>
    #     """,
    #         unsafe_allow_html=True,
    #     )
    col1, col2 = st.columns(2)



    with col1:
        st.markdown(
            """
            <div style="
                display: flex;
                align-items: left;
                justify-content: left;
                height: 100%;
            ">
                <div style="
                    font-weight: 600;
                    font-size: 16px;
                    color: #3a3939;
                    background: #f0f2f6;
                    padding: 8px 16px;
                    border-radius: 20px;
                    display: inline-block;
                ">
                    📅 Training Calendar
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        

    with col2:
        view_metric = st.radio(
            "Select View:",
            ["Distance", "Duration"],
            horizontal=True,
            key="training_log_view",
            label_visibility="collapsed",
        )
    # with col2:
    #     view_metric = st.radio(
    #         "Select View:",
    #         ["Distance", "Duration"],
    #         horizontal=True,
    #         key="training_log_view",
    #         label_visibility="collapsed",
    #     )

    if data.empty:
        st.info("No activities to display in training log.")
        return

    # Create the chart
    fig = create_strava_training_log(data, metric=view_metric)

    # Fixed height container (this actually works!)
    with st.container(height=510):
        st.plotly_chart(
            fig, use_container_width=True, key=f"training_log_{view_metric}"
        )
