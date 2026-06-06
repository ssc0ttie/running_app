# data/fetch_strava_automation_supa.py
"""
Streamlit-free version for GitHub Actions automation - SUPABASE VERSION
"""

import os
import json
import requests
from datetime import datetime, timedelta
import time

# Import your working Strava API class from data.strava
from data import strava as strav


def get_users():
    """Get users from environment variables (for automation)"""
    users_json = os.environ.get("STRAVA_USERS")
    if users_json:
        return json.loads(users_json)

    # Fallback for local testing
    try:
        import streamlit as st
        return st.secrets["users"]
    except:
        raise Exception("No users found in STRAVA_USERS env var or streamlit secrets")


def fetch_all_activities(days_back: int = 7):
    """Fetch activities for all users - NO STREAMLIT DEPENDENCIES"""
    users = get_users()
    all_activities = []

    for name, creds in users.items():
        try:
            print(f"  • Fetching for {name}...")

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
                print(f"    ✅ Fetched {len(activities)} activities for {name}")
            else:
                print(f"    ⚠️ Could not get profile for {name}")

        except Exception as e:
            print(f"    ❌ Error fetching {name}: {e}")

    return all_activities