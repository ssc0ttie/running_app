import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time as tm
from datetime import time, datetime
import data.push_data as push
import data.read_data as pull

st.set_page_config(
    page_title="Operation SCSM 2025",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)
Welcome_msg = (
    "Celebrate progress, not perfection. You showed up — and that matters most."
)
st.header(":blue[🏃‍♂️Operation SCSM 2025]")

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
        mem_selection = st.selectbox(
            "Members",
            ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"],
            index=None,
        )
        # member_name = st.markdown(f"Select Member", {mem_selection})
        date = st.date_input("Date of Activity", value=datetime.today())

        # Activity list
        act_selection = st.selectbox(
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
            index=None,
        )

        distance = st.number_input("Distance")
        pace = st.time_input("Pace (min/km)", value=time(8, 45), step=60)
        hr = st.number_input("HR (bmp)", min_value=0, max_value=220)
        cad = st.number_input("Cadence (spm)", min_value=0, max_value=200)
        rpe = st.slider("RPE", 0, 10, 1)
        rpe2 = st.feedback(options="faces", key=int)
        shoe = st.selectbox(
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
            index=None,
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
                    act_selection if act_selection else ""
                ),  # Get first selected activity or empty
                distance,
                pace.strftime("0:%H:%M"),  # Convert time to string (e.g., "08:45")
                hr,
                cad,
                rpe,
                shoe if shoe else "",  # Get first selected shoe or empty
                remarks,
                (
                    mem_selection if mem_selection else ""
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

    # """revert back"""
    # df = pd.DataFrame(pull.get_runner_data())

    df = pd.DataFrame(pull.get_runner_data())
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
    #######CHARTS###########
from visuals import sunburst as sb
from visuals import combochart as cb
from visuals import table as mt
from visuals import line_polar as lp
from visuals import stats_table as stats

st.subheader("ALL-TIME STATS", divider="gray")
# """revert back"""
stats.generate_matrix_member(pull.get_runner_data())

# Combo chart
st.subheader("Distance x Pace", divider="gray")
# cb.generate_combo(pull.get_runner_data())
# """revert back"""

cb.generate_combo(pull.get_runner_data())

# sunburst
st.subheader("Distance per Member per Week per Activity", divider="gray")
# """revert back"""
# sb.generate_sunburst(pull.get_runner_data())
sb.generate_sunburst(pull.get_runner_data())

# LINE POLAR
st.subheader("Activity Comparison Across Multiple Metrics (Normalized)", divider="gray")
# sb.generate_sunburst(pull.get_runner_data())
lp.generate_linepolar(pull.get_runner_data())

# TABLE OF ALL ACTIVITY
st.subheader("Activity List", divider="gray")
mt.generate_matrix(pull.get_runner_data())
