import streamlit as st
import data.strava as strav


# Add this to your existing fetch function
@st.cache_data(ttl=3600)
def fetch_all_activities_old(days_back: int = 7):
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


# In your main file
import streamlit as st
import pandas as pd
from data.zoneprocessor import (
    calculate_hr_zones_from_streams,
    calculate_pace_zones_from_streams,
)


@st.cache_data(ttl=3600)
def fetch_all_activities(days_back: int = 7, include_zones: bool = False):
    """
    Fetch all activities and optionally calculate zone distributions.

    Args:
        days_back: Number of days to look back
        include_zones: If True, fetches streams and calculates zones (slower but more data)

    Returns:
        Dictionary with 'activities' list and optional 'zones' list
    """
    users = st.secrets["users"]
    all_activities = []
    all_zones = []  # Store zone data separately

    for name, creds in users.items():
        try:
            strava = strav.StravaAPI(
                client_id=creds["client_id"],
                client_secret=creds["client_secret"],
                access_token=creds["access_token"],
                refresh_token=creds["refresh_token"],
            )

            # Get athlete profile for max HR
            profile = strava.get_athlete_profile()
            athlete_max_hr = profile.get("max_heart_rate") if profile else None

            # Fetch activities
            activities = strava.get_all_activities(days_back=days_back)

            for act in activities:
                act["athlete_name"] = name
                all_activities.append(act)

                # Calculate zones for this activity if requested
                if include_zones:
                    try:
                        # Fetch streams for this specific activity
                        streams = strava.get_activity_streams(
                            act["id"], types=["heartrate", "velocity_smooth", "time"]
                        )

                        if streams:
                            # Calculate HR zones
                            hr_zones = calculate_hr_zones_from_streams(
                                streams, athlete_max_hr=athlete_max_hr
                            )

                            # Calculate Pace zones
                            pace_zones = calculate_pace_zones_from_streams(streams)

                            # Store zone results
                            if hr_zones:
                                for zone in hr_zones:
                                    zone["activity_id"] = act["id"]
                                    zone["activity_date"] = act["start_date"]
                                    zone["athlete_name"] = name
                                    zone["metric_type"] = "HEARTRATE"
                                    all_zones.append(zone)

                            if pace_zones:
                                for zone in pace_zones:
                                    zone["activity_id"] = act["id"]
                                    zone["activity_date"] = act["start_date"]
                                    zone["athlete_name"] = name
                                    zone["metric_type"] = "PACE"
                                    all_zones.append(zone)

                    except Exception as zone_error:
                        st.warning(
                            f"Could not calculate zones for activity {act['id']}: {zone_error}"
                        )

        except Exception as e:
            st.error(f"Error fetching {name}: {e}")

    return {"activities": all_activities, "zones": all_zones if include_zones else None}


@st.cache_data(ttl=3600)
def fetch_zones_for_activities(activity_ids: list):
    """
    Fetch and calculate zones for specific activities only.
    This is more efficient than recalculating everything.

    Args:
        activity_ids: List of activity IDs to process

    Returns:
        DataFrame with zone data for all specified activities
    """
    users = st.secrets["users"]
    all_zones = []

    for name, creds in users.items():
        strava = strav.StravaAPI(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            access_token=creds["access_token"],
            refresh_token=creds["refresh_token"],
        )

        # Get athlete profile for max HR
        profile = strava.get_athlete_profile()
        athlete_max_hr = profile.get("max_heart_rate") if profile else None

        for activity_id in activity_ids:
            try:
                # Fetch streams for this activity
                streams = strava.get_activity_streams(
                    activity_id, types=["heartrate", "velocity_smooth", "time"]
                )

                if not streams:
                    continue

                # Get activity summary
                activity = strava.get_activity(activity_id)

                # Calculate zones
                hr_zones = calculate_hr_zones_from_streams(streams, athlete_max_hr)
                pace_zones = calculate_pace_zones_from_streams(streams)

                # Store results
                if hr_zones:
                    for zone in hr_zones:
                        zone["activity_id"] = activity_id
                        zone["activity_date"] = activity.start_date
                        zone["athlete_name"] = name
                        zone["metric_type"] = "HEARTRATE"
                        all_zones.append(zone)

                if pace_zones:
                    for zone in pace_zones:
                        zone["activity_id"] = activity_id
                        zone["activity_date"] = activity.start_date
                        zone["athlete_name"] = name
                        zone["metric_type"] = "PACE"
                        all_zones.append(zone)

            except Exception as e:
                st.warning(f"Error fetching zones for activity {activity_id}: {e}")

    return pd.DataFrame(all_zones) if all_zones else pd.DataFrame()
