import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time as tm
from datetime import time, datetime
import data.push_data as push
import data.read_data as pull
import data.read_data_local as local
import numpy as np


st.set_page_config(
    page_title="Operation SCSM 2025",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)


Welcome_msg = "darkgreen:[Celebrate progress, not perfection. You showed up — and that matters most.]"
st.markdown(
    '<p style="color:#206040; font-size:35px;">Celebrate progress, not perfection. You showed up — and that matters most.</p>',
    unsafe_allow_html=True,
)

st.markdown(":blue[*Use Sidebar to enter training log*] :sunglasses:")

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
            # new_log = pd.DataFrame(new_log)

            push.push_runner_data(new_log)
            ###Submit Notice
            with st.spinner("Wait lang...", show_time=True):
                tm.sleep(2)
            st.success("Done! Activity Recorded!")
            st.balloons()
            st.badge("Success", icon=":material/check:", color="green")

###############TRAINING PLAN SECTION#############################################


######METRICS########
# # LAYOUT COLOUMNS
tab1, tab2, tab3 = st.tabs(["📊 Stats", "🗓️ Program", "📘 Reference"])


full_df = pd.DataFrame(pull.get_runner_data())

with tab1:
    # -------PULL DATA ONCE --------#

    # MEMBER FILTER
    members = sorted(full_df["Member Name"].dropna().unique())
    members.insert(1, "All")  # Add 'All' option at the top
    selected_member = st.selectbox("Select Member to Filter", sorted(members), index=1)

    # Filter the DataFrame

    # Apply filtering
    if selected_member == "All":
        filtered_member_df = full_df
    else:
        filtered_member_df = full_df[full_df["Member Name"] == selected_member]

    st.header(f"📊 Overview & Stats : {selected_member}", divider="blue")

    # filter non running activity
    filtered_data = filtered_member_df[
        ~filtered_member_df["Activity"].isin(
            ["Rest", "Cross Train", "Strength Training", 0]
        )
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
    avg_pace = df["Pace"].mean()

    metric_pace = f"{int(avg_pace.total_seconds() // 60):02d}:{int(avg_pace.total_seconds() % 60):02d}"

    # .sum() / df["Pace"].len()

    col1, col2, col3, col4 = st.columns(4)
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

    metric_tillrace = (datetime(2025, 12, 7) - datetime.today()).days

    col4.metric(
        "Days Till Race Day 🏁 👏",
        value=metric_tillrace,
        label_visibility="visible",
        border=True,
    )

    ###########CHARTS###########
    from visuals import sunburst as sb
    from visuals import combochart as cb
    from visuals import table as mt
    from visuals import line_polar as lp
    from visuals import stats_table as stats

    # -----ALL STATS TABLE-------#
    st.subheader("🏆 All-Time Highlights", divider="gray")
    stats.generate_matrix_member(filtered_member_df)

    # -----COMBO CHART WEEKLY-------#
    st.subheader("📅🏃‍♂️ Weekly Distance vs. Pace", divider="gray")
    cb.generate_combo(filtered_member_df)

    # -----COMBO CHART DAILY-------#
    st.subheader("📈📍 Daily Distance vs. Pace", divider="gray")
    cb.generate_combo_daily(filtered_member_df)

    # -----SUN BURST-------#
    st.subheader("👥📊 Weekly Activity per Member", divider="gray")
    sb.generate_sunburst(filtered_member_df)

    # -----LINE POLAR-------#
    st.subheader("⚖️📊 Activity Comparison (Normalized)", divider="gray")
    lp.generate_linepolar(filtered_member_df)

    # -----ALL ACTIVITY TABLE-------#
    st.subheader("🗂️ Activity Reference", divider="gray")
    mt.generate_matrix(filtered_member_df)


with tab2:
    st.header("🗓️💪 Your Training Plan", divider="blue")

    # with st.expander("View Training Program"):
    prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=0&single=true"
    components.iframe(
        prog_sheet,
        width=1500,
        height=800,
    )

with tab3:
    from visuals import referencetab as ref

    ref.ref_tab()
