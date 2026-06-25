import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time as tm
from datetime import time, datetime
import data.push_data as push
import data.push_supa as pushsupa

from data import read_data_cached as pullc
# from data import read_data_uncached as pulluc
from zoneinfo import ZoneInfo
import traceback

userlist = [ "Guest","Scott", "Chona", "Aiza", "Fraulein", "Alvin", "Lead", "Maxine"]

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# === LOGIN CHECK ===
if not st.session_state.authenticated:
    # Use wide layout for login page
    st.set_page_config(page_title="StillHere", page_icon="🪨", layout="wide")
    
    st.subheader("🪨 StillHere",anchor=False)
    Welcome_msg = "The boulder will roll back down again — you already know that. You just have to keep showing up. And you did. That's enough."

    st.markdown(
        f"""
        <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                    background-color: rgba(0, 0, 0, 0); border-left: 2px solid #8b5a2b; margin-bottom: 1rem;">
            <p style="font-size: 1rem; color: #3b2f2a; font-style: italic; margin: 0;">
                {Welcome_msg}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.text("")
    # st.markdown("##### Select your profile to continue")
    
    users = userlist
    
    selected_user = st.selectbox("Select your profile to continue", [""]+users, index=0)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Login", type="primary", use_container_width=True):
            if selected_user:
                st.session_state.authenticated = True
                st.session_state.current_user = selected_user
                st.rerun()
            else:
                st.error("Please select a user first")
    
    st.stop()



# Sidebar with member selector
with st.sidebar:
    st.markdown("### 🏃‍♂️ Profile")
    
    # Member selector dropdown
    users = userlist
    selected_member = st.selectbox(
        "Select Member",
        users,
        index=users.index(st.session_state.current_user) if st.session_state.current_user in users else 0,
        key="member_selector",
        label_visibility="collapsed"
    )
    
    # Update session state if changed
    if selected_member != st.session_state.current_user:
        st.session_state.current_user = selected_member
        st.rerun()
    
    st.divider()
    
    # Display current user
    st.markdown(f"**Current:** {st.session_state.current_user}")
    
    st.info("💡 Tip: Click the '⋮' menu in the top-right to switch between light/dark theme")

selected_user = st.session_state.current_user


# Rest of your tabs and content...
    
import numpy as np
from visuals import racedaycounter as rdc
# Your main app content


st.subheader(f"Welcome, {st.session_state.current_user}! 🏃‍♂️")
st.markdown(":blue[*Need to switch accounts ? Tap the » icon in the top-left corner*]")
col1, col2 = st.columns(2)

with col2:
    
    with st.popover("💡 How to Use This Page"):
        st.markdown(
            """
            <p>Welcome! Here's how to navigate this page:</p>
            <ul>
                <li>🗓️ <strong>Program</strong>: Your marathon training plan.</li>
                <li>🗺️ <strong> Your Runs</strong>: View Recent Runs.</li>
                <li>📊 <strong>Stats</strong>: Track your weekly progress.</li>
                <li>📓 <strong>Logs</strong>: Edit your training entries.</li>
            </ul>
            <p><strong>PS:</strong> If it lags, don't worry — it's just *thinking really hard*. 🧠💻</p>
            """,
            unsafe_allow_html=True,
        )
with col1:
    # Initialize session state
    if "coachauthenticated" not in st.session_state:
        st.session_state.coachauthenticated = False

    with st.popover("Coach"):
        # Initialize session state
        if "authenticated" not in st.session_state:
            st.session_state.coachauthenticated = False

        if "memberverified" not in st.session_state:
            st.session_state.memberverified = False

        # Passcode input
        passcode = st.text_input("Passcode", type="password")

        if st.button("Submit"):
            if passcode == "8465":  # Your secret passcode
                st.session_state.coachauthenticated = True
            elif passcode == "0525":  # Your secret passcode
                st.session_state.memberverified = True
            else:
                st.session_state.coachauthenticated = False
                st.error("Wrong passcode!")

            # Radio button that shows/hides based on authentication
        options = ["🗓️ Program", "🗺️ Your Runs", "📊 Stats","📓Log"]

        if st.session_state.coachauthenticated:
            options.append("🏋🏻‍♂️ Str Training")
            options.append("💗 HR Zones")
            options.append("📓Log")
            options.append("🎯 Remarks")
            options.append("🔄 Strava Sync")
            # options.append("📊 Stats"),  # Add the hidden option

        if selected_member == "Scott":
            options.append("🔄 Strava Sync")


        if st.session_state.memberverified:
            options.append("📊 Stats")
            options.append("🗺️ Your Runs")
            options.append("📓Log")
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


#########################################################################

if tabs != "🗓️ Program" and tabs != "🗺️ Your Runs":

    if st.session_state.get("just_submitted", False):
        df = pullc.get_runner_data()  # Uncached for fresh data after submission
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
        *If you opted for strava auto sync
    </div>
""",
        unsafe_allow_html=True,
    )

    with st.expander(
        "Enter User Fields (*RPE, Shoes, Remarks, Type of Activity-for Run*)",
        expanded=True,
    ):
        from data import user_field
        from data import read_data_cached_for_recent

        # """DEPRECATED: Use edit_user_fields_supa() instead"""
        # user_field.edit_user_fields(full_df)

        df = read_data_cached_for_recent.get_runner_data()
        full_df = pd.DataFrame(df)
        

        if selected_user == "Guest":
            filtered_member_df = full_df
            selected_user = "All"
        else:
            filtered_member_df = full_df[full_df["Member Name"] == selected_user]
        
        user_field.edit_user_fields_supa(filtered_member_df,selected_user)
        

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
    ### FILTER RUNS ONLY ###
    # full_df = full_df[
    #             ~full_df["Activity"].isin(
    #                 [
    #                     "Rest",
    #                     "Cross Train",
    #                     "Strength Training",
    #                     "WeightTraining",
    #                     "Yoga",
    #                     0,
    #                     "",
    #                     "Walk",
    #                     "Pilates",
    #                     "Ride",
    #                     "Cooldown",
    #                     "Warm up",
    #                 ]
    #             )
    #         ]

   
    stats.generate_matrix_member(full_df)

    st.markdown(
        f"""
    <div style="
        color:#3a3939;
        font-size: 20px;
        font-weight: 600;
        border-bottom: 1px solid #ccc;
        padding-bottom: 8px;
        margin-top: 20px;
        margin-bottom: 10px;
        display: flex;
        align-items: center;">
        📊 Overview & Stats: &nbsp;
    </div>
    """,
        unsafe_allow_html=True,
    )


    # -------------------MEMBER FILTER  -----------------------#
    col1, col2, col3, col4 = st.columns(4)
    
    with col4:
         ### --- Capture Year --- ####
        full_df["Date_of_Activity"] = pd.to_datetime(
            full_df["Date_of_Activity"], errors="coerce"
        )
        full_df["year"] = full_df["Date_of_Activity"].dt.year

        _years = sorted(full_df["Date_of_Activity"].dt.year.dropna().unique().tolist())
        _years.insert(0, "All Time")
        last_index = len(_years) - 1

        selected_year = st.selectbox("Select Year to Filter", _years, index=last_index)

        ### All activity - but not filtered from app selections

        # Apply filtering with all years
        if selected_year == "All Time":
            filtered_member_df = full_df
        else:
            full_df = full_df[full_df["year"] == selected_year]

        

    with col1:
        members = sorted(full_df["Member Name"].dropna().unique())
        members_count = len(members)

        members.insert(0, "All")  # Add 'All' option at the top
        
        
        if selected_member == "Guest":
            default_mem = "All"
        else:
            default_mem = selected_user
        

        selected_member = st.selectbox(
            "Select Member to Filter", members, index=members.index(default_mem)
        )

        

        # selected_member = "Scott"

        # Filter the DataFrame

        # Apply filtering
        if selected_member == "All" or selected_member == "Guest" :
            filtered_member_df = full_df
        else:
            filtered_member_df = full_df[full_df["Member Name"] == selected_member]

        # menu = sorted(full_df["Menu"].dropna().unique())
        # menu = sorted(full_df["Menu"].dropna().astype(str).unique())
        # selected_menu = st.selectbox(
        #     "Select Menu",
        #     menu,
        # )

    # -------------------WEEK FILTER  -----------------------#
    with col2:
        weeks = sorted(filtered_member_df["Week"].dropna().unique(), reverse=True)
        weeks.insert(0, "All")
        selected_weeks = st.multiselect(
            "Select Week(s) to Compare", weeks, default=["All"]
        )

        if not selected_weeks or "All" in selected_weeks:
            filtered_df = filtered_member_df
        else:
            filtered_df = filtered_member_df[
                filtered_member_df["Week"].isin(selected_weeks)
            ]

    # -------------------EVENT FILTER  -----------------------#
    with col3:
        event = sorted(filtered_df["Event"].dropna().unique())
        if not filtered_df.empty and "Date_of_Activity" in filtered_df.columns and selected_user == "Scott":
            # Get the event from the most recent activity
            latest_activity = filtered_df.loc[filtered_df["Date_of_Activity"].idxmax()]
            latest_event = latest_activity["Event"]

            # Set default to the latest event (not "All")
            default_event = [latest_event] if latest_event in event else ["All"]
        else:
            default_event = ["All"]

        event.insert(0, "All")
        selected_event = st.multiselect(
            "Select Event(s) to Compare", event, default=default_event
        )
        if not selected_event or "All" in selected_event:
            filtered_df = filtered_df
        else:
            filtered_df = filtered_df[filtered_df["Event"].isin(selected_event)]
    # with col3:
    #     with st.popover("⏱️ Open Race Predictor"):
    #         from models import race_predictor as rp

    #         st.markdown(
    #             """
    #             <div style="
    #                 color:#3a3939;
    #                 font-size: 20px;
    #                 font-weight: 600;
    #                 border-bottom: 1px solid #ccc;
    #                 padding-bottom: 4px;
    #                 margin-top: 20px;
    #                 margin-bottom: 10px;">
    #                 ⏱️ Predict Your Race Time</div>
    #         """,
    #             unsafe_allow_html=True,
    #         )
    #         ### --- race predictor ----##

    #         rp.race_predictor(filtered_df)

    #########################--- ALL TIME STATS TABLE ----#######################
    


    # filtered_df_all_activity = filtered_df
    # filter non running activity

    filtered_df_withnonrun = filtered_df.copy()

    filtered_df_all_run = filtered_df[
        ~filtered_df["Activity"].isin(
            [
                "Rest",
                "Cross Train",
                "Strength Training",
                "",
                0,
                "Activity",
                "Pilates",
                "Rest",
                "Ride",
                "Swim",
                "Walk",
                "WeightTraining",
                "Workout",
                "Yoga",

            ]
        )
    ]

    filtered_df_all_non_run = filtered_df[
        filtered_df["Activity"].isin(
            [
                "Cross Train",
                "Strength Training",
                "Activity",
                "Pilates",
                "Rest",
                "Ride",
                "Swim",
                "Walk",
                "WeightTraining",
                "Workout",
                "Yoga",

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
    metric_movingtime = f"{hours:02d}:{minutes:02d}"

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


    col0, col1 = st.columns([1,4])


    with col0:
        
        st.markdown(
            """
            <style>
            @media (min-width: 1200px) {
                div[data-testid="stMetric"] {
                    height: 130px !important;
                }
            }
            @media (min-width: 768px) and (max-width: 1199px) {
                div[data-testid="stMetric"] {
                    height: 130px !important;
                }
            }
            @media (max-width: 767px) {
                div[data-testid="stMetric"] {
                    height: 100px !important;
                }
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.metric(
            "Runs 🏃‍♀️‍➡️",
            value=metric_number_runs,
            label_visibility="visible",
            border=True,
        )
        st.metric(
            "Total Distance 🏃💨KⓂ️",
            value=metric_distance,
            label_visibility="visible",
            border=True,
        )
        st.metric(
            "Moving Time ⏱️",
            value=metric_movingtime,
            label_visibility="visible",
            border=True,
        )
        st.metric(
            "Average Pace 🚄", value=metric_pace, label_visibility="visible", border=True
        )


    ######### TRAINING CALENDAR ############

    # with st.expander("View Calendar Log", expanded=True):
    with col1:
        from visuals import traininglog_calendar

        traininglog_calendar.create_training_log_section(filtered_df)


    
    ###########CHARTS###########
    from visuals import bubble as sb
    from visuals import combochart as cb
    from visuals import table as mt
    # from visuals import line_polar as lp
    from visuals import donut as dt
    from visuals import wordcloud as wc
    # from visuals import mappolyline as poly

    # -----COMBO CHART WEEKLY-------#
    # st.subheader("📅🏃‍♂️ Weekly Distance vs. Pace", divider="gray")
    with st.expander("View Weekly Key Metrics", expanded=False):
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

    with st.expander("View Supplimentary Metrics", expanded=False):
        # st.dataframe(filtered_df_all_non_run)
        cb.generate_combo_supplimentary_new(filtered_df_all_non_run)

    with st.expander("View Other Charts", expanded=False):
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

if tabs == "🗓️ Program":  ##TRAINING PLAN ##

    with st.popover("💡 Activity Abbreviations"):
        st.markdown("""
    ##### 📋 Activity Type Abbreviations

    **AR** – Active Recovery | **CT** – Cross Train | **E** – Easy Run
    **GA** – General Aerobic | **I** – Interval | **LSD** – Long Slow Distance
    **LT** – Lactate Threshold | **MLR** – Medium Long Run | **MP** – Marathon Pace
    **R** – Recovery Run | **S** – Speedwork | **STR** – Strength Training | **T** – Tempo
    """)

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
    

    # Define program URLs for each member
    

    PROGRAM_URLS = {
    "Scott": {
        "base": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1680121528&single=true",
        "personal": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1680121528&single=true"
    },
    "Chona": {
        "personal": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1489038442&single=true"
        # If Chona has a base program, add it here too
    },
    "Aiza": {
        "personal": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1351146568&single=true"
        # If Chona has a base program, add it here too
    },
    "Alvin": {
        "personal": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=959789449&single=true"
        # If Chona has a base program, add it here too
    },
        "All": {
        "base": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1748190509&single=true"
        # If Chona has a base program, add it here too
    }
}
    selected_user = st.session_state.current_user


    # Show expanders based on selected member
    if selected_user == "Scott":
        with st.expander("📅 Scott's Personal Program", expanded=True):
            components.iframe(
                PROGRAM_URLS["Scott"]["personal"],
                height=500,
                width=1600,
            )
    elif selected_user == "Chona":
        with st.expander("📅 Chona's Program", expanded=True):
            components.iframe(
                PROGRAM_URLS["Chona"]["personal"],
                height=500,
                width=1600,
            )
    elif selected_user == "Aiza":
        with st.expander("📅 Aiza's Program", expanded=True):
            components.iframe(
                PROGRAM_URLS["Aiza"]["personal"],
                height=500,
                width=1600,
            )
    elif selected_user == "Alvin":
        with st.expander("📅 Alvin's Program", expanded=True):
            components.iframe(
                PROGRAM_URLS["Alvin"]["personal"],
                height=500,
                width=1600,
            )
    else:
        # All other users (Aiza, Fraulein, Alvin, Lead, Maxine, Guest)
        with st.expander("🏋️ Base Building + SG Marathon 2026", expanded=True):
            components.iframe(
                PROGRAM_URLS["All"]["base"],
                height=500,
                width=1600,
            )

if tabs == "📘 Reference":  ##STR WORK
    from visuals import referencetab as ref

    ref.ref_tab()

if tabs == "🗺️ Your Runs":  ##STR WORK
    from data import read_data_cached_for_recent

    df = read_data_cached_for_recent.get_runner_data()
    full_df = pd.DataFrame(df)

    #############################################################################

    ### export sample ####
    # full_df.to_csv("view_fulldf.csv", index=False)
    st.markdown("### 🏃 Recent Runs")

    col1, col2 = st.columns(2)

    with col1:
        members = sorted(full_df["Member Name"].dropna().unique())
        members_count = len(members)

        members.insert(0, "All")
        
        if selected_member == "Guest":
            default_mem = "All"
        else:
            default_mem = selected_user
        
        selected_member = st.selectbox(
            "Select Member to Filter",
            members,
            index=members.index(default_mem),
        )

            

        if selected_member == "All" or selected_member == "Guest":
            filtered_member_df = full_df
        else:
            filtered_member_df = full_df[full_df["Member Name"] == selected_member]

    # -------------------WEEK FILTER  -----------------------#
    with col2:
        weeks = sorted(filtered_member_df["Week"].dropna().unique(), reverse=True)
        selected_weeks = st.multiselect(
            "Select Week(s) to Compare", weeks, default=[weeks[0]] if weeks else []
        )

        if not selected_weeks or "All" in selected_weeks:
            filtered_df = filtered_member_df
        else:
            filtered_df = filtered_member_df[
                filtered_member_df["Week"].isin(selected_weeks)
            ]

    from visuals import table as mt
    # from visuals import mappolyline as poly
    from visuals import activitycard as acard

    filtered_df = filtered_df[
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

    # Load zones data from Google Sheets
    zones_data = None
    try:
        import data.push_data as push
        import data.push_supa as pushsupa
        import gspread
        import data.read_data_cached


        try:
            zone_records = data.read_data_cached.get_zones()

            if len(zone_records) > 1:
                headers = zone_records[0]
                zones_data = pd.DataFrame(zone_records[1:], columns=headers)
                # Clean up percentage column
                zones_data["Percentage"] = (
                    zones_data["Percentage"].astype(str).str.replace("%", "")
                )
            if 'HR (bpm)' in zones_data.columns:
                zones_data['HR (bpm)'] = pd.to_numeric(zones_data['HR (bpm)'], errors='coerce')


        except gspread.WorksheetNotFound:
            st.info("Zone data not available yet. Run Strava Sync to calculate zones.")

    except Exception as e:
        st.warning(f"Could not load zone data: {e}")

    #Handle numerics
    if 'HR (bpm)' in filtered_df.columns:
        filtered_df['HR (bpm)'] = pd.to_numeric(filtered_df['HR (bpm)'], errors='coerce')
    if 'Cadence (steps/min)' in filtered_df.columns:
        filtered_df['Cadence (steps/min)'] = pd.to_numeric(filtered_df['Cadence (steps/min)'], errors='coerce')
    if 'Max_HR' in filtered_df.columns:
        filtered_df['Max_HR'] = pd.to_numeric(filtered_df['Max_HR'], errors='coerce')

        
    acard.display_strava_style_feed_test(filtered_df, zones_data)

    # st.write(f"Columns in filtered_df: {filtered_df.columns.tolist()}")
    # if "UniqueKey" not in filtered_df.columns:
    #     st.error("UniqueKey column not found! Zones will not match.")
    #     # acard.display_strava_style_feed_test(filtered_df)

    # # # In the Your Runs tab, after loading both dataframes
    # if zones_data is not None and not zones_data.empty:
    #     st.write("### Sample Parent_UniqueKey from zones_data:")
    #     if "Parent_UniqueKey" in zones_data.columns:
    #         st.write(zones_data["Parent_UniqueKey"].head(5).tolist())
    #     else:
    #         st.write("Parent_UniqueKey column not found!")

    # st.write("### Sample UniqueKey from activities:")
    # st.write(filtered_df["UniqueKey"].tail(5).tolist())

    # st.write("### full_df UniqueKey samples:")
    # st.write(full_df["UniqueKey"].tail(10).tolist())

    # st.write("### full_df columns:")
    # st.write(full_df.columns.tolist())

if tabs == "🏋🏻‍♂️ Str Training":  # REFERENCE
    from visuals import strength_ref as sref

    sref.general_str_ref()

if tabs == "🎯 Remarks":  # REMARKS
    from visuals import weekly_remarks as wr
    from visuals import stats_table as stats

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
            🎯 Weekly Remarks
        </div>
    """,
        unsafe_allow_html=True,
    )

    ### --- ACTIVATE ONLY DURING WEEKLY REVIEWS -----###
    # -- WEEKLY  CHART -- ##
    coach_df = (
        full_df
        if selected_weeks == "All"
        else full_df[full_df["Week"].isin(selected_weeks)]
    )

    list_weeks = sorted(
        filtered_df["Week"].dropna().unique(),
        key=lambda x: int("".join(filter(str.isdigit, x))),
    )
    # list_weeks = sorted(full_df["Week"].dropna().unique())
    latest_week = list_weeks[-1]

    latest_week = "W 3"
    coach_df = filtered_df[filtered_df["Week"] == (latest_week)]

    st.markdown(f"""## 🏁 Week: {latest_week}""")

    # st.write(filtered_df.columns)

    # ####----WEEKLY SUMMARY TABLE --- ###
    stats.generate_matrix_coach(coach_df)

    wr.weekly_remarks()

if tabs == "💗 HR Zones":  ##SCOTTS CORNER

    with st.expander("Scott Program"):
        st.markdown(
            """
                <div style="
                    color:#3a3939;
                    font-size: 20px;
                    font-weight: 450;
                    border-bottom: 1px solid #ccc;
                    padding-bottom: 4px;
                    margin-top: 20px;
                    margin-bottom: 10px;">
                    🗓️ Training Plan</div>
            """,
            unsafe_allow_html=True,
        )
        prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1680121528&single=true"
        components.iframe(
            prog_sheet,
            height=500,
            width=600,
        )

    with st.expander("Chona Progaram"):
        st.subheader("Chona")
        prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=1489038442&single=true"
        components.iframe(
            prog_sheet,
            height=500,
            width=600,
        )

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
    from data.zoneprocessor import (
        calculate_hr_zones_from_streams,
        calculate_pace_zones_from_streams,
    )

    days_back = st.slider("Days to look back", 2, 365, 2)
    days_back = int(days_back)

    col1, col2 = st.columns([3, 1])

    with col2:
        if st.button("🔄 Sync to Google Sheets", type="primary"):
            st.session_state.sync_triggered = True

    # # Fetch Strava data
    import data.fetch_strava as fs
    import data.strava as strav

    activities = fs.fetch_all_activities_old(days_back)


    ### export sample ####
    # sample_extract_df = pd.DataFrame(activities)
    # # Basic export
    # sample_extract_df.to_csv("output.csv", index=False)

    st.header("📊 Activity Zone Analysis")
    st.markdown("Analyze heart rate and pace zone distribution for your activities")

    col1, col2 = st.columns([2, 1])

    with col1:
        days_back_zones = st.slider(
            "Days to look back for zone analysis", 2, 365, 2, key="zone_days_back"
        )

    ### export sample ####
    # zones_df.to_csv("zones_df_output.csv", index=False)
    with col2:
        if st.button("🔄 Calculate Zones", type="primary", key="calc_zones"):
            st.session_state.calc_zones_triggered = True

    if st.session_state.get("calc_zones_triggered", False):
        with st.spinner("Fetching and processing activities..."):
            import data.fetch_strava as fs
            import data.strava as strav

            if activities and len(activities) > 0:
                # =========================================================
                # STEP 1: Create ONE StravaAPI client per athlete (outside the loop)
                # =========================================================
                athlete_clients = {}
                for name, creds in st.secrets["users"].items():
                    athlete_clients[name] = strav.StravaAPI(
                        client_id=creds["client_id"],
                        client_secret=creds["client_secret"],
                        access_token=creds["access_token"],
                        refresh_token=creds["refresh_token"],
                    )
                    print(f"✅ Created client for {name}")

                # Collect all zone data
                all_zone_data = []

                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, act in enumerate(activities):
                    status_text.text(
                        f"Processing {idx+1} of {len(activities)}: {act.get('name', 'Unknown')}"
                    )

                    # Only process activities with heart rate and distance
                    if act.get("has_heartrate") and act.get("distance", 0) > 0:
                        try:
                            # Get the athlete name
                            athlete_name = act.get("athlete_name")

                            # Reuse the existing client for this athlete
                            strava = athlete_clients.get(athlete_name)

                            if not strava:
                                st.warning(
                                    f"No client found for athlete: {athlete_name}"
                                )
                                continue

                            # Use the authenticated StravaAPI class (handles token refresh automatically)
                            streams = None
                            response = strava.make_authenticated_request(
                                f"/activities/{act['id']}/streams",
                                params={
                                    "keys": "time,heartrate,velocity_smooth",
                                    "key_by_type": "true",
                                },
                            )

                            if response and response.status_code == 200:
                                streams_data = response.json()

                                # Convert to expected format for your zone functions
                                class StreamWrapper:
                                    def __init__(self, data):
                                        self.data = data

                                streams = {}
                                if "heartrate" in streams_data:
                                    streams["heartrate"] = StreamWrapper(
                                        streams_data["heartrate"]["data"]
                                    )
                                if "time" in streams_data:
                                    streams["time"] = StreamWrapper(
                                        streams_data["time"]["data"]
                                    )
                                if "velocity_smooth" in streams_data:
                                    streams["velocity_smooth"] = StreamWrapper(
                                        streams_data["velocity_smooth"]["data"]
                                    )

                            if streams and "heartrate" in streams:
                                # Calculate HR zones
                                hr_zones = calculate_hr_zones_from_streams(
                                    streams, athlete_name=athlete_name
                                )

                                if hr_zones:
                                    # Format date
                                    start_date = act.get("start_date_local", "")
                                    if start_date and "T" in start_date:
                                        date_part = start_date.split("T")[0]
                                    else:
                                        date_part = (
                                            str(start_date)[:10] if start_date else ""
                                        )

                                    # Calculate average HR for this activity
                                    raw_hr = act.get("average_heartrate", 0)
                                    avg_hr = int(round(raw_hr))
                                    sport_type = act.get("sport_type", "Run")

                                    # Build parent UniqueKey
                                    parent_unique_key = f"{date_part}|{athlete_name}|{sport_type}|{avg_hr}"

                                    for zone in hr_zones:
                                        all_zone_data.append(
                                            {
                                                "Date": str(date_part),
                                                "Activity": sport_type,
                                                "Athlete": str(athlete_name),
                                                "Type": "Heart Rate",
                                                "Zone": str(zone["zone"]),
                                                "Zone Name": str(zone["zone_name"]),
                                                "Min": int(zone["min_hr"]),
                                                "Max": int(zone["max_hr"]),
                                                "Time": str(zone["time_formatted"]),
                                                "Percentage": f"{float(zone['percentage'])}%",
                                                "Parent_UniqueKey": str(
                                                    parent_unique_key
                                                ),
                                                "Avg_HR": int(avg_hr),
                                            }
                                        )

                                # Calculate Pace zones (only for runs)
                                if (
                                    act.get("sport_type") == "Run"
                                    and act.get("distance", 0) > 0
                                    and "velocity_smooth" in streams
                                ):
                                    pace_zones = calculate_pace_zones_from_streams(
                                        streams, athlete_name=athlete_name
                                    )
                                    if pace_zones:
                                        for zone in pace_zones:
                                            all_zone_data.append(
                                                {
                                                    "Date": date_part,
                                                    "Activity": sport_type,
                                                    "Athlete": athlete_name,
                                                    "Type": "Pace",
                                                    "Zone": zone["zone"],
                                                    "Zone Name": zone["zone_name"],
                                                    "Min": zone.get("min_pace", "-"),
                                                    "Max": zone.get("max_pace", "-"),
                                                    "Time": zone["time_formatted"],
                                                    "Percentage": f"{zone['percentage']}%",
                                                    "Parent_UniqueKey": parent_unique_key,
                                                    "Avg_HR": avg_hr,
                                                }
                                            )
                            else:
                                st.warning(f"No stream data for activity {act['id']}")

                        except Exception as e:
                            st.warning(
                                f"Could not process activity {act.get('id', 'unknown')}: {e}"
                            )

                    # Update progress
                    progress_bar.progress((idx + 1) / len(activities))

                status_text.empty()
                progress_bar.empty()

                if all_zone_data:
                    # Create dataframe
                    zones_df = pd.DataFrame(all_zone_data)

                    st.success(
                        f"✅ Processed {len(activities)} activities, generated {len(zones_df)} zone records"
                    )
                    st.subheader("📊 Zone Distribution Data")

                    # Display the dataframe
                    st.write("zones data to be pushed")
                    st.dataframe(zones_df, use_container_width=True, hide_index=True)

                    # Add download button
                    csv = zones_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Zone Data as CSV",
                        data=csv,
                        file_name=f"zone_analysis_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                    )


                else:
                    st.warning(
                        "No zone data could be calculated. Make sure your activities have heart rate data."
                    )
            else:
                st.info("No activities found in the selected date range.")

            st.session_state.calc_zones_triggered = False
    ############## BEFORE PUSH ####################

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
        #################EDIT HERE TO ADD DATA FROM STRAVA####################
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
            "Map_Polyline": act.get("map", {}).get("summary_polyline"),
            "Max_Pace": to_float(act.get("max_speed")),
            "Max_HR": to_float(act.get("max_heartrate")),
            "Elevation_Gained": to_float(act.get("total_elevation_gain")),
        }

    def convert_speed_to_pace(speed_mps):
        """Convert meters per second to min/km pace format (H:MM:SS or MM:SS)"""
        if speed_mps <= 0:
            return 0

        # Convert m/s to min/km
        pace_seconds_per_km = 1000 / speed_mps

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

        return total_seconds / 86400

    def convert_seconds_to_time_string(total_seconds):
        """Return formatted time string that looks correct"""
        if total_seconds <= 0:
            return "00:00:00"

        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        return f"{hours:02}:{minutes:02}:{seconds:02}"

    ############  Before Sync ###########
    if activities:
        cleaned_activities = [clean_activity_data(act) for act in activities]
        strava_df = pd.DataFrame(cleaned_activities)

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

        # Fill NaN values with 0
        strava_df["Max_Pace"] = pd.to_numeric(strava_df["Max_Pace"], errors="coerce")
        strava_df["Max_Pace"] = strava_df["Max_Pace"].fillna(0)
        #########################################################################
        strava_df["Max_Pace"] = strava_df["Max_Pace"].apply(
            lambda x: convert_speed_to_pace_string(x) if x > 0 else "00:00:00"
        )
        strava_df["HR (bpm)"] = strava_df["HR (bpm)"].round().astype(int)
        strava_df["Max_HR"] = strava_df["Max_HR"].round().astype(int)

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
        strava_df.rename(columns={'Duration': 'Duration_Other'}, inplace=True)
        # strava_df["Duration_Other"] = strava_df["Duration"]


        strava_df["UniqueKey"] = (
            strava_df[["Date_of_Activity", "Member Name", "Activity", "HR (bpm)"]]
            .astype(str)
            .agg("|".join, axis=1)
        )
        st.write("strava_df to be pushed")
        st.dataframe(strava_df)

        ######SYNC ACTIVATION#########
        if st.session_state.get("sync_triggered", False):
            

            st.divider()
            st.subheader("🔄 Syncing to Google Sheets...")

            with st.spinner("Pushing activities to Google Sheets..."):
                # success_count, error_count = push.push_strava_data_to_sheet(strava_df)
                success_count, error_count = pushsupa.push_activity_data_to_supabase(strava_df)

            if success_count > 0:
                st.success(
                    f"✅ Successfully pushed {success_count} activities to Google Sheets!"
                )

            if error_count > 0:
                st.error(f"❌ Failed to push {error_count} activities")

            # Reset the trigger
            st.session_state.sync_triggered = False


        # Push zone data if available
    if st.button("Sync Zones", type="primary", key="sync_zones"):
        st.session_state.sync_zones_triggered = True

    if st.session_state.get("sync_zones_triggered", False):
        with st.spinner("Fetching and processing activities..."):
    
            if "zones_df" in locals() and not zones_df.empty:
                # Group by Parent_UniqueKey
                grouped = zones_df.groupby("Parent_UniqueKey")

                total_success = 0
                total_errors = 0

                for parent_key, group_df in grouped:
                    # Get activity data from the first row of this group
                    first_row = group_df.iloc[0]

                    activity_row_data = {
                        "Date": first_row["Date"],
                        "Member Name": first_row["Athlete"],
                        "Activity": first_row["Activity"],
                        "Avg_HR": first_row["Avg_HR"],
                    }

                    st.write(f"📊 Pushing {len(group_df)} zones for {parent_key}")

                    # zone_success, zone_errors = push.push_zone_data_to_sheet(
                    #     group_df, parent_key, activity_row_data
                    # )
                    zone_success, zone_errors = pushsupa.push_zone_data_to_supabase(
                        group_df, parent_key, activity_row_data
                    )

                    total_success += zone_success
                    total_errors += zone_errors

                if total_success > 0:
                    st.success(f"✅ Successfully pushed {total_success} zone records!")
                if total_errors > 0:
                    st.error(f"❌ Failed to push {total_errors} zone records")
