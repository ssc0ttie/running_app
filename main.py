import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time as tm
from datetime import time, datetime
import data.push_data as push
from data import read_data_cached as pullc
from data import read_data_uncached as pulluc

# import data.read_data_local as local
import numpy as np
from visuals import racedaycounter as rdc


st.set_page_config(
    page_title="Operation SCSM 2025",
    page_icon="🏃‍♂️",
    layout="wide",
    initial_sidebar_state="expanded",
)

rdc.raceday_counter()

Welcome_msg = (
    "Celebrate progress, not perfection. You showed up — and that matters most."
)
st.text("")

st.markdown(
    f"""
    <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                background-color: rgba(0, 0, 0, 0); border-left: 4px solid #2e8b57; margin-bottom: 1rem;">
        <p style="font-size: 1.1rem; color: #2f3e46; font-style: italic; margin: 0;">
            {Welcome_msg}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.text("")
st.text("")


# # st.header(Welcome_msg)
# st.markdown(":blue[* *Navigate through the tabs here ⬇️*] :sunglasses:")
st.markdown(
    """
    <h2>💡 How to Use This Page</h2>
    <p>Use tabs below to explore your training logs, stats, programs, and strength workouts. 💪</p>
    """,
    unsafe_allow_html=True,
)


# element_name = "Log Your Activity Here"


# ----------------- Confirmation Dialog -----------------
@st.dialog("Confirm Entry?")
def confirm_submission(new_log):
    st.write("Are you sure you want to submit this entry?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, Submit"):
            # Simulate push to backend
            st.session_state["submitted_data"] = new_log
            # st.success("✅ Activity Recorded!")
            st.session_state["submitted"] = True
            st.session_state["pending_log"] = None
            # st.balloons()
            st.rerun()

    with col2:
        if st.button("❌ Cancel"):
            st.warning("Submission cancelled.")
            st.session_state.submitted = False
            st.session_state["pending_log"] = None
            st.rerun()


# ###############TRAINING PLAN SECTION#############################################


######METRICS########
# # LAYOUT COLOUMNS
from visuals import stats_table as stats

st.text("")

tab0, tab1, tab2, tab3, tab4 = st.tabs(
    [
        "✎📓Log Training",
        "📊 Stats",
        "🗓️ Program",
        "📘 Reference",
        "🏋🏻‍♂️ Strength Training",
    ]
)

# -------PULL DATA ONCE --------#
# -----load un cached when not submitting
if "just_submitted" not in st.session_state:
    st.session_state["just_submitted"] = False


if st.session_state["just_submitted"] == False:
    df = pulluc.get_runner_data()
    st.session_state["just_submitted"] = False
else:
    df = pullc.get_runner_data()

full_df = pd.DataFrame(df)


####----LOG TAB ------ ######


with tab0:

    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            ✎ᝰ.📓 Runner's Training Log 🏃‍♂️
        </div>
    """,
        unsafe_allow_html=True,
    )
    # st.markdown(
    #     """
    #     <div style="
    #         color:#3a3939;
    #         font-size: 16px;
    #         font-weight: 600;
    #         border-bottom: 1px solid #ccc;
    #         padding-bottom: 4px;
    #         margin-top: 20px;
    #         margin-bottom: 10px;">
    #         ✎ᝰ.📓Use this panel to input your training data.
    #     </div>
    # """,
    #     unsafe_allow_html=True,
    # )
    # st.sidebar.title("🏃‍♂️ Runner's Training Log")
    # st.sidebar.markdown("Use this panel to input your training data.")

    ####----- FORM --------------######
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
            sorted(
                [
                    "LSD Road@ Zone 2 Pace",
                    "LSD Trail@ Zone 2 Pace",
                    "Easy Run",
                    "Rest",
                    "Speed Work (Zone 4-5 x400M)",
                    "Strength Training",
                    "Cross Train",
                    "Tempo Run",
                    "Cooldown",
                    "Warm up",
                    "RACE DAY",
                ]
            ),
            index=None,
        )

        distance = st.number_input("Distance")

        # ----Generate Pace list ----#
        # Generate paces as strings
        pace_list = [
            f"{h:02}:{m:02}:{s:02}"
            for h in range(0, 2)
            for m in range(0, 15)
            for s in (range(0, 60))
        ]

        pace_list = [f"{m:02}:{s:02}" for m in range(0, 15) for s in (range(0, 60))]

        # display_paces = [f"{m:02}:{s:02}" for m in range(0, 15) for s in range(0, 60)]
        value_paces = [f"0:{m:02}:{s:02}" for m in range(0, 15) for s in range(0, 60)]
        pace_map = dict(zip(pace_list, value_paces))

        # Let user pick
        pace_display = st.selectbox("Select Pace (min:sec)", pace_list)
        pace_str = pace_map[pace_display]

        hr = st.number_input("HR (bmp)", min_value=0, max_value=220)
        cad = st.number_input("Cadence (spm)", min_value=0, max_value=200)
        rpe = st.slider("RPE", 0, 10, 1)
        # rpe2 = st.feedback(options="faces", key=int)
        shoe = st.selectbox(
            "Shoe",
            sorted(
                [
                    "Adidas Adizero SL2",
                    "Asics Purple",
                    "Boston 12",
                    "NB Rebel v3",
                    "Nike",
                    "Nike Winflo 10",
                    "Novablast 3",
                    "Novablast 4",
                    "Novablast 5",
                    "Asics GT1000-12",
                    "Adidas Pink",
                    "Reebok Float Ride Energy 4",
                    "Sketcher",
                    "Peppa Pig",
                    "Others (Inform Scott)",
                    "On Cloud ni Frau",
                ]
            ),
            index=None,
        )
        remarks = st.text_area(
            "Remarks", placeholder="How did the session feel?", key="remarks_input"
        )

        # Every form must have a submit button.

        submitted = st.form_submit_button("Submit Log", type="primary")

        if submitted:

            new_log = [
                time_stamp,  # Convert datetime to ISO string
                date.isoformat(),  # Convert date to ISO string
                (
                    act_selection if act_selection else ""
                ),  # Get first selected activity or empty
                distance,
                pace_str,
                hr,
                cad,
                rpe,
                shoe if shoe else "",  # Get first selected shoe or empty
                remarks,
                (
                    mem_selection if mem_selection else ""
                ),  # Get first selected member or empty
            ]
            st.session_state.pending_log = new_log
            confirm_submission(new_log)

    ####----- AFTER DIALOG --------------######
    if "submitted" not in st.session_state:
        st.session_state["submitted"] = False
    if "pending_log" not in st.session_state:
        st.session_state["pending_log"] = None

    if st.session_state.get("submitted") and st.session_state.get("submitted_data"):
        push.push_runner_data(st.session_state["submitted_data"])
        st.success("✅ Your activity log was successfully recorded! Latest entry:")
        st.write(st.session_state["submitted_data"])
        st.balloons()
        # Reset state so it doesn't rerun again
        st.session_state["submitted"] = False
        st.session_state["submitted_data"] = None


