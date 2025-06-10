import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
import time as tm
from datetime import time, datetime


st.title("🏃‍♂️Training Log")


Welcome_msg = (
    "Celebrate progress, not perfection. You showed up — and that matters most."
)
st.subheader(Welcome_msg)

# LAYOUT COLOUMNS
col1, col2 = st.columns(2)

with col1:

    with st.form("activity_log"):
        # Member list
        mem_selection = st.multiselect(
            "Members",
            ["Aiza", "Chona", "Fraulein", "Lead", "Maxine", "Scott"],
            max_selections=1,
        )
        # member_name = st.markdown(f"Select Member", {mem_selection})
        date = st.date_input("Date of Activity", value=datetime.today())

        # Activity list
        act_selection = st.multiselect(
            "Activity",
            [
                "5k LSD Road@ Zone 2 Pace",
                "6k LSD Road@ Zone 2 Pace",
                "8k LSD Road@ Zone 2 Pace",
                "10k LSD Road@ Zone 2 Pace",
                "10k LSD Trail@ Zone 2 Pace",
                "11k LSD Road@ Zone 2 Pace",
                "12k LSD Road@ Zone 2 Pace",
                "14k LSD Road@ Zone 2 Pace",
                "15k LSD Road@ Zone 2 Pace",
                "15k LSD Trail@ Zone 2 Pace",
                "17k LSD Road@ Zone 2 Pace",
                "18k LSD Road@ Zone 2 Pace",
                "19k LSD Road@ Zone 2 Pace",
                "20k LSD Road@ Zone 2 Pace",
                "20k LSD Trail@ Zone 2 Pace",
                "21k LSD Trail@ Zone 2 Pace",
                "24k LSD Trail@ Zone 2 Pace",
                "26k LSD Road@ Zone 2 Pace",
                "27k LSD Trail@ Zone 2 Pace",
                "28k LSD Road@ Zone 2 Pace",
                "31k LSD Road@ Zone 2 Pace",
                "20 Mins Easy Run",
                "30 Mins Easy Run",
                "35 Mins Easy Run",
                "40 Mins Easy Run",
                "45 Mins Easy Run",
                "50 Mins Easy Run",
                "55 Mins Easy Run",
                "60 Mins Easy Run",
                "RACE DAY",
                "Rest",
                "Speed Work (Zone 4 : 3x400M)",
                "Speed Work (Zone 4 : 4x400M)",
                "Speed Work (Zone 4 : 5x400M)",
                "Speed Work (Zone 4 : 6x400M)",
                "Strength Training",
                "Cross Train",
                "1k Tempo",
                "2k Tempo",
                "3k Tempo",
                "4k Tempo",
                "5k Tempo",
                "6k Tempo",
                "7k Tempo",
                "8k Tempo",
                "9k Tempo",
                "10k Tempo",
            ],
        )

        distance = st.number_input("Distance")
        pace = st.time_input("Pace (min/km)", value=time(8, 45), step=60)
        hr = st.number_input("HR (bmp)", min_value=0, max_value=220)
        cad = st.number_input("Cadence (spm)", min_value=0, max_value=200)
        rpe = st.slider("RPE", 0, 10, 1)
        rpe2 = st.feedback(options="faces", key=int)
        shoe = st.multiselect(
            "Shoe",
            [
                "Adidas Adizero SL2",
                "Asics Purple",
                "Boston 12",
                "NB Rebel v3",
                "Nike",
                "Nike Winflo 10",
                "Novablast 3",
                "Adidas Pink",
                "Reebok Float Ride Energy 4",
                "Sketcher",
            ],
        )
        remarks = st.text_area("Remarks")
        submit = st.form_submit_button("Submit")

    ###Submit Notice
    with st.spinner("Wait lang...", show_time=True):
        tm.sleep(2)
    st.success("Done!")
    st.balloons()

###############TRAINING PLAN SECTION#############################################
st.subheader("TRAINING PLAN", divider="blue")

with st.expander("View Training Program"):
    prog_sheet = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRF_uf-orH_71Ibql9N1QZ2FSWblHhvX2_KzjN_SLOSlchsDz0Mo8jOBI9mQOONyeKJR4pEQOjXAjKt/pubhtml?gid=0&single=true"
    components.iframe(
        prog_sheet,
        width=1500,
        height=800,
    )


####TEST CHART#######


import data.read_data as rd
import pandas as pd

df = pd.DataFrame(rd.get_runner_data())
# ensure that datetime is a date
# df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"])

# filters all distance > zero
df = df[df["Distance"] > 0 & df["Distance"].notna()]

##GROUP BY
act_date_group = df.groupby("Week", as_index=False)

st.subheader("Distance")

line_data = act_date_group["Distance"].sum()

st.bar_chart(line_data, x="Week", y="Distance", y_label="Distance")


##FILTER BY MEMBER ##
filt = df["Member_Name"] == mem_selection

df.loc[filt]
