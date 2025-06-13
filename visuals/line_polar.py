import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
import streamlit as st


def generate_linepolar(data):
    # filter, group and aggregate
    filtered_data = data[
        ~data["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]  # filter non running activity

    agg_df = filtered_data.groupby("Activity", as_index=False).agg(
        {
            "Distance": "mean",
            "Cadence (steps/min)": "mean",
            "RPE (1–10 scale)": "mean",
            "Pace": "mean",  # timedelta format
        }
    )
    # Format Pace as mm:ss string
    agg_df["Pace_Str"] = agg_df["Pace"].apply(
        lambda td: f"{int(td.total_seconds() // 60):02d}:{int(td.total_seconds() % 60):02d}"
    )

    agg_df["Pace"] = agg_df["Pace"].dt.total_seconds().astype(float)

    # Normalize the measures
    measures = ["Distance", "Cadence (steps/min)", "RPE (1–10 scale)", "Pace"]
    scaler = MinMaxScaler()
    # agg_df_scaled[measures] = scaler.fit_transform(agg_df[measures])

    normalized = pd.DataFrame(scaler.fit_transform(agg_df[measures]), columns=measures)

    # Melt for polar plotting

    df_normalized = agg_df[["Activity"]].copy()
    for metric in measures:
        df_normalized[metric + "_norm"] = normalized[metric]
        df_normalized[metric + "_actual"] = agg_df[metric]

    melted = pd.melt(
        df_normalized,
        id_vars=["Activity"],
        value_vars=[m + "_norm" for m in measures],
        var_name="Metric",
        value_name="Normalized Value",
    )
    # Add actual values
    melted["Metric"] = melted["Metric"].str.replace("_norm", "")
    melted["Actual Value"] = pd.concat(
        [df_normalized[m + "_actual"] for m in measures], ignore_index=True
    )

    # Plot
    fig = px.line_polar(
        melted,
        r="Normalized Value",
        theta="Activity",
        color="Metric",
        line_close=True,
        markers=True,
        text="Actual Value",
        template="plotly",
    )

    fig.update_traces(
        fill="toself",
        textposition="top center",
        textfont=dict(color="blue"),
        hovertemplate="Metric: %{theta}<br>Actual: %{text}<extra></extra>",
    )

    fig.update_layout(
        # title="Activity Comparison Across Multiple Metrics (Normalized)",
        width=800,
        height=800,
    )

    st.plotly_chart(fig, use_container_width=True)
