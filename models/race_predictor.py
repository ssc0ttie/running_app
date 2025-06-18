def race_predictor(data):
    import streamlit as st
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score

    import numpy as np

    # --- Load and clean data --- #
    df = data

    def load_data(df):
        df["Elapsed Time"] = pd.to_timedelta(df["Moving_Time"], errors="coerce")
        df["Elapsed Minutes"] = df["Elapsed Time"].dt.total_seconds() / 60
        df["RPE (1–10 scale)"] = pd.to_numeric(df["RPE (1–10 scale)"], errors="coerce")
        df["HR (bpm)"] = pd.to_numeric(df["HR (bpm)"], errors="coerce")
        df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")
        df["Cadence (steps/min)"] = pd.to_numeric(
            df["Cadence (steps/min)"], errors="coerce"
        )

        return df.dropna(
            subset=[
                "Elapsed Minutes",
                "Distance",
                "RPE (1–10 scale)",
                "HR (bpm)",
                "Cadence (steps/min)",
            ],
        )

    df_predict = load_data(df)
    df_predict = df_predict[
        ~df_predict["Activity"].str.contains("tempo", case=False, na=False)
        & ~df_predict["Activity"].isin(["Warm up", "Cooldown", 0])
    ]

    # --- Train model --- #
    X = df_predict[["Distance", "RPE (1–10 scale)", "HR (bpm)", "Cadence (steps/min)"]]
    y = df_predict["Elapsed Minutes"]

    model = LinearRegression()
    model.fit(X, y)

    # --- User Input --- #
    # st.header("⏱️ Predict Your Race Time")

    distance = st.selectbox(
        "Select Target Distance (km)", options=[1, 3, 5, 10, 15, 21.1, 42.2]
    )
    rpe = st.selectbox("Expected RPE (1–10)", options=list(range(1, 11)), index=1)
    hr = st.selectbox("Expected HR (bpm)", options=list(range(100, 201, 5)), index=9)
    cadence = st.selectbox(
        "Expected Cadence (steps/min)", options=list(range(140, 200, 5)), index=4
    )

    # --- Predict --- #
    input_df = pd.DataFrame(
        [[distance, rpe, hr, cadence]],
        columns=[
            "Distance",
            "RPE (1–10 scale)",
            "HR (bpm)",
            "Cadence (steps/min)",
        ],
    )
    predicted_time_min = model.predict(input_df)[0]

    # --- Format time --- #
    hours = int(predicted_time_min // 60)
    minutes = int(predicted_time_min % 60)
    seconds = int((predicted_time_min * 60) % 60)
    formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    # --- Calculate predicted pace --- #
    pace_min_per_km = predicted_time_min / distance
    pace_min = int(pace_min_per_km)
    pace_sec = int((pace_min_per_km - pace_min) * 60)
    formatted_pace = f"{pace_min}:{pace_sec:02d} min/km"

    # --- Display --- #
    st.success(f"🏁 Predicted Time for {distance}km: **{formatted_time}**")
    st.info(f"🔥 Estimated Pace: **{formatted_pace}**")

    ## -------------------RIEGEL METHOD COMPARISON -------------------##

    # Get best effort from history
    best_row = df_predict.sort_values(by="Elapsed Minutes").iloc[0]
    D1 = best_row["Distance"]
    T1 = best_row["Elapsed Minutes"]

    if pd.isna(T1) or pd.isna(D1) or D1 == 0:
        st.warning("❗ Not enough valid past run data for Riegel prediction.")
    else:
        T2 = T1 * (distance / D1) ** 1.06

        if pd.isna(T2):
            st.warning(
                "❗ Riegel prediction could not be calculated due to missing data."
            )
        else:
            r_hours = int(T2 // 60)
            r_minutes = int(T2 % 60)
            r_seconds = int((T2 * 60) % 60)
            riegel_time = f"{r_hours:02}:{r_minutes:02}:{r_seconds:02}"
            st.warning(f"🧮 Riegel Prediction for {distance}km: **{riegel_time}**")
