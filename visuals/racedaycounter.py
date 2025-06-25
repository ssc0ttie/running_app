def raceday_counter():
    import streamlit as st
    from datetime import datetime
    from zoneinfo import ZoneInfo

    sg_now = datetime.now(ZoneInfo("Asia/Singapore"))
    race_day = datetime(2025, 12, 7)
    race_day = race_day.date()

    today = sg_now.date()
    now_ = datetime.now()
    days_left = (race_day - now_.date()).days

    # <p style="font-size: 1rem; color: #2f3e46; margin-top: 0.25rem;">Stay consistent. Trust the process . You've got this 💪</p>
    if days_left > 1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(1, 0, 0, 0);">
                <h4 style="color: #2e8b57; margin-bottom: 0.5rem;">🏁 Countdown to Race Day! 🏁</h4>
                <p style="font-size: 2.5rem; color: #811331; margin: 0;"><strong>{days_left} Days</strong></p>

            </div>
            """,
            unsafe_allow_html=True,
        )

    elif days_left == 1:
        st.markdown(
            """
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(0, 0, 0, 0); border: 1px solid #2e8b57;">
                <h4 style="color: #2e8b57;">🎉 Race Day is Tomorrow!</h4>
                <p style="font-size: 1.75rem; color: #2f3e46;">Final prep time!</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif days_left == 0:
        st.markdown(
            """
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(0, 0, 0, 0); border: 1px solid #2e8b57;">
                <h4 style="color: #2e8b57;">🏃‍♂️ It's Race Day!</h4>
                <p style="font-size: 1.75rem; color: #2f3e46;">Run your heart out! 🏁</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(0, 0, 0, 0); border: 1px solid #2e8b57;">
                <h4 style="color: #2e8b57;">🏁 Race Day has passed</h4>
                <p style="font-size: 1.25rem; color: #2f3e46;">You did it! Time to recover and reflect 🏅</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
