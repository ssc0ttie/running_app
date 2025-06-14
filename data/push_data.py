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
