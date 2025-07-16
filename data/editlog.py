import streamlit as st
from datetime import time, datetime
from zoneinfo import ZoneInfo
from data import read_data_uncached as pulluc
from data import read_data_cached as pullc
import pandas as pd
from data import push_data as push


# ----------------- Confirmation Dialog -----------------
@st.dialog("Confirm Entry?")
def confirm_submission(new_log_2):
    st.write("Are you sure you want to submit this entry?")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✅ Yes, Submit"):
            # Simulate push to backend
            st.session_state["submitted_data"] = new_log_2
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


# def edit_log(data):
#     logindex = int(
#         st.number_input("LogIndex", placeholder="Enter Log ID", step=1, format="%d")
#     )

#     # -------PULL DATA ONCE --------#
#     # -----load un cached when not submitting
#     if "just_submitted" not in st.session_state:
#         st.session_state["just_submitted"] = False

#     if st.session_state["just_submitted"] == False:
#         df = pulluc.get_runner_data()
#         st.session_state["just_submitted"] = False
#     else:
#         df = pullc.get_runner_data()

#     full_df = pd.DataFrame(data)

#     ##RETRIEVE RECORD
#     if logindex in full_df.index:
#         filtered_df = full_df.loc[[logindex]]
#         st.write("Filtered Row:", filtered_df)
#     else:
#         st.warning("LogIndex not found in data.")


def new_log_2(record_to_edit=None):

    with st.form("activity_log_edit", clear_on_submit=True, border=True):
        time_stamp_ = datetime.now()
        time_stamp = time_stamp_.strftime("%Y-%m-%d")
        now_ = datetime.now()

        ### -------- Prefill values from record_to_edit -------- ###
        default_date = now_.date()
        default_member = None
        default_activity = None
        default_distance = 0.0
        default_pace_str = "00:00:00"
        default_hr = 0
        default_cad = 0
        default_rpe = 0
        default_shoe = None
        default_remarks = ""

        if record_to_edit is not None:
            default_date = pd.to_datetime(record_to_edit["Date"]).date()
            default_member = record_to_edit["Member Name"]
            default_activity = record_to_edit["Activity"]
            default_distance = float(record_to_edit["Distance"])
            default_pace_str = record_to_edit["Pace"]
            default_hr = int(record_to_edit["HR (bpm)"])
            default_cad = int(record_to_edit["Cadence (steps/min)"])
            default_rpe = int(record_to_edit["RPE (1–10 scale)"])
            default_shoe = record_to_edit["Shoe"]
            default_remarks = record_to_edit["Remarks"]

        # ----- Form Inputs ----- #

        mem_selection = st.selectbox(
            "Members",
            ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"],
            index=None,
            placeholder="Select Member",
            key="mem_selection",
        )
        if default_member:
            st.session_state["mem_selection"] = default_member

        date = st.date_input("Date of Activity", value=default_date)

        act_selection = st.selectbox(
            "Activity",
            [
                "Easy Run",
                "Aerobic Run",
                "Tempo Run",
                "Cooldown",
                "Warm up",
                "Speed Work (Zone 4-5 x400M)",
                "Strength Training",
                "LSD Road@ Zone 2 Pace",
                "LSD Trail@ Zone 2 Pace",
                "Yoga",
                "Cross Train",
                "Rest",
                "RACE DAY",
            ],
            index=None,
            placeholder="Select an activity",
            key="act_selection",
        )
        if default_activity:
            st.session_state["act_selection"] = default_activity

        distance = st.number_input(
            "Distance", placeholder="Enter distance", value=default_distance
        )

        # Pace dropdowns
        pace_list = [f"{m:02}:{s:02}" for m in range(0, 15) for s in (range(0, 60))]
        value_paces = [f"0:{m:02}:{s:02}" for m in range(0, 15) for s in range(0, 60)]
        pace_map = dict(zip(pace_list, value_paces))

        # Convert pace back to dropdown format (mm:ss)
        default_pace_dropdown = (
            default_pace_str.split(":")[1] + ":" + default_pace_str.split(":")[2]
        )

        pace_display = st.selectbox(
            "Select Pace (min:sec) *type in your pace and select",
            pace_list,
            index=(
                pace_list.index(default_pace_dropdown)
                if default_pace_dropdown in pace_list
                else 0
            ),
        )
        pace_str = pace_map[pace_display]

        hr = st.number_input("HR (bmp)", min_value=0, max_value=220, value=default_hr)
        cad = st.number_input(
            "Cadence (spm)", min_value=0, max_value=200, value=default_cad
        )
        rpe = st.slider("RPE", 0, 10, value=default_rpe)

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
                    "Pink Nimbus 27",
                ]
            ),
            index=None,
            key="shoe_selection",
        )
        if default_shoe:
            st.session_state["shoe_selection"] = default_shoe

        remarks = st.text_area(
            "Remarks",
            placeholder="How did the session feel?",
            value=default_remarks,
            key="remarks_input",
        )

        submitted_edit = st.form_submit_button("Edit:Submit Log", type="primary")

        if submitted_edit:
            new_log_2 = [
                time_stamp,
                date.isoformat(),
                act_selection or "",
                distance,
                pace_str,
                hr,
                cad,
                rpe,
                shoe or "",
                remarks,
                mem_selection or "",
            ]
            st.session_state.pending_log = new_log_2
            confirm_submission(new_log_2)


def replace_log_row(full_df, logindex, updated_data):
    try:
        # Update the specific row
        full_df.loc[logindex] = updated_data

        # Push changes
        push.push_runner_data(full_df.to_dict(orient="records"))

        # Clear edit state
        del st.session_state.record_to_edit
        st.session_state.editing = False

        st.success("Log updated successfully!")
        st.balloons()
        st.rerun()
    except Exception as e:
        st.error(f"Error updating log: {e}")


def start_edit():
    with st.expander("Edit Log"):
        df = pulluc.get_runner_data()
        logindex = st.number_input("Enter Log ID to edit", step=1, format="%d")

        if st.button("Load Log for Editing"):
            if logindex in df.index:
                record_to_edit = df.loc[logindex].to_dict()
                st.session_state.record_to_edit = record_to_edit
                st.session_state.editing = True
                st.rerun()
            else:
                st.warning("LogIndex not found")

    # If we're in edit mode, show the form with the record
    if st.session_state.get("editing"):
        if st.button("Cancel Editing"):
            del st.session_state.record_to_edit
            st.session_state.editing = False
            st.rerun()

        new_log_2(record_to_edit=st.session_state.record_to_edit)
