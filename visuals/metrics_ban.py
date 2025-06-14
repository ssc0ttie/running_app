import streamlit as st
import numpy as np


def generate_metrics(data):
    st.header("STATS", divider="blue")

    # """revert back"""
    # df = pd.DataFrame(pull.get_runner_data())

    df = data
    # filter non running activity
    filtered_data = df[
        ~df["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]

    df = filtered_data

    df["Moving_Time"] = pd.to_timedelta(df["Moving_Time"])
    metric_distance = int(df["Distance"].sum())

    # TOTAL MOVING TIME
    total_seconds = int(df["Moving_Time"].sum().total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    metric_movingtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # AVG PACE
    avg_pace = pd.to_timedelta(df["Pace"]).mean()

    metric_pace = f"{int(avg_pace.total_seconds() // 60):02d}:{int(avg_pace.total_seconds() % 60):02d}"

    # .sum() / df["Pace"].len()

    col1, col2, col3 = st.columns(3)
    col1.metric(
        "Total Distance in kms 🏃‍♀️‍➡️",
        value=metric_distance,
        label_visibility="visible",
        border=True,
    )
    col2.metric(
        "Moving Time ⏱️",
        value=metric_movingtime,
        label_visibility="visible",
        border=True,
    )
    col3.metric(
        "Average Pace 🚄", value=metric_pace, label_visibility="visible", border=True
    )
