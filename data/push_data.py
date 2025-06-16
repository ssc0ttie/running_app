import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit as st
import pandas as pd
import data.read_data as rd


def push_runner_data(data):
    gsclient = rd.get_gsheet_client()
    client = gsclient
    sheet = client.open_by_key("1RDIWNLnrMR9SxR6uMxI-BuQlkefXPsGTlaQx2PQ7ENM")
    newsource_worksheet = sheet.get_worksheet_by_id(
        1611308583
    )  # or use get_worksheet_by_id(gid)

    newsource_worksheet.append_row(data)


# def push_runner_data_dev(hist_df, newlog_df):
#     path = r"C:/Users/king.m/Python/2025/DS Proj/running_app/data/runner_data.xlsx"

#     updated_df = pd.concat([hist_df, newlog_df], ignore_index=True)

#     # Optional cleanup (remove duplicates, sort, etc.)
#     updated_df.drop_duplicates(inplace=True)

#     # Write back to Excel (overwrites existing content in that sheet)
#     with pd.ExcelWriter(path, mode="w", engine="openpyxl") as writer:
#         updated_df.to_excel(writer, sheet_name="for streamlit", index=False)

#     return True
