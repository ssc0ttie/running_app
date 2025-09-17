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
