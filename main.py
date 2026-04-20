import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time as tm
from datetime import time, datetime
import data.push_data as push
from data import read_data_cached as pullc
from data import read_data_uncached as pulluc
from zoneinfo import ZoneInfo
import traceback


# import data.read_data_local as local
import numpy as np
from visuals import racedaycounter as rdc


st.set_page_config(
    page_title="StillHere",
    page_icon="🪨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# rdc.raceday_counter_2()


Welcome_msg = "The boulder will roll back down again — you already know that. You just have to keep showing up. And you did. That's enough."

# st.markdown("🪨 · · · ✦ · · · 🪨")
st.text("")

st.markdown(
    f"""
    <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                background-color: rgba(0, 0, 0, 0); border-left: 4px solid #8b5a2b; margin-bottom: 1rem;">
        <p style="font-size: 1.1rem; color: #3b2f2a; font-style: italic; margin: 0;">
            {Welcome_msg}
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Welcome_msg = "The boulder will roll back down again — you already know that. You just have to keep showing up. And you did. That’s enough."
# st.text("")

# st.markdown(
#     f"""
#     <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
#                 background-color: rgba(0, 0, 0, 0); border-left: 4px solid #2e8b57; margin-bottom: 1rem;">
#         <p style="font-size: 1.1rem; color: #2f3e46; font-style: italic; margin: 0;">
#             {Welcome_msg}
#         </p>
#     </div>
#     """,
#     unsafe_allow_html=True,
# )

col1, col2 = st.columns(2)

with col2:
    with st.popover("💡 How to Use This Page"):
        st.markdown(
            """
            <p>Welcome! Here's how to navigate this page:</p>
            <ul>
                <li>📓 <strong>Logs</strong>: Edit / Log your training.</li>
                <li>📊 <strong>Stats</strong>: Track your progress.</li>
                <li>🗓️ <strong>Program</strong>: Your marathon plan.</li>
                <li>📘 <strong>Activities</strong>: Learn about your activities.</li>
                <li>🏋🏻‍♂️ <strong>Strength</strong>: Your strength workouts.</li>
                <li>🎯 <strong>Remarks</strong>: Your Weekly Remarks.</li>
                <li>💗 <strong> HR Zones.</li>
                
            </ul>
            <p><em>Tip:</em> If switching apps (Strava, Garmin, etc.),the app will try to rerun, wait for the app to load and continue with your log.</p>
            <p><strong>PS:</strong> If it lags, don't worry — it's just *thinking really hard*. 🧠💻</p>
            """,
            unsafe_allow_html=True,
        )
with col1:
    with st.popover("Coach"):
        # Initialize session state
        if "authenticated" not in st.session_state:
            st.session_state.authenticated = False

        if "memberverified" not in st.session_state:
            st.session_state.memberverified = False

        # Passcode input
        passcode = st.text_input("Passcode", type="password")

        if st.button("Submit"):
            if passcode == "8465":  # Your secret passcode
                st.session_state.authenticated = True
            elif passcode == "0525":  # Your secret passcode
                st.session_state.memberverified = True
            else:
                st.session_state.authenticated = False
                st.error("Wrong passcode!")

            # Radio button that shows/hides based on authentication
        options = ["🗓️ Program", "📊 Stats", "📘 Activities", "📓Log /  Edit Log"]

        if st.session_state.authenticated:
            options.append("📊 Stats")
            options.append("📘 Activities")
            options.append("🏋🏻‍♂️ Str Training")
            options.append("💗 HR Zones")
            options.append("📓Log /  Edit Log")
            options.append("🎯 Remarks")
            options.append("🔄 Strava Sync")  # Add the hidden option

        if st.session_state.memberverified:
            options.append("📊 Stats")
            options.append("📘 Activities")
            options.append("📓Log /  Edit Log")
        # Add the hidden option

tabs = st.radio("Choose a Section:", options, horizontal=True, index=0)

# element_name = "Log Your Activity Here"


# ----------------- Confirmation Dialog -----------------
@st.dialog("Confirm Run Entry?")
def confirm_submission(new_log):
    st.write("Are you sure you want to submit this entry?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, Submit"):
            # Simulate push to backend
            st.session_state["submitted_data_run"] = new_log
            # st.session_state["submitted_data_other"] = new_log_other
            st.success("✅ Activity Recorded!")
            st.session_state["submitted_run"] = True
            # st.session_state["submitted_other"] = True
            st.session_state["pending_log"] = None
            # st.balloons()
            st.rerun()

    with col2:
        if st.button("❌ Cancel"):
            st.warning("Submission cancelled.")
            st.session_state.submitted = False
            st.session_state["pending_log"] = None
            st.rerun()


@st.dialog("Confirm Other Activity Entry?")
def confirm_submission_other(new_log_other):
    st.write("Are you sure you want to submit this entry?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, Submit"):
            # Simulate push to backend
            st.session_state["submitted_data_other"] = new_log_other
            # st.success("✅ Activity Recorded!")
            st.session_state["submitted_other"] = True
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


# tabs = st.radio(
#     "Choose a Section: ",
#     [
#         "🗓️ Program",
#         "📊 Stats",
#         # "📘 Activities",
#         # "🏋🏻‍♂️ Str Training",
#         # "🎯 Remarks",
#         # "💗 HR Zones",
#         "🔄 Strava Sync",
#         # "📓Log /  Edit Log",
#     ],
#     horizontal=True,
#     index=0,
# )


# -------PULL DATA ONCE --------#
# -----load un cached when not submitting

##################################################################
# if "just_submitted" not in st.session_state:
#     st.session_state["just_submitted"] = False


# if st.session_state["just_submitted"] == False:
#     df = pulluc.get_runner_data()
#     st.session_state["just_submitted"] = False
# else:
#     df = pullc.get_runner_data()

##########################################################################

if tabs != "🗓️ Program":

    if st.session_state.get("just_submitted", False):
        df = pulluc.get_runner_data()  # Uncached for fresh data after submission
        st.session_state["just_submitted"] = False
    else:
        df = pullc.get_runner_data()  # Cached for normal viewing
        if df is None:
            # Fallback to empty dataframe or previous data
            df = pd.DataFrame()

    #############################################################################

    full_df = pd.DataFrame(df)

#################################----LOG TAB ------ ################################

if tabs == "📓Log":  ##LOG

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
    st.markdown(
        """
        <div style="
            color:#f15950;
            font-size: 15px;
            font-weight: 800;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            *Click Box Below to enter Log
        </div>
    """,
        unsafe_allow_html=True,
    )
    mem_selection = st.selectbox(
        "Members",
        ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"],
        index=None,
        placeholder="Select Member",
        key="shared_member",
    )
    # member_name = st.markdown(f"Select Member", {mem_selection})
    sg_now = datetime.now(ZoneInfo("Asia/Singapore"))
    now_ = datetime.now()

    date = st.date_input("Date of Activity", value=now_.date(), key="shared_date")

    ###----- FORM RUN--------------######
    with st.expander("Log Run"):
        with st.form("activity_log", clear_on_submit=True, border=True):

            # Activity list
            act_selection_run = st.selectbox(
                "Activity",
                # sorted(
                [
                    "Easy Run",
                    "Aerobic Run",
                    "Tempo Run",
                    "Cooldown",
                    "Warm up",
                    "Speed Work (Zone 4-5 x400M)",
                    "LSD Road@ Zone 2 Pace",
                    "LSD Trail@ Zone 2 Pace",
                    "RACE DAY",
                ],
                # ),
                index=None,
                placeholder="Select an activity",
                key="activity_run",
            )

            distance_run = st.number_input(
                "Distance", placeholder="Enter distance", key="distance_run"
            )

            # Add default value at the beginning
            default_pace = "00:00:00"

            pace_list = [f"{m:02}:{s:02}" for m in range(0, 15) for s in (range(0, 59))]

            # display_paces = [f"{m:02}:{s:02}" for m in range(0, 15) for s in range(0, 60)]
            value_paces = [
                f"0:{m:02}:{s:02}" for m in range(0, 15) for s in range(0, 59)
            ]
            pace_map = dict(zip(pace_list, value_paces))
            pace_display = st.selectbox(
                "Select Pace (min:sec) *type in your pace and select",
                pace_list,
                index=0,
                key="pace_run",
            )

            pace_str_run = pace_map[pace_display]

            hr_run = st.number_input(
                "HR (bmp)", min_value=0, max_value=220, key="hr_run"
            )
            cad_run = st.number_input(
                "Cadence (spm)", min_value=0, max_value=200, key="cad_run"
            )
            rpe_run = st.slider("RPE", 0, 10, 0, key="rpe_run")
            # rpe2 = st.feedback(options="faces", key=int)
            shoe_run = st.selectbox(
                "Shoe",
                sorted(
                    [
                        "Adidas Adizero SL2",
                        "Adidas Adizero SL",
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
                        "Superblast 2",
                        "Peak Cushy",
                        "Peppa Pig",
                        "Others (Inform Scott)",
                        "On Cloud ni Frau",
                        "Pink Nimbus 27",
                    ]
                ),
                index=None,
                key="shoe_run",
            )
            remarks_run = st.text_area(
                "Remarks", placeholder="How did the session feel?", key="remarks_run"
            )

            submitted_run = st.form_submit_button("Run: Submit Log", type="primary")

            unique_key = f"{date}|{mem_selection}|{act_selection_run}"

            if submitted_run:
                time_stamp_ = datetime.now()
                time_stamp = time_stamp_.strftime("%Y-%m-%d")

                new_log = [
                    unique_key,
                    time_stamp,  # Convert datetime to ISO string
                    date.isoformat(),  # Convert date to ISO string
                    (
                        act_selection_run if act_selection_run else ""
                    ),  # Get first selected activity or empty
                    distance_run,
                    pace_str_run,
                    hr_run,
                    cad_run,
                    rpe_run,
                    shoe_run if shoe_run else "",  # Get first selected shoe or empty
                    remarks_run,
                    (mem_selection if mem_selection else ""),
                    None,  # Duration_other,  # Get first selected member or empty
                ]
                st.session_state.pending_log = new_log
                # st.session_state.submitted_run = True

                confirm_submission(new_log)

                ####----- AFTER DIALOG WORKING --------------######
            if "submitted_run" not in st.session_state:
                st.session_state["submitted_run"] = False
            if "pending_log" not in st.session_state:
                st.session_state["pending_log"] = None

            if st.session_state.get("submitted_run") and st.session_state.get(
                "submitted_data_run"
            ):
                push.push_runner_data(st.session_state["submitted_data_run"])
                st.success("✅ Your Run was successfully recorded! Latest entry:")
                st.write(st.session_state["submitted_data_run"])
                st.balloons()
                # Reset state so it doesn't rerun again
                st.session_state["submitted_run"] = False
                st.session_state["submitted_data_run"] = None

    with st.expander("Log Other Activity"):
        with st.form("activity_log_other", clear_on_submit=True, border=True):
            time_stamp_ = datetime.now()
            time_stamp = time_stamp_.strftime("%Y-%m-%d")

            # Activity list
            act_selection_other = st.selectbox(
                "Activity",
                # sorted(
                [
                    "WeightTraining",
                    "Yoga",
                    "Cross Train",
                    "Rest",
                    "Pilates",
                    "Walk",
                ],
                # ),
                index=None,
                placeholder="Select an activity",
            )

            hr_other = st.number_input("HR (bmp)", min_value=0, max_value=220)

            duration_list = [
                f"{h:02}:{m:02}:{s:02}"
                for h in range(0, 10)
                for m in (range(0, 59))
                for s in (range(0, 59))
            ]

            # display_duration = [f"{m:02}:{s:02}" for m in range(0, 15) for s in range(0, 60)]
            value_duration = [
                f"{h:02}:{m:02}:{s:02}"
                for h in range(0, 10)
                for m in range(0, 59)
                for s in (range(0, 59))
            ]
            duration_map = dict(zip(duration_list, value_duration))
            duration_display = st.selectbox(
                "Select duration (hour:min:sec) *type in your pace and select",
                duration_list,
                index=0,
            )

            duration_other = duration_map[duration_display]

            rpe_other = st.slider("RPE", 0, 10, 0)
            # rpe2 = st.feedback(options="faces", key=int)
            remarks_other = st.text_area(
                "Remarks",
                placeholder="How did the session feel?",
                key="remarks_input_other",
            )

            unique_key_other = f"{date}|{mem_selection}|{act_selection_other}"
            # Every form must have a submit button.

            submitted_other = st.form_submit_button("Other: Submit Log", type="primary")

            if submitted_other:

                new_log_other = [
                    unique_key_other,
                    time_stamp,  # Convert datetime to ISO string
                    date.isoformat(),  # Convert date to ISO string
                    (
                        act_selection_other if act_selection_other else ""
                    ),  # Get first selected activity or empty
                    None,  # dist
                    None,  # pace
                    hr_other,
                    None,  # cad
                    rpe_other,
                    None,  # shoes
                    remarks_other,
                    (
                        mem_selection if mem_selection else ""
                    ),  # Get first selected member or empty
                    duration_other,
                ]
                st.session_state.pending_log_other = new_log_other
                # st.session_state.submitted_other = True
                confirm_submission_other(new_log_other)

                ####----- AFTER DIALOG OTHER WORKING --------------######
            if "submitted_other" not in st.session_state:
                st.session_state["submitted_other"] = False
            if "pending_log_other" not in st.session_state:
                st.session_state["pending_log_other"] = None

            if st.session_state.get("submitted_other") and st.session_state.get(
                "submitted_data_other"
            ):
                push.push_runner_data(st.session_state["submitted_data_other"])
                st.success(
                    "✅ Your Other Activity was successfully recorded! Latest entry:"
                )
                st.write(st.session_state["submitted_data_other"])
                st.balloons()
                # Reset state so it doesn't rerun again
                st.session_state["submitted_other"] = False
                st.session_state["submitted_data_other"] = None

    with st.expander("Edit Log"):
        from data import edit

        edit.edit_log(full_df)

    st.write("After Strava Sync:")

    with st.expander(
        "Enter User Fields (*RPE, Shoes, Remarks, Type of Activity-for Run*)"
    ):
        from data import user_field

        user_field.edit_user_fields(full_df)

    # with st.expander(
    #     "Bulk Enter User Fields (*RPE, Shoes, Remarks, Type of Activity-for Run*)"
    # ):
    #     from data import user_field

    #     user_field.bulk_edit_user_fields_new(full_df)

if tabs == "📊 Stats":  # STATS

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

    ### --- Capture Year --- ####
    full_df["Date_of_Activity"] = pd.to_datetime(
        full_df["Date_of_Activity"], errors="coerce"
    )
    full_df["year"] = full_df["Date_of_Activity"].dt.year

    _years = sorted(full_df["Date_of_Activity"].dt.year.dropna().unique().tolist())
    _years.insert(0, "All")
    last_index = len(_years) - 1

    selected_year = st.selectbox("Select Year to Filter", _years, index=last_index)

    ### All activity - but not filtered from app selections

    # Apply filtering with all years
    if selected_year == "All":
        filtered_member_df = full_df
    else:
        full_df = full_df[full_df["year"] == selected_year]

    filtered_df_full_activity = full_df[
        ~full_df["Activity"].isin(
            [
                "Rest",
                "Cross Train",
                "Strength Training",
                "WeightTraining",
                "Yoga",
                0,
                "",
                "Walk",
                "Pilates",
                "Ride",
                "Cooldown",
                "Warm up",
            ]
        )
    ]

    stats.generate_matrix_member(filtered_df_full_activity)

    # -------------------MEMBER FILTER  -----------------------#
    members = sorted(full_df["Member Name"].dropna().unique())
    members_count = len(members)

    members.insert(0, "All")  # Add 'All' option at the top
    selected_member = st.selectbox(
        "Select Member to Filter", members, index=members_count
    )
    # selected_member = "Scott"

    # Filter the DataFrame

    # Apply filtering
    if selected_member == "All":
        filtered_member_df = full_df
    else:
        filtered_member_df = full_df[full_df["Member Name"] == selected_member]

    # -------------------WEEK FILTER  -----------------------#

    weeks = sorted(filtered_member_df["Week"].dropna().unique())
    weeks.insert(0, "All")
    selected_weeks = st.multiselect("Select Week(s) to Compare", weeks, default=["All"])

    if not selected_weeks or "All" in selected_weeks:
        filtered_df = filtered_member_df
    else:
        filtered_df = filtered_member_df[
            filtered_member_df["Week"].isin(selected_weeks)
        ]

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

        rp.race_predictor(filtered_df)

    #########################--- ALL TIME STATS TABLE ----#######################
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

    # filtered_df_all_activity = filtered_df
    # filter non running activity

    filtered_df_withnonrun = filtered_df.copy()
    filtered_df_all_run = filtered_df[
        ~filtered_df["Activity"].isin(
            [
                "Rest",
                "Cross Train",
                "Strength Training",
                "WeightTraining",
                "Yoga",
                "",
                0,
                "Pilates",
                "Walk",
                "Ride",
                "Warm up",
                "Cooldown",
            ]
        )
    ]

    filtered_df_all_non_run = filtered_df[
        filtered_df["Activity"].isin(
            [
                "Rest",
                "Cross Train",
                "Strength Training",
                "WeightTraining",
                "Yoga",
                0,
                "",
                "Walk",
                "Pilates",
                "Ride",
                "Warm up",
                "Cooldown",
            ]
        )
    ]

    filtered_df_all_run = filtered_df_all_run.copy()

    # df["Moving_Time"] = pd.to_timedelta(df["Moving_Time"])
    # df["Pace"] = pd.to_timedelta(df["Pace"])
    metric_distance = int(filtered_df_all_run["Distance"].sum())

    # TOTAL MOVING TIME
    total_seconds = int(filtered_df_all_run["Moving_Time"].sum().total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    metric_movingtime = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    # NUMBER OF RUNS
    metric_number_runs = int(filtered_df_all_run["Activity"].count())
    # AVG PACE
    avg_pace = filtered_df_all_run["Pace"].mean()
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
    with st.expander("View Weekly Key Metrics", expanded=True):
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
        cb.generate_combo(filtered_df_all_run)
        cb.generate_running_duration_chart_new(filtered_df_all_run)

    with st.expander("View Supplimentary Metrics", expanded=True):
        cb.generate_combo_supplimentary_new(filtered_df_all_non_run)

    with st.expander("View Other Charts", expanded=True):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("##### 🫧 Activity Intensity Bubble Chart")
            bubble_fig = sb.generate_bubble_chart_new(filtered_df_all_run)
            st.plotly_chart(bubble_fig, use_container_width=True, key="bubble_chart")

        with col2:
            st.markdown("##### 👟 Distance by Shoe")
            donut_fig = dt.generate_donut_chart_new(filtered_df_all_run)
            st.plotly_chart(donut_fig, use_container_width=True, key="donut_chart")

        with col3:
            st.markdown("##### 🏃💬 Runner's Word Cloud")
            wc.generate_wordcloud_new(filtered_df_withnonrun)

    with st.expander("View Detailed Entries", expanded=True):

        st.subheader("🗂️ Activity Reference", divider="gray")

        # # Run section with expander for cleaner UI
        # with st.expander("🏃‍♀️ Run Activities", expanded=True):
        mt.generate_matrix_new(filtered_df_all_run)

        # # Other activities section
        # with st.expander("🤸‍♀️ Cross-Training & Recovery", expanded=True):
        mt.generate_matrix_new(filtered_df_all_non_run)


if tabs == "🗓️ Program":  ##TRAINING PLAN ##

    # st.header("🗓️💪 Your Training Plan", divider="blue")
    st.markdown(
        """
        <div style="
            color:#3a3939;
            font-size: 24px;
            font-weight: 600;
            border-bottom: 1px solid #ccc;
            padding-bottom: 4px;
            margin-top: 20px;
            margin-bottom: 10px;">
            🗓️💪 Your Training Plan</div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    ##### 📋 Activity Type Abbreviations

    **AR** – Active Recovery | **CT** – Cross Train | **E** – Easy Run  
    **GA** – General Aerobic | **I** – Interval | **LSD** – Long Slow Distance  
    **LT** – Lactate Threshold | **MLR** – Medium Long Run | **MP** – Marathon Pace  
    **R** – Recovery Run | **S** – Speedwork | **STR** – Strength Training | **T** – Tempo
    """
    )

    with st.expander("Base Building 2026"):
        # with st.expander("View Training Program"):
        prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1748190509&single=true"
        components.iframe(
            prog_sheet,
            height=500,
            width=1600,
        )

    with st.expander("Scott Program"):
        prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1680121528&single=true"
        components.iframe(
            prog_sheet,
            height=500,
            width=1600,
        )

    with st.expander("Chona Program"):
        # st.subheader("Chona")
        prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1489038442&single=true"
        components.iframe(
            prog_sheet,
            height=500,
            width=1600,
        )


if tabs == "📘 Activities":  ##STR WORK
    from visuals import referencetab as ref

    ref.ref_tab()

if tabs == "🏋🏻‍♂️ Str Training":  # REFERENCE
    from visuals import strength_ref as sref

    sref.general_str_ref()

    # --------filter df

# if tabs == "🎯 Remarks":  # REMARKS
#     from visuals import weekly_remarks as wr
#     from visuals import stats_table as stats

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
#             🎯 Weekly Remarks
#         </div>
#     """,
#         unsafe_allow_html=True,
#     )

#### --- ACTIVATE ONLY DURING WEEKLY REVIEWS -----###
##-- WEEKLY  CHART -- ##
# coach_df = (
#     full_df
#     if selected_weeks == "All"
#     else full_df[full_df["Week"].isin(selected_weeks)]
# )
#
# list_weeks = sorted(
#     filtered_df["Week"].dropna().unique(),
#     key=lambda x: int("".join(filter(str.isdigit, x))),
# )
# # list_weeks = sorted(full_df["Week"].dropna().unique())
# latest_week = list_weeks[-1]

# latest_week = "W 3"
# coach_df = filtered_df[filtered_df["Week"] == (latest_week)]

# st.markdown(f"""## 🏁 Week: {latest_week}""")

# # st.write(filtered_df.columns)

# # ####----WEEKLY SUMMARY TABLE --- ###
# stats.generate_matrix_coach(coach_df)

# wr.weekly_remarks()

if tabs == "💗 HR Zones":  ##SCOTTS CORNER

    # with st.expander("Scott Program"):
    #     st.markdown(
    #         """
    #             <div style="
    #                 color:#3a3939;
    #                 font-size: 20px;
    #                 font-weight: 450;
    #                 border-bottom: 1px solid #ccc;
    #                 padding-bottom: 4px;
    #                 margin-top: 20px;
    #                 margin-bottom: 10px;">
    #                 🗓️ Training Plan</div>
    #         """,
    #         unsafe_allow_html=True,
    #     )
    #     prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1680121528&single=true"
    #     components.iframe(
    #         prog_sheet,
    #         height=500,
    #         width=600,
    #     )

    # with st.expander("Chona Progaram"):
    #     st.subheader("Chona")
    #     prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1489038442&single=true"
    #     components.iframe(
    #         prog_sheet,
    #         height=500,
    #         width=600,
    #     )

    ####CUSTOM ZONES####
    col1, col2 = st.columns(2)
    with col1:  ###SCOTT ZONES####
        with st.expander("Your Zones : Scott"):
            st.subheader(":blue[Scott]", divider=True)
            st.markdown(
                """
                ### 🏃‍♂️ Pfitzinger Heart Rate Training Zones
                ### As of July 14, 2025 : Transition Week 11

                Your Resting HR: **55 bpm**  
                Your Max HR: **192 bpm** as of 16-Jul-2025  
                Heart Rate Reserve (HRR): **136 bpm**

                **🏷️ Zones**
                - 🟢 Zone 2: Recovery / Easy ➡️**Target HR: 118-130 bpm**  🔥RPE : **2-4**
                - 🔵 Zone 2.5–3: Aerobic / General ➡️ **Target HR: 130-140 bpm**  🔥RPE : **3-5**
                - 🟡 Zone 3: Long Run ➡️ **Target HR: 135-145 bpm**  🔥RPE : **3-6**
                - 🔶 Zone 4: Marathon Pace ➡️ **Target HR: 145-155**  🔥RPE : **5-7**
                - 🔴 Zone 4+: Threshold / Tempo ➡️ **Target HR: 156-170 bpm**  🔥RPE : **7-8**
                - 🟣 Zone 5: VO₂ Max ➡️ **Target HR: 171-187 bpm**   🔥RPE : **9-10**                   ⭐⭐⭐☆ – Use sparingly; high injury risk if overused
                """,
                unsafe_allow_html=True,
            )
    with col2:  ###CHONA ZONES ####
        with st.expander("Your Zones : Chona"):
            st.subheader(":green[Chona]", divider=True)
            st.markdown(
                """
                    ### 🏃‍♂️ Effort-Based Zones
                    ### As of July 14, 2025 : Transition Week 11

                    Your Resting HR: **56 bpm**  
                    Your Max HR: **190 bpm** as of 16-Jul-2025  
                    Heart Rate Reserve (HRR): **134 bpm**

                    **🏷️ Zones**
                    - 🟢 Zone 2: Recovery / Easy ➡️**Target HR: 140-150 bpm**  🔥RPE : **2-4**
                    - 🔵 Zone 2.5–3: Aerobic / General ➡️ **Target HR: 150-160 bpm**  🔥RPE : **3-5**
                    - 🟡 Zone 3: Long Run ➡️ **Target HR: 145-165 bpm**  🔥RPE : **3-6**
                    - 🔶 Zone 4: Marathon Pace ➡️ **Target HR: TBD**  🔥RPE : **5-7**
                    - 🔴 Zone 4+: Threshold / Tempo ➡️ **Target HR: 165-175 bpm**  🔥RPE : **7-8**
                    - 🟣 Zone 5: VO₂ Max ➡️ **Target HR: 178-190 bpm**   🔥RPE : **8-10**                   ⭐⭐⭐☆ – Use sparingly; high injury risk if overused

                    ---
                    """,
                unsafe_allow_html=True,
            )


if tabs == "🔄 Strava Sync":  ##strava sync plus cleanup before push

    days_back = st.slider("Days to look back", 2, 365, 2)
    days_back = int(days_back)

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("🔄 Sync to Google Sheets", type="primary"):
            st.session_state.sync_triggered = True

    # Fetch Strava data
    import data.fetch_strava as fs

    activities = fs.fetch_all_activities(days_back)

    def clean_activity_data(act):
        """Clean and convert numeric values for a single activity"""

        # Helper function to safely convert to float
        def to_float(value, default=0):
            try:
                return float(value) if value is not None else default
            except (ValueError, TypeError):
                return default

        # Helper function to safely convert to string
        def to_str(value, default=""):
            if value is None:
                return default
            try:
                return str(value)
            except:
                return default

        # Extract and clean date
        start_date = act.get("start_date_local")
        if start_date and "T" in start_date:
            date_part = start_date.split("T")[0]
        else:
            date_part = ""

        return {
            "TimeStamp": date_part,
            "Date_of_Activity": date_part,
            "Activity": to_str(act.get("sport_type")),
            "Distance": to_float(act.get("distance")) / 1000,  # Convert to km
            "Pace": to_float(act.get("average_speed")),
            "HR (bpm)": to_float(act.get("average_heartrate")),
            "Cadence (steps/min)": to_float(act.get("average_cadence")) * 2,
            "Member Name": to_str(act.get("athlete_name", "Unknown")),
            "Duration": to_float(act.get("moving_time")),
        }

    def convert_speed_to_pace(speed_mps):
        """Convert meters per second to min/km pace format (H:MM:SS or MM:SS)"""
        if speed_mps <= 0:
            return 0

        # Convert m/s to min/km
        pace_seconds_per_km = 1000 / speed_mps

        # hours = int(pace_seconds_per_km // 3600)
        # minutes = int((pace_seconds_per_km % 3600) // 60)
        # seconds = int(pace_seconds_per_km % 60)

        # if hours > 0:
        #     return f"{hours}:{minutes:02d}:{seconds:02d}"
        # else:
        #     return f"{hours}:{minutes:02d}:{seconds:02d}"

        return pace_seconds_per_km / 86400

    def convert_speed_to_pace_string(speed_mps):
        """Convert meters per second to min/km pace format (H:MM:SS or MM:SS)"""
        if speed_mps <= 0:
            return "00:00:00"

        # Convert m/s to min/km
        pace_seconds_per_km = 1000 / speed_mps

        hours = int(pace_seconds_per_km // 3600)
        minutes = int((pace_seconds_per_km % 3600) // 60)
        seconds = int(pace_seconds_per_km % 60)

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def convert_seconds_to_time(total_seconds):
        """Convert seconds to HH:MM:SS format"""
        if total_seconds <= 0:
            return "00:00:00"

        # hours = int(total_seconds // 3600)
        # minutes = int((total_seconds % 3600) // 60)
        # seconds = int(total_seconds % 60)

        # return f"{hours}:{minutes:02d}:{seconds:02d}"

        return total_seconds / 86400

    def convert_seconds_to_time_string(total_seconds):
        """Return formatted time string that looks correct"""
        if total_seconds <= 0:
            return "00:00:00"

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    if activities:
        cleaned_activities = [clean_activity_data(act) for act in activities]
        strava_df = pd.DataFrame(cleaned_activities)

        # Define user mapping dictionary so athlete name
        USER_MAPPING = {
            29563579: "Scott",
            # Add more users here as needed
            # 12345678: "John",
            # 87654321: "Sarah",
        }

        # Apply conversions
        # Now apply conversions - values are guaranteed to be numbers

        strava_df["TimeStamp"] = pd.to_datetime(strava_df["TimeStamp"]).dt.date
        strava_df["Date_of_Activity"] = pd.to_datetime(
            strava_df["Date_of_Activity"]
        ).dt.date
        strava_df["Distance"] = (strava_df["Distance"]).round(2)

        ######## Convert the Pace column to numeric first, forcing errors to NaN######
        strava_df["Pace"] = pd.to_numeric(strava_df["Pace"], errors="coerce")

        # Fill NaN values with 0
        strava_df["Pace"] = strava_df["Pace"].fillna(0)
        #########################################################################
        strava_df["Pace"] = strava_df["Pace"].apply(
            lambda x: convert_speed_to_pace_string(x) if x > 0 else "00:00:00"
        )
        strava_df["HR (bpm)"] = strava_df["HR (bpm)"].round().astype(int)
        strava_df["Cadence (steps/min)"] = (
            (strava_df["Cadence (steps/min)"]).round().astype(int)
        )
        strava_df["Member Name"] = strava_df["Member Name"].apply(
            lambda x: x.get("id", "") if isinstance(x, dict) else x
        )

        strava_df["Duration"] = pd.to_numeric(
            strava_df["Duration"], errors="coerce"
        ).fillna(0)

        strava_df["Duration"] = strava_df["Duration"].apply(
            convert_seconds_to_time_string
        )

        strava_df["UniqueKey"] = (
            strava_df[["Date_of_Activity", "Member Name", "Activity", "HR (bpm)"]]
            .astype(str)
            .agg("|".join, axis=1)
        )
        st.dataframe(strava_df)

        ######SYNC ACTIVATION#########
        if st.session_state.get("sync_triggered", False):
            # from data import push_data

            st.divider()
            st.subheader("🔄 Syncing to Google Sheets...")

            with st.spinner("Pushing activities to Google Sheets..."):
                success_count, error_count = push.push_strava_data_to_sheet(strava_df)

            if success_count > 0:
                st.success(
                    f"✅ Successfully pushed {success_count} activities to Google Sheets!"
                )

            if error_count > 0:
                st.error(f"❌ Failed to push {error_count} activities")

            # Reset the trigger
            st.session_state.sync_triggered = False
