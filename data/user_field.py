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

    # Let user select an entry to edit
    full_df["Date_of_Activity_str"] = full_df["Date_of_Activity"].dt.strftime(
        "%Y-%m-%d"
    )
    full_df["HR (bpm)"] = pd.to_numeric(full_df["HR (bpm)"], errors="coerce")
    hrval = full_df["HR (bpm)"]

    # Build a unique composite key for each row
    full_df["UniqueKey"] = (
        full_df["Date_of_Activity_str"]
        + "|"
        + full_df["Member Name"]
        + "|"
        + full_df["Strava_Base_Activity"]
        + "|"
        + full_df["HR (bpm)"].apply(lambda x: str(int(x)) if pd.notnull(x) else "N/A")
    )
    if not full_df.empty:
        # Create a unique identifier for each row
        full_df["display"] = (
            full_df["Date_of_Activity_str"]
            + "|"
            + full_df["Member Name"]
            + "|"
            + full_df["Strava_Base_Activity"]
            + "|"
            + full_df["HR (bpm)"].apply(
                lambda x: str(int(x)) if pd.notnull(x) else "N/A"
            )
        )

    # Filter rows with missing user-defined fields
    df_to_edit = full_df[
        ((full_df["RPE (1–10 scale)"] == 0) & (full_df["Activity"] != "Rest"))
        # | full_df["Shoe"].isna()
        # | full_df["Remarks"].isna()
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

    # df_to_edit["HR (bpm)"] = df_to_edit["HR (bpm)"].round().astype(int)

    # Build unique key and display string

    df_to_edit["UniqueKey"] = (
        df_to_edit[["Date_of_Activity", "Member Name", "Strava_Base_Activity", "HR (bpm)"]]
        .astype(str)
        .agg("|".join, axis=1)
    )

    df_to_edit = df_to_edit[df_to_edit["Strava_Base_Activity"]=="Run"]

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
            "Tempo",
            "Cooldown",
            "Warm up",
            "Speed Work",
            "LSD Road",
            "LSD Trail",
            "RACE DAY",
            "Interval",

        ]
        edited_activity = st.selectbox(
            "Activity (*Select Type of Run for Running Activity*)",
            options=activity_options,
            index=None,
            # index=(
            #     activity_options.index(selected_row["Activity"])
            #     if selected_row["Activity"] in activity_options
            #     else 0
            # ),
    placeholder="Select an entry to edit...",
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
                "Leili",
                "None",
            ]
        )
        edited_shoe = st.selectbox(
            "Shoe",
            options=shoe_options,
            index=None,
            # index=(
            #     shoe_options.index(selected_row["Shoe"])
            #     if selected_row["Shoe"] in shoe_options
            #     else 0
            # ),
            placeholder="Select Shoe to edit...",
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
            key_selected_row = selected_row["UniqueKey"]
            cleaned_key = (
                key_selected_row[: key_selected_row.rfind(".")]
                if "." in key_selected_row
                else key_selected_row
            )

            # Update Google Sheet
            if update_data.update_runner_data_user_field(cleaned_key, updated_entry):
                st.success("✅ Entry updated successfully!")
                st.session_state["just_submitted"] = True

            else:
                st.error("❌ Error updating entry. Please try again.")

    if st.button("🔄 Refresh App"):
        st.rerun()


def edit_user_fields_supa(full_df,member_name):
    """
    Let users fill in missing user-defined fields:
    Activity, RPE, Shoe, Remarks
    Only shows rows where at least one field is blank
    """
    from data.push_supa import update_activity_in_supabase  # Add this import

    # full_df = full_df[(full_df["Member Name"] == member_name)]
    # Ensure Date_of_Activity is datetime
    full_df["Date_of_Activity"] = pd.to_datetime(
        full_df["Date_of_Activity"], errors="coerce"
    )

    # Let user select an entry to edit
    full_df["Date_of_Activity_str"] = full_df["Date_of_Activity"].dt.strftime(
        "%Y-%m-%d"
    )
    full_df["HR (bpm)"] = pd.to_numeric(full_df["HR (bpm)"], errors="coerce")
    hrval = full_df["HR (bpm)"]

    # Build a unique composite key for each row
    full_df["UniqueKey"] = (
        full_df["Date_of_Activity_str"]
        + "|"
        + full_df["Member Name"]
        + "|"
        + full_df["Activity"]
        + "|"
        + full_df["HR (bpm)"].apply(lambda x: str(int(x)) if pd.notnull(x) else "N/A")
    )
    
    if not full_df.empty:
        # Create a unique identifier for each row
        full_df["display"] = (
            full_df["Date_of_Activity_str"]
            + "|"
            + full_df["Member Name"]
            + "|"
            + full_df["Activity"]
            + "|"
            + full_df["HR (bpm)"].apply(
                lambda x: str(int(x)) if pd.notnull(x) else "N/A"
            )
        )

    # Filter rows with missing user-defined fields
    df_to_edit = full_df[
        (full_df["Activity"] == "Run")].copy()

    # df_to_edit = full_df

    if df_to_edit.empty:
        st.info("✅ All user-defined fields are already filled.")
        return

    # Add string version of date for display
    df_to_edit["Date_of_Activity_str"] = df_to_edit["Date_of_Activity"].dt.strftime(
        "%Y-%m-%d"
    )

    # Build unique key and display string
    df_to_edit['hr_str']=full_df["HR (bpm)"].apply(
                lambda x: str(int(x)) if pd.notnull(x) else "N/A"
            )
    df_to_edit["UniqueKey"] = (
        df_to_edit[["Date_of_Activity", "Member Name", "Activity", "hr_str"]]
        .astype(str)
        .agg("|".join, axis=1)
    )

    # df_to_edit = df_to_edit[df_to_edit["Strava_Base_Activity"] == "Run"]

    # Debug: See what's in df_to_edit
    # st.write(f"🔍 Full_df size: {len(full_df)}")
    # st.write(f"🔍 df_to_edit after filtering: {len(df_to_edit)}")
    st.write(f"🔍 Your Recent Runs:")
    st.dataframe(df_to_edit[['Date_of_Activity',  'Activity','Distance',"HR (bpm)", 'Duration_Other']].tail(5))
    
    
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
            "Speed Work",
            "LSD Road",
            "LSD Trail",
            "RACE",
            "Interval",
        ]
        edited_activity = st.selectbox(
            "Activity (*Select Type of Run for Running Activity*)",
            options=activity_options,
            # index=(
            #     activity_options.index(selected_row["Activity"])
            #     if selected_row["Activity"] in activity_options
            #     else 0
            # ),
                    index=None,
        placeholder="Select run...",
        )

        # RPE
        # Use it for RPE
            # Use it for RPE
        cleaned_rpe = clean_supabase_value(selected_row["RPE (1–10 scale)"], 0)

        edited_rpe = st.slider(
            "RPE (1–10 scale)",
            min_value=0,
            max_value=10,
            value=cleaned_rpe,
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
                "Leili",
                "None",
            ]
        )
        edited_shoe = st.selectbox(
            "Shoe",
            options=shoe_options,
            # index=(
            #     shoe_options.index(selected_row["Shoe"])
            #     if selected_row["Shoe"] in shoe_options
            #     else 0
            # ),
                index=None,
        placeholder="Select Shoe...",
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
            updated_entry = {
                "Activity": edited_activity,
                "RPE (1–10 scale)": edited_rpe,
                "Shoe": edited_shoe,
                "Remarks": edited_remarks,
            }
            
            # Get the UniqueKey from the selected row
            unique_key = selected_row["UniqueKey"]
            
            # Remove trailing .0 if present (from float conversion)
            if "." in unique_key:
                unique_key = unique_key[:unique_key.rfind(".")]
            
            # Update Supabase
            if update_activity_in_supabase(unique_key, updated_entry):
                st.success("✅ Entry updated successfully!")
                st.balloons()
                st.session_state["just_submitted"] = True
                # st.rerun()



    if st.button("🔄 Refresh App"):
        st.rerun()


def clean_supabase_value(value, default=0):
    """Clean PostgreSQL literal values from Supabase"""
    if value is None or value == "":
        return default
    
    value_str = str(value)
    
    # Handle PostgreSQL cast format: '0'::double precision
    if "::" in value_str:
        value_str = value_str.split("::")[0]
        value_str = value_str.strip("'").strip('"')
    
    # Try to convert to number
    try:
        return int(float(value_str))
    except (ValueError, TypeError):
        return default