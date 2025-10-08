import streamlit as st
import pandas as pd
import datetime as dt
from data import update_data


def edit_user_fields(full_df):
    """
    Let users fill in missing user-defined fields:
    Activity, RPE, Shoe, Remarks
    Only shows rows where at least one field is blank
    """

    # Ensure Date_of_Activity is datetime
    full_df["Date_of_Activity"] = pd.to_datetime(
        full_df["Date_of_Activity"], errors="coerce"
    )

    # Filter rows with missing user-defined fields
    df_to_edit = full_df[
        ((full_df["RPE (1–10 scale)"] == 0) & (full_df["Activity"] != "Rest"))
        | full_df["Shoe"].isna()
        | full_df["Remarks"].isna()
        | (full_df["Activity"] == "")
        | (full_df["Activity"] == "Run")
    ].copy()

    if df_to_edit.empty:
        st.info("✅ All user-defined fields are already filled.")
        return

    # Add string version of date for display
    df_to_edit["Date_of_Activity_str"] = df_to_edit["Date_of_Activity"].dt.strftime(
        "%Y-%m-%d"
    )

    # Build unique key and display string
    df_to_edit["UniqueKey"] = (
        df_to_edit["Date_of_Activity_str"]
        + "|"
        + df_to_edit["Member Name"]
        + "|"
        + df_to_edit["Activity"].fillna("")
    )
    df_to_edit["display"] = (
        df_to_edit["Date_of_Activity_str"]
        + " - "
        + df_to_edit["Member Name"]
        + " - "
        + df_to_edit["Activity"].fillna("")
    )

    # Let user select entry to edit
    entry_to_edit = st.selectbox(
        "Select entry to edit",
        options=df_to_edit.sort_values(by="display", ascending=False)[
            "display"
        ].tolist(),
        index=None,
        placeholder="Select an entry to edit",
    )

    if not entry_to_edit:
        return

    selected_index = df_to_edit[df_to_edit["display"] == entry_to_edit].index[0]
    selected_row = df_to_edit.loc[selected_index]

    with st.form("edit_user_fields_form"):
        st.write("Fill in missing fields below:")

        # Activity selection
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
            "Activity (*Select Type of Run for Running Activity*)",
            options=activity_options,
            index=(
                activity_options.index(selected_row["Activity"])
                if selected_row["Activity"] in activity_options
                else 0
            ),
        )

        # RPE
        edited_rpe = st.slider(
            "RPE (1–10 scale)",
            min_value=0,
            max_value=10,
            value=(
                int(selected_row["RPE (1–10 scale)"])
                if pd.notna(selected_row["RPE (1–10 scale)"])
                else 0
            ),
        )

        # Shoe
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
                "None",
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
        )

        # Remarks
        edited_remarks = st.text_area(
            "Remarks",
            value=selected_row["Remarks"] if pd.notna(selected_row["Remarks"]) else "",
            placeholder="How did the session feel?",
        )

        # Submit button
        submitted = st.form_submit_button("Update Entry")

        if submitted:
            # Build updated entry
            updated_entry = selected_row.to_dict()
            updated_entry.update(
                {
                    "Activity": edited_activity,
                    "RPE (1–10 scale)": edited_rpe,
                    "Shoe": edited_shoe,
                    "Remarks": edited_remarks,
                }
            )

            # Update Google Sheet
            if update_data.update_runner_data_user_field(
                selected_row["UniqueKey"], updated_entry
            ):
                st.success("✅ Entry updated successfully!")
                st.session_state["just_submitted"] = True

            else:
                st.error("❌ Error updating entry. Please try again.")

    if st.button("🔄 Refresh App"):
        st.rerun()


def bulk_edit_user_fields(full_df):
    """
    Let users bulk fill in missing user-defined fields:
    Activity, RPE, Shoe, Remarks
    Only shows rows where at least one field is blank
    """

    # Filter rows with missing user-defined fields
    df_to_edit = full_df[
        ((full_df["RPE (1–10 scale)"] == 0) & (full_df["Activity"] != "Rest"))
        | full_df["Shoe"].isna()
        | full_df["Remarks"].isna()
        | (full_df["Activity"] == "")
        | (full_df["Activity"] == "Run")
    ].copy()

    df_to_edit = df_to_edit.reset_index(drop=True)

    if df_to_edit.empty:
        st.info("✅ All user-defined fields are already filled.")
        return

    # Add a display column for context
    df_to_edit["Date_of_Activity_str"] = pd.to_datetime(
        df_to_edit["Date_of_Activity"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    df_to_edit["display"] = (
        df_to_edit["Date_of_Activity_str"]
        + " - "
        + df_to_edit["Member Name"]
        + " - "
        + df_to_edit["Activity"].fillna("")
    )

    df_to_edit["UniqueKey"] = (
        df_to_edit["Date_of_Activity_str"]
        + " - "
        + df_to_edit["Member Name"]
        + " - "
        + df_to_edit["Activity"].fillna("")
    )

    # Select relevant columns for editing
    editable_cols = ["display", "Activity", "RPE (1–10 scale)", "Shoe", "Remarks"]
    edit_df = df_to_edit[editable_cols].copy()

    # Options for activity and shoe
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
        "WeightTraining",
        "Yoga",
        "Cross Train",
        "Rest",
        "Pilates",
    ]
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
            "None",
        ]
    )

    # Use data_editor inside a form to prevent constant reruns
    with st.form("edit_entries_form"):
        edited_df = st.data_editor(
            edit_df,
            column_config={
                "Activity": st.column_config.SelectboxColumn(
                    "Activity", options=activity_options
                ),
                "RPE (1–10 scale)": st.column_config.NumberColumn(
                    "RPE (1–10 scale)", min_value=0, max_value=10
                ),
                "Shoe": st.column_config.SelectboxColumn("Shoe", options=shoe_options),
                "Remarks": st.column_config.TextColumn("Remarks"),
                "display": st.column_config.TextColumn("Entry", disabled=True),
            },
            num_rows="dynamic",
            use_container_width=True,
        )

        # Submit button inside the form
        submitted = st.form_submit_button("Update All Entries")

        if submitted:
            updates_list = []

            # Collect all updates first
            for idx, row in edited_df.iterrows():
                original_row = df_to_edit.iloc[idx]
                updated_entry = (
                    full_df.loc[full_df["UniqueKey"] == original_row["UniqueKey"]]
                    .iloc[0]
                    .to_dict()
                )
                updated_entry.update(
                    {
                        "Activity": row["Activity"],
                        "RPE (1–10 scale)": row["RPE (1–10 scale)"],
                        "Shoe": row["Shoe"],
                        "Remarks": row["Remarks"],
                    }
                )

                updates_list.append((original_row["UniqueKey"], updated_entry))

            # Execute bulk update
            success_count, error_count = update_data.update_runner_data_bulk_new(
                updates_list
            )

            st.success(f"✅ Successfully updated {success_count} entries.")
            if error_count > 0:
                st.error(f"❌ Failed to update {error_count} entries.")
            st.rerun()
