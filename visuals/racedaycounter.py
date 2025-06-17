def raceday_counter():
    import streamlit as st
    from datetime import datetime

    race_day = datetime(2025, 12, 7)
    today = datetime.today()
    days_left = (race_day - today).days

    if days_left > 1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; border-radius: 1rem; background: #f0f8ff; border: 2px dashed #4682b4;">
                <h2 style="color: #ff4500;font-size: 2rem">🏁 Countdown to Race Day!</h2>
                <h1 style="font-size: 3rem; color: #1e90ff;">{days_left} Days</h1>
                <p style="font-size: 1.5rem;">Lace up, stay strong, and keep pushing! 💪</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif days_left == 1:
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem; border-radius: 1rem; background: #fffacd; border: 2px solid #ffa500;">
                <h2 style="color: #ff4500;">🎉 Race Day is Tomorrow!</h2>
                <h1 style="font-size: 4rem;">Get hyped! 🔥</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif days_left == 0:
        st.markdown(
            """
            <div style="text-align: center; padding: 1rem; border-radius: 1rem; background: #d4edda; border: 2px solid #28a745;">
                <h2 style="color: #28a745;">🏃‍♂️ IT'S RACE DAY! 🏁</h2>
                <h1 style="font-size: 4rem;">GO CRUSH IT! 💥</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem; border-radius: 1rem; background: #e0e0e0; border: 2px dashed #a9a9a9;">
                <h2 style="color: #a9a9a9;">🏁 Race Day has passed</h2>
                <h1 style="font-size: 3rem;">Well done, champ! 🏅</h1>
            </div>
            """,
            unsafe_allow_html=True,
        )
