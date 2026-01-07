def raceday_counter():
    import streamlit as st
    from datetime import datetime
    from zoneinfo import ZoneInfo

    sg_now = datetime.now(ZoneInfo("Asia/Singapore"))

    st.write(sg_now)

    race_day = datetime(2026, 4, 5)
    race_day = race_day.date()
    st.write(race_day)

    today = sg_now.date()
    now_ = datetime.now()
    days_left = (race_day - now_.date()).days

    st.write(days_left)
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


def raceday_counter_2():
    import streamlit as st
    from datetime import datetime
    from zoneinfo import ZoneInfo

    sg_now = datetime.now(ZoneInfo("Asia/Singapore"))
    race_day = datetime(2026, 4, 5, tzinfo=ZoneInfo("Asia/Singapore"))

    st.write(sg_now)
    st.write(race_day)

    today = sg_now.date()
    now_ = sg_now

    # Calculate time difference
    time_diff = race_day - now_

    # Extract components
    days_left = time_diff.days
    hours_left = time_diff.seconds // 3600
    minutes_left = (time_diff.seconds % 3600) // 60
    seconds_left = time_diff.seconds % 60

    st.write(days_left)
    if days_left > 1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(1, 0, 0, 0);">
                <h4 style="color: #2e8b57; margin-bottom: 0.5rem;">🏁 Countdown to Race Day! 🏁</h4>
                <p style="font-size: 2rem; color: #811331; margin: 0;"><strong>{days_left} Days</strong></p>
                <p style="font-size: 1.5rem; color: #811331; margin: 0.25rem 0;">
                    {hours_left:02d}h {minutes_left:02d}m {seconds_left:02d}s
                </p>
                <p style="font-size: 1rem; color: #2f3e46; margin-top: 0.25rem;">Stay consistent. Trust the process. You've got this 💪</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    elif days_left == 1:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(0, 0, 0, 0); border: 1px solid #2e8b57;">
                <h4 style="color: #2e8b57; margin-bottom: 0.5rem;">🎉 Race Day is Tomorrow!</h4>
                <p style="font-size: 1.75rem; color: #2f3e46; margin: 0;"><strong>{days_left} Day</strong></p>
                <p style="font-size: 1.25rem; color: #2f3e46; margin: 0.25rem 0;">
                    {hours_left:02d}h {minutes_left:02d}m {seconds_left:02d}s
                </p>
                <p style="font-size: 1rem; color: #2f3e46; margin-top: 0.25rem;">Final prep time! Get some rest! 🛌</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    elif days_left == 0:
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(0, 0, 0, 0); border: 1px solid #2e8b57;">
                <h4 style="color: #2e8b57; margin-bottom: 0.5rem;">🏃‍♂️ It's Race Day!</h4>
                <p style="font-size: 1.75rem; color: #2f3e46; margin: 0;"><strong>Today!</strong></p>
                <p style="font-size: 1.25rem; color: #2f3e46; margin: 0.25rem 0;">
                    {hours_left:02d}h {minutes_left:02d}m {seconds_left:02d}s
                </p>
                <p style="font-size: 1rem; color: #2f3e46; margin-top: 0.25rem;">Run your heart out! 🏁</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        days_passed = abs(days_left)
        st.markdown(
            f"""
            <div style="text-align: center; padding: 0.75rem; border-radius: 0.5rem;
                        background-color: rgba(0, 0, 0, 0); border: 1px solid #2e8b57;">
                <h4 style="color: #2e8b57; margin-bottom: 0.5rem;">🏁 Race Day has passed</h4>
                <p style="font-size: 1.25rem; color: #2f3e46; margin: 0.25rem 0;">
                    {days_passed} days ago
                </p>
                <p style="font-size: 1rem; color: #2f3e46; margin-top: 0.25rem;">You did it! Time to recover and reflect 🏅</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
