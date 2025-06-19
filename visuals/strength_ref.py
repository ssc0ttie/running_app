def general_str_ref():

    import streamlit as st

    st.header("🏋️ Strength Training Programs")

    st.markdown("### 🏋️‍♂️ Option 1: Full Body Training")
    st.markdown("**💡 Reps Guide:**")
    st.markdown("- 3 sets of 8–12 reps for **strength**")
    st.markdown("- 12–15 reps for **endurance** (e.g., calves, bodyweight)")

    with st.expander("💪 Program A – Full Body Stability & Strength"):
        st.markdown(
            """
        | Exercise               | Weighted Variation                                  | Bodyweight Alternative                                |
        |------------------------|-----------------------------------------------------|--------------------------------------------------------|
        | Bulgarian Split Squat  | Dumbbells/kettlebells in each hand                 | Hands on hips or arms forward for balance             |
        | Romanian Deadlift (RDL)| With dumbbells or barbell                          | Single-leg hip hinge (no weight)                      |
        | Standing Calf Raises   | Hold dumbbells; use step for full stretch          | On edge of step, slow and controlled                  |
        | Push-up                | Weighted vest or elevate feet for difficulty       | Standard push-up or incline (hands elevated)          |
        | One-arm Dumbbell Row   | On bench or sturdy surface                         | Body row under table or resistance band row           |
        | Plank + Shoulder Taps  | Add weight plate on back or longer hold            | Regular plank with slow shoulder taps                 |
        """,
            unsafe_allow_html=True,
        )

    with st.expander("🏋️ Program B – Posterior Chain Focus"):
        st.markdown(
            """
        | Exercise                | Weighted Variation                                 | Bodyweight Alternative                                |
        |-------------------------|----------------------------------------------------|--------------------------------------------------------|
        | Step-ups (knee height)  | Dumbbells/kettlebells held at sides               | Step-up on sturdy chair or bench                      |
        | Glute Bridge            | Barbell or dumbbell on hips                       | Single-leg glute bridge on floor                      |
        | Calf Raises (Bent Knee) | Dumbbell in one hand, seated or standing          | Seated bent-knee calf raise (bodyweight)             |
        | Inverted Row            | Under sturdy table or TRX with feet elevated      | Lower incline or standard under-table row             |
        | Overhead Press          | Dumbbells/barbell                                 | Pike push-up or wall handstand hold                   |
        | Side Plank w/ Reach-Through | Hold dumbbell for twist                    | Standard side plank + slow arm thread-through         |
        """,
            unsafe_allow_html=True,
        )

    with st.expander("🦵 Program C – Explosive & Core Strength"):
        st.markdown(
            """
        | Exercise                   | Weighted Variation                                | Bodyweight Alternative                                |
        |----------------------------|---------------------------------------------------|--------------------------------------------------------|
        | Goblet Squat               | Hold dumbbell or kettlebell at chest             | Air squat with slow tempo (5s down, 2s pause)         |
        | Bulgarian Split Squat Jump| Weighted vest or light dumbbells                 | Jumping BSS (explosive upward motion)                |
        | Single-leg Calf Raises     | Hold weight in opposite hand for balance         | On step, slow and controlled                          |
        | Deadlift to Row            | Use dumbbells/barbell                            | Hip hinge + towel/bodyweight row on surface           |
        | Pike Push-up               | Add pause at bottom or elevate feet              | Standard pike push-up                                 |
        | V-Ups or Hollow Body Hold  | Hold small weight between hands and feet         | Bodyweight V-ups or hollow hold with bent knees       |
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🦵 Option 2: Leg-Focused Bodyweight Supersets")
    st.markdown("**Instructions:**")
    st.markdown("- Do **3 sets** per superset")
    st.markdown("- **10 sec rest** between exercises")
    st.markdown("- **60 sec rest** between sets")

    with st.expander("🔥 Super Set 1"):
        st.markdown(
            """
        - **Single Leg Squat x20**  
            A squat on one leg; go low while maintaining balance and control.

        - **Single Leg Calf Raise x15 (per leg)**  
            Stand on one foot, lift heel, rise onto toes, lower slowly.

        - **Single Leg RDL x12 (per leg)**  
            Hinge forward on one leg, keeping hips back and back flat.
        """
        )

    with st.expander("🔥 Super Set 2"):
        st.markdown(
            """
        - **Clam Shells (M) x30**  
            Side-lying, knees bent, lift top knee while keeping feet together. *(M = Medium resistance band)*

        - **Reverse Lunge x12 (per leg)**  
            Step back into a lunge, lower rear knee, return to standing.

        - **Single Leg Soleus Calf Raise x15 (per leg)**  
            Bent-knee version of a calf raise; targets deeper soleus.
        """
        )

    with st.expander("🔥 Super Set 3"):
        st.markdown(
            """
        - **Single Leg Bridge x15 (per leg)**  
            Lie on back, lift one leg, push through heel to lift hips.

        - **Pogo Hops x25**  
            Fast, small jumps with stiff ankles — bounce using calves.

        - **Side Walks (M) x3 rounds**  
            With a medium band, step sideways with control and resistance.
        """
        )
