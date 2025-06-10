import data.read_data as rd
import pandas as pd


def generatechart():
    df = pd.DataFrame(rd.get_runner_data())
    # ensure that datetime is a date
    # df["Date_of_Activity"] = pd.to_datetime(df["Date_of_Activity"])

    # filters all distance > zero
    df = df[df["Distance"] > 0 & df["Distance"].notna()]

    ##GROUP BY
    act_date_group = df.groupby("Week_Number", as_index=False)

    st.subheader("Distance")

    line_data = act_date_group["Distance"].sum()

    st.bar_chart(line_data, x="Week_Number", y="Distance", y_label="Distance")

    ##FILTER BY MEMBER ##
    filt = df["Member_Name"] == mem_selection

    df.loc[filt]
