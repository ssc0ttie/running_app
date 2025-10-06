def update_runner_data(old_key, updated_data):
    from data import read_data_uncached as pull
    import traceback

    """
    Update an existing runner data entry based on timestamp
    
    Args:
        timestamp: The unique timestamp of the entry to update
        updated_data: Dictionary containing the updated values
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # This will depend on your data storage method
        # Here's an example if you're using Google Sheets:

        # First, find the row with the matching timestamp
        worksheet = pull.get_worksheet_object()  # Your function to get the worksheet

        print(f"Looking for old key: {old_key}")
        print(f"Worksheet type: {type(worksheet)}")

        #### DEBUG: Get all timestamps from the first column
        all_keys = worksheet.col_values(1)  # Get all values from column A
        print(f"First few keys in sheet: {all_keys[:5]}")

        # Try to find exact match
        cell = worksheet.find(old_key)
        print(f"Find result: {cell}")

        if cell:
            row_index = cell.row

            # Prepare the updated row data
            updated_row = [
                updated_data["UniqueKey"],
                updated_data["TimeStamp"],
                updated_data["Date_of_Activity"],
                updated_data["Activity"],
                updated_data["Distance"],
                updated_data["Pace"],
                updated_data["HR (bpm)"],
                updated_data["Cadence (steps/min)"],
                updated_data["RPE (1–10 scale)"],
                updated_data["Shoe"],
                updated_data["Remarks"],
                updated_data["Member Name"],
                updated_data["Duration_Other"],
            ]
            # Update the row
            worksheet.update(f"A{row_index}:M{row_index}", [updated_row])
            return True
        else:
            print(f"Entry with timestamp {old_key} not found")
            return False

    except Exception as e:
        print(f"Error updating data: {e}")
        traceback.print_exc()  # This will show the full error traceback
        return False


def update_runner_data_user_field(old_key, updated_data):
    from data import read_data_uncached as pull
    import traceback

    """
    Update an existing runner data entry based on timestamp
    
    Args:
        timestamp: The unique timestamp of the entry to update
        updated_data: Dictionary containing the updated values
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # This will depend on your data storage method
        # Here's an example if you're using Google Sheets:

        # First, find the row with the matching timestamp
        worksheet = pull.get_worksheet_object()  # Your function to get the worksheet

        print(f"Looking for old key: {old_key}")
        print(f"Worksheet type: {type(worksheet)}")

        #### DEBUG: Get all timestamps from the first column
        all_keys = worksheet.col_values(1)  # Get all values from column A
        print(f"First few keys in sheet: {all_keys[:5]}")

        # Try to find exact match
        cell = worksheet.find(old_key)
        print(f"Find result: {cell}")

        if cell:
            row_index = cell.row

            # Update only specific columns (hardcoded positions in sheet)
            # Adjust column numbers if your sheet layout is different
            worksheet.update_cell(row_index, 4, updated_data["Activity"])  # Col D
            worksheet.update_cell(
                row_index, 9, updated_data["RPE (1–10 scale)"]
            )  # Col I
            worksheet.update_cell(row_index, 10, updated_data["Shoe"])  # Col J
            worksheet.update_cell(row_index, 11, updated_data["Remarks"])  # Col K

            return True
        else:
            print(f"Entry with timestamp {old_key} not found")
            return False

    except Exception as e:
        print(f"Error updating data: {e}")
        traceback.print_exc()  # This will show the full error traceback
        return False


def update_runner_data_bulk(updates_list):
    """
    Bulk update multiple rows at once

    Args:
        updates_list: List of tuples (old_key, updated_data)

    Returns:
        tuple: (success_count, error_count)
    """
    from data import read_data_uncached as pull
    import traceback

    try:
        worksheet = pull.get_worksheet_object()
        all_keys = worksheet.col_values(1)

        batch_updates = []
        success_count = 0

        for old_key, updated_data in updates_list:
            cell = worksheet.find(old_key)
            if cell:
                row_index = cell.row
                batch_updates.extend(
                    [
                        {
                            "range": f"D{row_index}",
                            "values": [[updated_data["Activity"]]],
                        },
                        {
                            "range": f"I{row_index}",
                            "values": [[updated_data["RPE (1–10 scale)"]]],
                        },
                        {"range": f"J{row_index}", "values": [[updated_data["Shoe"]]]},
                        {
                            "range": f"K{row_index}",
                            "values": [[updated_data["Remarks"]]],
                        },
                    ]
                )
                success_count += 1

        # Execute all updates in one API call
        if batch_updates:
            worksheet.batch_update(batch_updates)
            print(f"Bulk update: {success_count} rows updated in single API call")

        return success_count, len(updates_list) - success_count

    except Exception as e:
        print(f"Error in bulk update: {e}")
        traceback.print_exc()
        return 0, len(updates_list)


