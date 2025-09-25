import streamlit as st
import datetime as dt
from data import update_data
import pandas as pd


def edit_log(full_df):

    # Ensure Date_of_Activity is datetime
    full_df["Date_of_Activity"] = pd.to_datetime(
        full_df["Date_of_Activity"], errors="coerce"
    )

    # Let user select an entry to edit
    full_df["Date_of_Activity_str"] = full_df["Date_of_Activity"].dt.strftime(
        "%Y-%m-%d"
    )

    # Build a unique composite key for each row
    full_df["UniqueKey"] = (
        full_df["Date_of_Activity_str"]
        + "|"
        + full_df["Member Name"]
        + "|"
        + full_df["Activity"]
    )

    if not full_df.empty:
        # Create a unique identifier for each row
        full_df["display"] = (
            full_df["Date_of_Activity_str"]
            + " - "
            + full_df["Member Name"]
            + " - "
            + full_df["Activity"]
        )

        # Let user select which entry to edit
        entry_to_edit = st.selectbox(
            "Select entry to edit",
            options=full_df.sort_values(by="display", ascending=False)[
                "display"
            ].tolist(),
            index=None,
            placeholder="Select an entry to edit",
        )

        if entry_to_edit:
            # Get the selected row
            selected_index = full_df[full_df["display"] == entry_to_edit].index[0]
            selected_row = full_df.loc[selected_index]

            # DEBUG: Print the actual timestamp
            print(f"Selected display: {entry_to_edit}")
            print(f"Composite key: {selected_row['UniqueKey']}")

            # Display current values and allow editing
            with st.form("edit_form"):
                st.write("Edit the values below:")

                # Member selection
                edited_member = st.selectbox(
                    "Member",
                    ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"],
                    index=(
                        ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"].index(
                            selected_row["Member Name"]
                        )
                        if selected_row["Member Name"]
                        in ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"]
                        else 0
                    ),
                    key="edit_member",
                )

                # Date selection
                edited_date = st.date_input(
                    "Date of Activity",
                    value=dt.datetime.strptime(
                        selected_row["Date_of_Activity_str"], "%Y-%m-%d"
                    ).date(),
                    key="edit_date",
                )

                # Activity type
                activity_options = [
                    "Easy Run",
                    "Aerobic Run",
                    "Tempo Run",
                    "Cooldown",
                    "Warm up",
                    "Speed Work (Zone 4-5 x400M)",
                    "LSD Road@ Zone 2 Pace",
                    "LSD Trail@ Zone 2 Pace",
                    "RACE DAY",
                    "Strength Training",
                    "Yoga",
                    "Cross Train",
                    "Rest",
                    "Pilates",
                ]

                edited_activity = st.selectbox(
                    "Activity",
                    options=activity_options,
                    index=(
                        activity_options.index(selected_row["Activity"])
                        if selected_row["Activity"] in activity_options
                        else 0
                    ),
                    key="edit_activity",
                )

                # Show appropriate fields based on activity type
                if edited_activity in [
                    "Easy Run",
                    "Aerobic Run",
                    "Tempo Run",
                    "Cooldown",
                    "Warm up",
                    "Speed Work (Zone 4-5 x400M)",
                    "LSD Road@ Zone 2 Pace",
                    "LSD Trail@ Zone 2 Pace",
                    "RACE DAY",
                ]:
                    # Running activity fields
                    edited_distance = st.number_input(
                        "Distance",
                        value=(
                            float(selected_row["Distance"])
                            if selected_row["Distance"]
                            else 0.0
                        ),
                        key="edit_distance",
                    )

                    # Handle pace editing
                    pace_str = str(selected_row["Pace"])

                    if selected_row["Pace"]:
                        # Convert pace string to minutes:seconds format for display
                        pace_parts = pace_str.split(":")
                        if len(pace_parts) == 3:  # Format is HH:MM:SS
                            current_pace_display = (
                                f"{int(pace_parts[1]):02d}:{int(pace_parts[2]):02d}"
                            )
                        else:
                            current_pace_display = "00:00"
                    else:
                        current_pace_display = "00:00"

                    pace_list = [
                        f"{m:02}:{s:02}" for m in range(0, 15) for s in range(0, 60)
                    ]
                    pace_map = dict(
                        zip(
                            pace_list,
                            [
                                f"0:{m:02}:{s:02}"
                                for m in range(0, 15)
                                for s in range(0, 60)
                            ],
                        )
                    )

                    edited_pace_display = st.selectbox(
                        "Select Pace (min:sec)",
                        pace_list,
                        index=(
                            pace_list.index(current_pace_display)
                            if current_pace_display in pace_list
                            else 0
                        ),
                        key="edit_pace",
                    )
                    edited_pace = pace_map[edited_pace_display]

                    edited_hr = st.number_input(
                        "HR (bpm)",
                        value=(
                            int(selected_row["HR (bpm)"])
                            if selected_row["HR (bpm)"]
                            else 0
                        ),
                        min_value=0,
                        max_value=220,
                        key="edit_hr",
                    )

                    edited_cad = st.number_input(
                        "Cadence (spm)",
                        value=(
                            int(selected_row["Cadence (steps/min)"])
                            if selected_row["Cadence (steps/min)"]
                            else 0
                        ),
                        min_value=0,
                        max_value=200,
                        key="edit_cad",
                    )

                    shoe_options = sorted(
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
                    )

                    edited_shoe = st.selectbox(
                        "Shoe",
                        options=shoe_options,
                        index=(
                            shoe_options.index(selected_row["Shoe"])
                            if selected_row["Shoe"] in shoe_options
                            else 0
                        ),
                        key="edit_shoe",
                    )

                    # Set duration to None for running activities
                    edited_duration = None

                else:
                    # Other activity fields
                    edited_distance = None
                    edited_pace = None
                    edited_cad = None
                    edited_shoe = None

                    # Handle duration editing
                    if selected_row["Duration_Other"]:
                        # Convert duration string to HH:MM:SS format for display
                        duration_parts = selected_row["Duration_Other"].split(":")
                        if len(duration_parts) == 3:
                            current_duration_display = f"{int(duration_parts[0]):02d}:{int(duration_parts[1]):02d}:{int(duration_parts[2]):02d}"
                        else:
                            current_duration_display = "00:00:00"
                    else:
                        current_duration_display = "00:00:00"

                    duration_list = [
                        f"{h:02}:{m:02}:{s:02}"
                        for h in range(0, 10)
                        for m in range(0, 60)
                        for s in range(0, 60)
                    ]

                    duration_map = dict(
                        zip(
                            duration_list,
                            [
                                f"{h:02}:{m:02}:{s:02}"
                                for h in range(0, 10)
                                for m in range(0, 60)
                                for s in range(0, 60)
                            ],
                        )
                    )

                    edited_duration_display = st.selectbox(
                        "Select Duration (hour:min:sec)",
                        duration_list,
                        index=(
                            duration_list.index(current_duration_display)
                            if current_duration_display in duration_list
                            else 0
                        ),
                        key="edit_duration",
                    )
                    edited_duration = duration_map[edited_duration_display]

                    edited_hr = st.number_input(
                        "HR (bmp)",
                        value=(
                            int(selected_row["HR (bpm)"])
                            if selected_row["HR (bpm)"]
                            else 0
                        ),
                        min_value=0,
                        max_value=220,
                        key="edit_hr_other",
                    )

                # Common fields
                edited_rpe = st.slider(
                    "RPE",
                    min_value=0,
                    max_value=10,
                    value=(
                        int(selected_row["RPE (1–10 scale)"])
                        if selected_row["RPE (1–10 scale)"]
                        else 0
                    ),
                    key="edit_rpe",
                )

                edited_remarks = st.text_area(
                    "Remarks",
                    value=selected_row["Remarks"] if selected_row["Remarks"] else "",
                    placeholder="How did the session feel?",
                    key="edit_remarks",
                )

                # Submit button
                update_submitted = st.form_submit_button("Update Entry", type="primary")

                if update_submitted:
                    # Build updated entry with new composite key
                    new_key = (
                        f"{edited_date.isoformat()}|{edited_member}|{edited_activity}"
                    )

                    updated_entry = {
                        "UniqueKey": new_key,
                        "TimeStamp": edited_date.isoformat(),
                        "Date_of_Activity": edited_date.isoformat(),
                        "Activity": edited_activity,
                        "Distance": edited_distance,
                        "Pace": edited_pace,
                        "HR (bpm)": edited_hr,
                        "Cadence (steps/min)": edited_cad,
                        "RPE (1–10 scale)": edited_rpe,
                        "Shoe": edited_shoe,
                        "Remarks": edited_remarks,
                        "Member Name": edited_member,
                        "Duration_Other": edited_duration,
                    }

                    if update_data.update_runner_data(
                        selected_row["UniqueKey"], updated_entry
                    ):
                        st.success("✅ Entry updated successfully!")
                        st.session_state["just_submitted"] = True
                        st.rerun()
                    else:
                        st.error("❌ Error updating entry. Please try again.")

    else:
        st.info("No entries available to edit.")
