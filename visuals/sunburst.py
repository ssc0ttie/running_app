# SUNBURST

import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly._subplots import make_subplots
import pandas as pd
import streamlit as st


def generate_sunburst(data):

    sunburst_data = data.groupby(["Member Name", "Week", "Activity"], as_index=False)[
        "Distance"
    ].sum()

    fig = px.sunburst(
        sunburst_data,
        path=["Member Name", "Week", "Activity"],
        values="Distance",
        title="Distance per Member per Week per Activity",
        color="Distance",
        color_continuous_scale="RdBu",
    )
    fig.update_layout(
        width=800,
        height=800,
        legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5),
    )
    st.plotly_chart(fig, use_container_width=True)


def generate_sunburst_member(data):
    # SUNBURST

    sunburst_data = data.groupby(["Member Name", "Week", "Activity"], as_index=False)[
        "Distance"
    ].sum()

    for member in sunburst_data["Member Name"].unique():
        member_df = sunburst_data[sunburst_data["Member Name"] == member]

        fig = px.sunburst(
            member_df,
            path=["Member Name", "Week", "Activity"],
            values="Distance",
            title=f"Distance per Member per Week per Activity{member}",
            color="Distance",
            color_continuous_scale="RdBu",
        )
        fig.update_layout(
            legend=dict(
                orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5
            )
        )

        fig.show()

        st.subheader(member)

        st.plotly_chart(fig, use_container_width=True)
