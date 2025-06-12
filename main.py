import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time as tm
from datetime import time, datetime
import data.push_data as push
import data.read_data as pull


st.title("🏃‍♂️Operation SCSM 2025")


Welcome_msg = (
    "Celebrate progress, not perfection. You showed up — and that matters most."
)
st.subheader(Welcome_msg)
st.markdown(":blue[*Use Sidebar to enter training log*] :sunglasses:")
# # LAYOUT COLOUMNS
tab1, tab2 = st.tabs(["Stats", "Program"])

element_name = "Log Your Activity Here"
with st.sidebar:
    st.sidebar.title("🏃‍♂️ Runner's Training Log")
    st.sidebar.markdown("Use this panel to input your training data.")
    with st.form("activity_log", clear_on_submit=True, border=True):
        time_stamp_ = datetime.now()
        time_stamp = time_stamp_.strftime("%Y-%m-%d")
        mem_selection = st.multiselect(
            "Members",
            ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"],
            max_selections=1,
        )
        # member_name = st.markdown(f"Select Member", {mem_selection})
        date = st.date_input("Date of Activity", value=datetime.today())

        # Activity list
        act_selection = st.multiselect(
            "Activity",
            [
                "5k LSD Road@ Zone 2 Pace",
                "6k LSD Road@ Zone 2 Pace",
                "8k LSD Road@ Zone 2 Pace",
                "10k LSD Road@ Zone 2 Pace",
                "10k LSD Trail@ Zone 2 Pace",
                "11k LSD Road@ Zone 2 Pace",
                "12k LSD Road@ Zone 2 Pace",
                "14k LSD Road@ Zone 2 Pace",
                "15k LSD Road@ Zone 2 Pace",
                "15k LSD Trail@ Zone 2 Pace",
                "17k LSD Road@ Zone 2 Pace",
                "18k LSD Road@ Zone 2 Pace",
                "19k LSD Road@ Zone 2 Pace",
                "20k LSD Road@ Zone 2 Pace",
                "20k LSD Trail@ Zone 2 Pace",
                "21k LSD Trail@ Zone 2 Pace",
                "24k LSD Trail@ Zone 2 Pace",
                "26k LSD Road@ Zone 2 Pace",
                "27k LSD Trail@ Zone 2 Pace",
                "28k LSD Road@ Zone 2 Pace",
                "31k LSD Road@ Zone 2 Pace",
                "20 Mins Easy Run",
                "30 Mins Easy Run",
                "35 Mins Easy Run",
                "40 Mins Easy Run",
                "45 Mins Easy Run",
                "50 Mins Easy Run",
                "55 Mins Easy Run",
                "60 Mins Easy Run",
                "RACE DAY",
                "Rest",
                "Speed Work (Zone 4 : 3x400M)",
                "Speed Work (Zone 4 : 4x400M)",
                "Speed Work (Zone 4 : 5x400M)",
                "Speed Work (Zone 4 : 6x400M)",
                "Strength Training",
                "Cross Train",
                "1k Tempo",
                "2k Tempo",
                "3k Tempo",
                "4k Tempo",
                "5k Tempo",
                "6k Tempo",
                "7k Tempo",
                "8k Tempo",
                "9k Tempo",
                "10k Tempo",
            ],
            max_selections=1,
        )

        distance = st.number_input("Distance")
        pace = st.time_input("Pace (min/km)", value=time(8, 45), step=60)
        hr = st.number_input("HR (bmp)", min_value=0, max_value=220)
        cad = st.number_input("Cadence (spm)", min_value=0, max_value=200)
        rpe = st.slider("RPE", 0, 10, 1)
        rpe2 = st.feedback(options="faces", key=int)
        shoe = st.multiselect(
            "Shoe",
            [
                "Adidas Adizero SL2",
                "Asics Purple",
                "Boston 12",
                "NB Rebel v3",
                "Nike",
                "Nike Winflo 10",
                "Novablast 3",
                "Adidas Pink",
                "Reebok Float Ride Energy 4",
                "Sketcher",
            ],
            max_selections=1,
        )
        remarks = st.text_area("Remarks")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit Log")

        #############PUSH DATA####################

        if submitted:

            new_log = [
                time_stamp,  # Convert datetime to ISO string
                date.isoformat(),  # Convert date to ISO string
                (
                    act_selection[0] if act_selection else ""
                ),  # Get first selected activity or empty
                distance,
                pace.strftime("0:%H:%M"),  # Convert time to string (e.g., "08:45")
                hr,
                cad,
                rpe,
                shoe[0] if shoe else "",  # Get first selected shoe or empty
                remarks,
                (
                    mem_selection[0] if mem_selection else ""
                ),  # Get first selected member or empty
            ]

            push.push_runner_data(new_log)
            ###Submit Notice
            with st.spinner("Wait lang...", show_time=True):
                tm.sleep(2)
            st.success("Done! Activity Recorded!")
            st.balloons()

###############TRAINING PLAN SECTION#############################################
with tab2:
    st.header("TRAINING PLAN", divider="blue")

    # with st.expander("View Training Program"):
    prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=0&single=true"
    components.iframe(
        prog_sheet,
        width=1500,
        height=800,
    )
######METRICS########
with tab1:
    st.header("STATS", divider="blue")
    import numpy as np

    df = pd.DataFrame(pull.get_runner_data())

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

    #####################################TEST CHART#####################

    # ##FILTER BY MEMBER ##
    # filt = df["Member_Name"] == mem_selection

    # df.loc[filt]

    ###PLOTLY TEST###

    import plotly.express as px
    import plotly.graph_objects as go

    # import plotly.io as pio

    # pio.renderers.default = "browser"

    from plotly._subplots import make_subplots

    ##GROUP BY
    act_date_group = df.groupby("Week", as_index=False)
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
            x=dist_data["Week"],
            y=dist_data["Distance"],
            name="Distance (km)",
            marker=dict(color="DarkSlateGrey"),
        )
    )

    # Add line chart for Pace
    fig.add_trace(
        go.Scatter(
            x=dist_data["Week"],
            y=pace_data["Pace_Mins"],
            name="Pace (min/km)",
            yaxis="y2",
            marker=dict(size=12, line=dict(width=2, color="DarkSlateGrey")),
        ),
    )

    # Add second y-axis for Pace
    fig.update_layout(title="Distance x Pace")
    fig.update_xaxes(title_text="Week")
    fig.update_yaxes(title_text="KMS", secondary_y=False)
    fig.update_yaxes(title_text="Pace (min/km)", secondary_y=True)

    fig.show()

    st.plotly_chart(fig, use_container_width=True)

    # DISPLAY TABLE OF ALL ACTIVITY##
    st.dataframe(df, height=500)


import visuals.sunburst as sb

sb.generate_sunburst(pull.get_runner_data())