with tab1:

    # -----ALL STATS TABLE-------#
    # st.subheader("🏆 All-Time Highlights", divider="gray")

    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            🏆 All-Time Highlights
        </div>
    """,
        unsafe_allow_html=True,
    )
    stats.generate_matrix_member(full_df)

    # -------------------MEMBER FILTER  -----------------------#
    members = sorted(full_df["Member Name"].dropna().unique())
    members.insert(0, "All")  # Add 'All' option at the top
    selected_member = st.selectbox("Select Member to Filter", members, index=0)

    # Filter the DataFrame

    # Apply filtering
    if selected_member == "All":
        filtered_member_df = full_df
    else:
        filtered_member_df = full_df[full_df["Member Name"] == selected_member]

    # -------------------WEEK FILTER  -----------------------#

    weeks = sorted(filtered_member_df["Week"].dropna().unique())
    weeks.insert(0, "All")
    selected_weeks = st.multiselect("Select Week", weeks, default=["All"])

    if not selected_weeks or "All" in selected_weeks:
        filtered_df = filtered_member_df
    else:
        filtered_df = filtered_member_df[
            filtered_member_df["Week"].isin(selected_weeks)
        ]

    # # st.subheader(" ", divider="darkgreen")
    # # st.subheader(selected_member, divider="darkgreen")
    # ##--- MEMBER NAME HEADER ---- ##

    # st.markdown(
    #     f"""
    #     <div style="display: flex; justify-content: left; padding: 0.75rem;">
    #         <h3 style="color: #986868; margin: 0; text-decoration: underline;">👤 {selected_member}</h3>
    #     </div>
    #     """,
    #     unsafe_allow_html=True,
    # )

    with st.popover("⏱️ Open Race Predictor"):
        from models import race_predictor as rp

        st.markdown(
            """
            <div style="
                color:#3a3939;
                font-size: 20px;
                font-weight: 600;
                border-bottom: 1px solid #ccc;
                padding-bottom: 4px;
                margin-top: 20px;
                margin-bottom: 10px;">
                ⏱️ Predict Your Race Time</div>
        """,
            unsafe_allow_html=True,
        )
        ### --- race predictor ----##
        rp.race_predictor(filtered_member_df)

    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            📊 Overview & Stats
        </div>
    """,
        unsafe_allow_html=True,
    )

    # filter non running activity
    filtered_df = filtered_df[
        ~filtered_df["Activity"].isin(["Rest", "Cross Train", "Strength Training", 0])
    ]

    df = filtered_df.copy()

    # df["Moving_Time"] = pd.to_timedelta(df["Moving_Time"])
    # df["Pace"] = pd.to_timedelta(df["Pace"])
    metric_distance = int(df["Distance"].sum())

    # TOTAL MOVING TIME
    total_seconds = int(df["Moving_Time"].sum().total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    metric_movingtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # NUMBER OF RUNS
    metric_number_runs = int(df["Activity"].count())
    # AVG PACE
    avg_pace = df["Pace"].mean()
    if pd.isna(avg_pace):
        metric_pace = "N/A"
    else:
        metric_pace = f"{int(avg_pace.total_seconds() // 60):02d}:{int(avg_pace.total_seconds() % 60):02d}"

    # Days till race
    metric_tillrace = (datetime(2025, 12, 7) - datetime.today()).days

    # Display metrics in columns
    col0, col1, col2, col3 = st.columns(4)

    col0.metric(
        "Runs 🏃‍♀️‍➡️",
        value=metric_number_runs,
        label_visibility="visible",
        border=True,
    )
    col1.metric(
        "Total Distance 🏃💨KⓂ️",
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

    ###########CHARTS###########
    from visuals import sunburst as sb
    from visuals import combochart as cb
    from visuals import table as mt
    from visuals import line_polar as lp
    from visuals import donut as dt
    from visuals import wordcloud as wc

    # -----COMBO CHART WEEKLY-------#
    # st.subheader("📅🏃‍♂️ Weekly Distance vs. Pace", divider="gray")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            📅🏃‍♂️ Weekly Key Metrics</div>
    """,
        unsafe_allow_html=True,
    )
    cb.generate_combo(filtered_df)

    # -----COMBO CHART DAILY-------#
    with st.expander("Daily Distance vs. Pace"):
        # st.subheader("📈📍 Daily Distance vs. Pace", divider="gray")
        st.markdown(
            """
            <div style="
                color:#3a3939;
                font-size: 20px;
                font-weight: 600;
                border-bottom: 1px solid #ccc;
                padding-bottom: 4px;
                margin-top: 20px;
                margin-bottom: 10px;">
                📈📍 Daily Distance vs. Pace</div>
        """,
            unsafe_allow_html=True,
        )
        cb.generate_combo_daily(filtered_df)

    # -----SUN BURST-------#
    # st.subheader("👥📊 Activity Intensity", divider="gray")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            👥📊 Activity Intensity</div>
    """,
        unsafe_allow_html=True,
    )
    sb.generate_bubble_chart(filtered_df)

    # -----LINE POLAR-------#
    # st.subheader("", divider="gray")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            ⚖️📊 Activity Comparison</div>
    """,
        unsafe_allow_html=True,
    )
    lp.generate_linepolar(filtered_df)

    # -----DONUT-------#
    # st.subheader("", divider="gray")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
             👟📈! Shoe Mileage</div>
    """,
        unsafe_allow_html=True,
    )
    dt.generate_donut_chart(filtered_df)

    # -----WORDCLOUD-------#
    # st.subheader("", divider="gray")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
             🏃💬 Runner's Word Cloud</div>
    """,
        unsafe_allow_html=True,
    )
    wc.generate_wordcloud(filtered_df)

    # -----ALL ACTIVITY TABLE-------#
    # st.subheader("🗂️ Activity Reference", divider="gray")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            🗂️ Activity Reference</div>
    """,
        unsafe_allow_html=True,
    )
    mt.generate_matrix(filtered_member_df)


with tab2:
    # st.header("🗓️💪 Your Training Plan", divider="blue")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 20px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            🗓️💪 Your Training Plan</div>
    """,
        unsafe_allow_html=True,
    )
    # with st.expander("View Training Program"):
    prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1748190509&single=true"
    components.iframe(
        prog_sheet,
        width=500,
        height=1000,
    )

with tab3:
    from visuals import referencetab as ref

    ref.ref_tab()

with tab4:
    from visuals import strength_ref as sref

    sref.general_str_ref()
