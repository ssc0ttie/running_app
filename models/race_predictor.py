def race_predictor(data):
    import streamlit as st
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    import numpy as np

    # --- Load and clean data --- #
    df = data

    def load_data(df):
        df["Elapsed Time"] = pd.to_timedelta(df["Moving_Time"], errors="coerce")
        df["Elapsed Minutes"] = df["Elapsed Time"].dt.total_seconds() / 60
        df["RPE (1–10 scale)"] = pd.to_numeric(df["RPE (1–10 scale)"], errors="coerce")
        df["HR (bpm)"] = pd.to_numeric(df["HR (bpm)"], errors="coerce")
        df["Distance"] = pd.to_numeric(df["Distance"], errors="coerce")
        return df.dropna(
            subset=["Elapsed Minutes", "Distance", "RPE (1–10 scale)", "HR (bpm)"]
        )

    df_predict = load_data(df)
    df_predict = df_predict[
        ~df_predict["Activity"].str.contains("tempo", case=False, na=False)
        & ~df_predict["Activity"].isin(["Warm up", "Cooldown", 0])
    ]

    # --- Train model --- #
    X = df_predict[["Distance", "RPE (1–10 scale)", "HR (bpm)"]]
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

    # --- Predict --- #
    input_df = pd.DataFrame(
        [[distance, rpe, hr]], columns=["Distance", "RPE (1–10 scale)", "HR (bpm)"]
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