def update_runner_data_bulk_old(old_key, updated_data):
    from data import read_data_uncached as pull
    import traceback

    try:
        client = pull.get_gsheet_client()
        sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

        # Try finding the key in BOTH worksheets
        worksheet_hist = sheet.get_worksheet_by_id(1508007696)  # Historical
        worksheet_new = sheet.get_worksheet_by_id(1611308583)  # New logs

        print(f"Looking for old key: {old_key}")

        # Try new logs worksheet first (most likely for recent entries)
        cell = worksheet_new.find(old_key)
        if cell:
            print(f"Found in NEW logs worksheet at row {cell.row}")
            worksheet = worksheet_new
        else:
            # Try historical worksheet
            cell = worksheet_hist.find(old_key)
            if cell:
                print(f"Found in HISTORICAL worksheet at row {cell.row}")
                worksheet = worksheet_hist
            else:
                print(f"Entry with key {old_key} not found in either worksheet")
                return False

        row_index = cell.row

        # Use batch update
        updates = [
            {"range": f"D{row_index}", "values": [[updated_data["Activity"]]]},
            {"range": f"I{row_index}", "values": [[updated_data["RPE (1–10 scale)"]]]},
            {"range": f"J{row_index}", "values": [[updated_data["Shoe"]]]},
            {"range": f"K{row_index}", "values": [[updated_data["Remarks"]]]},
        ]

        worksheet.batch_update(updates)
        print(f"Successfully updated row {row_index} in worksheet")
        return True

    except Exception as e:
        print(f"Error updating data for key {old_key}: {e}")
        traceback.print_exc()
        return False


def update_runner_data_bulk_new(updates_list):
    """
    Bulk update multiple rows at once

    Args:
        updates_list: List of tuples (old_key, updated_data)

    Returns:
        tuple: (success_count, error_count)
    """
    from data import read_data_uncached as pull
    import traceback

    try:
        client = pull.get_gsheet_client()
        sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")

        worksheet_hist = sheet.get_worksheet_by_id(1508007696)  # Historical
        worksheet_new = sheet.get_worksheet_by_id(1611308583)  # New logs

        batch_updates = []
        success_count = 0

        for old_key, updated_data in updates_list:
            print(f"Looking for old key: {old_key}")

            # Try new logs worksheet first
            cell = worksheet_new.find(old_key)
            if cell:
                print(f"Found in NEW logs worksheet at row {cell.row}")
                worksheet = worksheet_new
            else:
                # Try historical worksheet
                cell = worksheet_hist.find(old_key)
                if cell:
                    print(f"Found in HISTORICAL worksheet at row {cell.row}")
                    worksheet = worksheet_hist
                else:
                    print(f"Entry with key {old_key} not found in either worksheet")
                    continue  # Skip this entry

            row_index = cell.row

            # Add updates to batch
            batch_updates.extend(
                [
                    {"range": f"D{row_index}", "values": [[updated_data["Activity"]]]},
                    {
                        "range": f"I{row_index}",
                        "values": [[updated_data["RPE (1–10 scale)"]]],
                    },
                    {"range": f"J{row_index}", "values": [[updated_data["Shoe"]]]},
                    {"range": f"K{row_index}", "values": [[updated_data["Remarks"]]]},
                ]
            )
            success_count += 1

        # Execute all updates in one API call
        if batch_updates:
            # Group updates by worksheet and execute separately
            new_updates = [
                update for update in batch_updates if "worksheet" not in update
            ]  # Adjust logic as needed
            hist_updates = [
                update for update in batch_updates if "worksheet" not in update
            ]  # Adjust logic as needed

            if new_updates:
                worksheet_new.batch_update(new_updates)
            if hist_updates:
                worksheet_hist.batch_update(hist_updates)

            print(f"Bulk update: {success_count} rows updated")

        return success_count, len(updates_list) - success_count

    except Exception as e:
        print(f"Error in bulk update: {e}")
        traceback.print_exc()
        return 0, len(updates_list)
