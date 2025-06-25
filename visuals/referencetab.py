import streamlit as st
import pandas as pd


def ref_tab():

    # Reference Data
    reference_data = [
        {
            "Activity": "🚴‍♂️ Cross Train",
            "Definition": "A low-impact aerobic workout (e.g. cycling, swimming, rowing) to improve endurance and reduce injury risk without the pounding of running.",
        },
        {
            "Activity": "🏃‍♂️ Easy Run",
            "Definition": "A relaxed, conversational-pace run done at low intensity (Zone 1–2), meant to build endurance while keeping stress on the body low.",
        },
        {
            "Activity": "🧘 LSD @ Zone 2 Pace",
            "Definition": "Long Slow Distance run done at Zone 2 heart rate — steady, comfortable pace to build aerobic base and teach your body to burn fat efficiently.",
        },
        {
            "Activity": "🌲 LSDTrail @ Zone 2 Pace",
            "Definition": "Same as LSD, but done on trails — great for building strength, balance, and variety with softer impact on joints.",
        },
        {
            "Activity": "🛌 Rest",
            "Definition": "A complete day off from training to allow your body to recover, rebuild, and adapt — just as important as the workouts!",
        },
        {
            "Activity": "⚡ Speed Work (Zone 5: 6x400M)",
            "Definition": "Interval training at a hard effort (Zone 5 HR) — e.g. 6 repeats of 400 meters fast, with recovery jogs or walks between. Boosts power & speed.",
        },
        {
            "Activity": "🏋️ Strength Training",
            "Definition": "Bodyweight or weight-based resistance training (e.g. squats, lunges, core work) to improve stability, reduce injury risk, and support running.",
        },
        {
            "Activity": "🔥 Tempo Run",
            "Definition": "A run at a “comfortably hard” pace — typically Zone 3— faster than easy pace but sustainable for 20–40 mins; builds lactate threshold.",
        },
    ]

    # Create tab layout

    st.header("📘 Types of Activity")

    for ref in reference_data:
        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 1rem;">
                    <h4 style="color:#0e1117;">{ref['Activity']}</h4>
                    <p style="color:#4f4f4f;">{ref['Definition']}</p>
                </div>
            """,
                unsafe_allow_html=True,
            )
    st.header("🧭 Activity Priority")
    st.markdown(
        """
            ### 🏃‍♀️ Run Types – Priority & Importance

            ---

            #### 🥇 **Must-Do (Core Runs)**  
            - 🟢 **LSD @ Zone 2 (Road)**  
            ⭐⭐⭐⭐⭐ – *Most important*. Builds endurance and aerobic base. Don’t skip.  
            - 🟢 **LSD Trail @ Zone 2**  
            ⭐⭐⭐⭐☆ – Adds variety and time-on-feet with less impact. Helpful especially for trail races.  

            ---

            #### 🥈 **Should-Do (Performance Boosters)**  
            - 🔵 **Tempo Run**  
            ⭐⭐⭐⭐☆ – Improves lactate threshold and race pace. Do if energy allows.  
            - 🔵 **Easy Run**  
            ⭐⭐⭐⭐☆ – Helps recovery and builds volume. Can be skipped *sometimes* if needed.  

            ---

            #### 🥉 **Optional (Complementary)**  
            - 🟡 **Speed Work (6x400m @ Zone 5)**  
            ⭐⭐⭐☆ – Good for sharpness and running form. Skip if feeling tired or still building base.  
            - 🟡 **Strength Training**  
            ⭐⭐⭐☆ – Injury prevention & muscle balance. 2x/week is ideal. Bodyweight okay.  

            ---

            #### 🌀 **Substitutes & Support**  
            - ⚪ **Cross Training**  
            ⭐⭐☆☆☆ – Useful substitute for recovery or injury. Non-essential but helpful.  
            - 🔴 **Rest**  
            ⭐⭐⭐⭐⭐ – *Absolutely critical*. One full day weekly. No compromise.  

            ---

            ### ✅ If Busy, You Can Skip:
            - Cross Train  
            - 1 Easy Run  
            - Speed Work (if tired)  
            - 1 Strength Session

            ### ❌ But NEVER Skip:
            - Long Run (LSD)  
            - Rest Day  
            - Taper Weeks  
            """,
        unsafe_allow_html=True,
    )
