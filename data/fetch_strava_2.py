import streamlit as st
import data.strava as strav

# data/fetch_strava.py
import pandas as pd
import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")


# Define fallback print functions
def _print_info(msg):
    print(f"ℹ️ {msg}")


def _print_success(msg):
    print(f"✅ {msg}")


def _print_error(msg):
    print(f"❌ {msg}")


# Try to import Streamlit
try:
    import streamlit as st

    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

    # Create dummy st functions
    class DummySt:
        def cache_data(self, *args, **kwargs):
            def decorator(func):
                return func

            return decorator

        def error(self, msg):
            _print_error(msg)

        def info(self, msg):
            _print_info(msg)

        def success(self, msg):
            _print_success(msg)

        def warning(self, msg):
            print(f"⚠️ {msg}")

    st = DummySt()

from data import strava as strav


def get_users():
    """Get users from either st.secrets or environment variables"""
    if HAS_STREAMLIT:
        try:
            return st.secrets["users"]
        except:
            pass

    # Fall back to environment variable
    import json

    users_json = os.environ.get("STRAVA_USERS")
    if users_json:
        return json.loads(users_json)

    raise Exception("No users found in st.secrets or STRAVA_USERS env var")


@st.cache_data(ttl=3600)
def fetch_all_activities(days_back: int = 7):
    """Fetch activities for all users"""
    users = get_users()
    all_activities = []

    for name, creds in users.items():
        try:
            st.info(f"Fetching data for {name}...")

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
                st.success(f"Fetched {len(activities)} activities for {name}")

        except Exception as e:
            st.error(f"Error fetching {name}: {e}")

    return all_activities
