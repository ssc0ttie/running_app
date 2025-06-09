import pandas as pd


def get_runner_data():
    """
    https://docs.google.com/spreadsheets/d/1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM/edit?usp=sharing

    """
    sheet_id = "1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM"
    historical_log_gid = "1233739225"
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
            "  Pace (min/km)",
            "Time (moving time)",
            "HR (bpm)",
            "Cadence (steps/min)",
            "RPE (1–10 scale)",
            "Shoe",
            "Remarks",
            "Member_Name",
            "dummy",
        ],
    )

    # return pd.DataFrame(df)


sheet_id = "1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM"
historical_log_gid = "1233739225"
week_lookup_gid = "336401596"
prog_gid = 0
url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid="


df_week_lookup = pd.read_csv(f"{url}{week_lookup_gid}", header=None)
