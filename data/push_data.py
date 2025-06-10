import pandas as pd

sheet_id = "1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM"
new_log_gid = "1611308583"
week_lookup_gid = "336401596"


def push_runner_data():
    sheet_id = "1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM"
    historical_log_gid = "1508007696"
    week_lookup_gid = "336401596"
    prog_gid = 0
    url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid="

    pd.set_option("display.max_colum", 50)

    # Read Historical Data and adding header names

    df = pd.read_csv(
        f"{url}{historical_log_gid}",
        header=None,
        names=[
            "TimeStamp",
            "Date_of_Activity",
            "Activity",
            "Distance",
            "Pace",
            "Time (moving time)",
            "HR (bpm)",
            "Cadence (steps/min)",
            "RPE (1–10 scale)",
            "Shoe",
            "Remarks",
            "Member Name",
        ],
    )
    ######DATA CLEANUP######
    df_week_lookup = pd.read_csv(f"{url}{week_lookup_gid}", header=None, skiprows=1)

    # filter only first 3 columns
    df2 = df_week_lookup[[0, 1, 2]].copy()
    # rename columns
    df2.columns = ["Date", "Week", "Scheduled_Activity"]

    # clean data columns used for calculations
    df2["Date"] = pd.to_datetime(df2["Date"])

    # cleanup main df
    df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"], errors="coerce")
    df["Pace"] = pd.to_timedelta(df["Pace"])
    df["Distance"] = pd.to_numeric(df["Distance"])

    # lookup of weekname
    df = df.merge(df2, left_on="Date_of_Activity", right_on="Date", how="left")
    # Apply to column

    # CALCULATE MOVING TIME
    df["Moving_Time"] = df["Pace"] * df["Distance"]

    return pd.DataFrame(df)
