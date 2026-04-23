import plotly.express as px
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
import streamlit as st


def generate_donut_chart(data):
    # Ensure Distance is numeric
    data["Distance"] = pd.to_numeric(data["Distance"], errors="coerce")

    # Drop rows where Shoe or Distance is missing
    shoe_data = data.dropna(subset=["Shoe", "Distance"])

    # Group by Shoe and sum Distance
    grouped = shoe_data.groupby("Shoe", as_index=False)["Distance"].sum()
    # label
    grouped["label"] = (
        grouped["Shoe"] + " " + grouped["Distance"].round(1).astype(str) + " km"
    )

    # Create Donut chart
    fig = px.pie(
        grouped,
        names="Shoe",
        values="Distance",
        # title="Distance Covered by Shoe",
        hole=0.4,  # 👈 donut style
        color_discrete_sequence=px.colors.qualitative.Set3,
        hover_data={"Distance": ":.1f"},
    )

    fig.update_traces(textinfo="percent+label")
    fig.update_layout(height=400, showlegend=False)

    st.plotly_chart(fig)


def generate_donut_chart_new(data):
    # Ensure Distance is numeric
    data["Distance"] = pd.to_numeric(data["Distance"], errors="coerce")

    # Drop rows where Shoe or Distance is missing
    shoe_data = data.dropna(subset=["Shoe", "Distance"])

    # Group by Shoe and sum Distance
    grouped = shoe_data.groupby("Shoe", as_index=False)["Distance"].sum()

    # label
    grouped["label"] = (
        grouped["Shoe"] + " " + grouped["Distance"].round(1).astype(str) + " km"
    )

    # Create Donut chart with Mediterranean colors
    fig = px.pie(
        grouped,
        names="Shoe",
        values="Distance",
        hole=0.4,
        color_discrete_sequence=["#E8956A", "#4A9B9B", "#6B9B6A", "#D4855A", "#F0B87A"],
        hover_data={"Distance": ":.0f"},
    )

    fig.update_traces(
        textinfo="percent+label",
        textfont=dict(color="#2b2b2b", size=10),
        marker=dict(line=dict(color="#faf7f2", width=2)),
    )

    fig.update_layout(
        height=400,
        showlegend=False,
        title_font=dict(color="#2b2b2b", size=14),
        paper_bgcolor="#faf7f2",
        margin=dict(l=20, r=20, t=40, b=20),
    )

    return fig
