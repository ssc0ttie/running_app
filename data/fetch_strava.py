import streamlit as st
import data.strava as strav


# Add this to your existing fetch function
@st.cache_data(ttl=3600)
def fetch_all_activities(days_back: int = 7):
    users = st.secrets["users"]
    """Your existing fetch function"""
    # users = load_strava_users()
    all_activities = []

    for name, creds in users.items():
        try:
            strava = strav.StravaAPI(
                client_id=creds["client_id"],
                client_secret=creds["client_secret"],
                access_token=creds["access_token"],
                refresh_token=creds["refresh_token"],
            )

            profile = strava.get_athlete_profile()
            if profile:
                activities = strava.get_all_activities(days_back=days_back)

                for act in activities:
                    act["athlete_name"] = name

                all_activities.extend(activities)

        except Exception as e:
            st.error(f"Error fetching {name}: {e}")

    return all_activities
