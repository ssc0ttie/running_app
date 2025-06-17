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
