#!/usr/bin/env python3
"""
Strava Zone Sync Script for GitHub Actions
Uses the same working functions as the manual process
Runs weekly to calculate and push HR and Pace zone distributions
"""

import os
import sys
import json
import warnings
import time
from datetime import datetime

# Suppress warnings
os.environ["STREAMLIT_WATCH_FILE"] = "false"
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
warnings.filterwarnings("ignore")

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import requests


class StravaAPI:
    """Strava API client for GitHub Actions (no Streamlit dependencies)"""
    
    def __init__(self, client_id, client_secret, access_token, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://www.strava.com/api/v3"

    def refresh_access_token(self):
        """Refresh the access token"""
        url = "https://www.strava.com/oauth/token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }
        
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            if "refresh_token" in tokens:
                self.refresh_token = tokens["refresh_token"]
            print("  ✅ Token refreshed successfully")
            return True
        else:
            print(f"  ❌ Token refresh failed: {response.text}")
            return False

    def get_activity_streams(self, activity_id, types=None):
        """Get activity streams"""
        if types is None:
            types = ['time', 'heartrate', 'velocity_smooth']
        
        params = {
            'keys': ','.join(types),
            'key_by_type': 'true'
        }
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(
            f"{self.base_url}/activities/{activity_id}/streams",
            headers=headers,
            params=params
        )
        
        # If token expired, refresh and retry
        if response.status_code == 401:
            print("    ⚠️ Token expired, refreshing...")
            if self.refresh_access_token():
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(
                    f"{self.base_url}/activities/{activity_id}/streams",
                    headers=headers,
                    params=params
                )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None

    def get_athlete_profile(self):
        """Get athlete profile to verify connection"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}/athlete", headers=headers)
        
        if response.status_code == 401:
            print("    ⚠️ Token expired, refreshing...")
            if self.refresh_access_token():
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/athlete", headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"    ❌ Profile fetch failed: {response.status_code}")
            return None


# Import the WORKING zone processor functions
def format_time(seconds):
    """Convert seconds to mm:ss format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


def format_pace(min_per_km):
    """Convert min/km to mm:ss format"""
    if min_per_km is None or min_per_km == float("inf"):
        return None
    minutes = int(min_per_km)
    seconds = int((min_per_km - minutes) * 60)
    return f"{minutes}:{seconds:02d}"


def calculate_hr_zones_from_streams(streams, athlete_name=None):
    """Calculate HR zones from streams using athlete's max HR"""
    if "heartrate" not in streams:
        return None
    
    heartrates = streams["heartrate"]["data"]
    times = streams["time"]["data"]
    
    if len(heartrates) < 2:
        return None
    
    time_diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    
    # Get max HR from athlete metrics (simplified for automation)
    # You can expand this to use your athlete_metrics.py
    max_hr = max(heartrates) if heartrates else 180
    
    zone_definitions = [
        {"zone": "Z1", "name": "Endurance", "min_pct": 0.50, "max_pct": 0.60},
        {"zone": "Z2", "name": "Moderate", "min_pct": 0.60, "max_pct": 0.70},
        {"zone": "Z3", "name": "Tempo", "min_pct": 0.70, "max_pct": 0.80},
        {"zone": "Z4", "name": "Threshold", "min_pct": 0.80, "max_pct": 0.90},
        {"zone": "Z5", "name": "Anaerobic", "min_pct": 0.90, "max_pct": 1.00},
    ]
    
    zones = []
    for zd in zone_definitions:
        zones.append({
            "zone": zd["zone"],
            "zone_name": zd["name"],
            "min_hr": int(zd["min_pct"] * max_hr),
            "max_hr": int(zd["max_pct"] * max_hr),
            "time_seconds": 0,
        })
    
    total_time = 0
    for i, hr in enumerate(heartrates[:-1]):
        for zone in zones:
            if zone["min_hr"] <= hr < zone["max_hr"]:
                zone["time_seconds"] += time_diffs[i]
                total_time += time_diffs[i]
                break
    
    for zone in zones:
        zone["percentage"] = round((zone["time_seconds"] / total_time * 100), 1) if total_time > 0 else 0
        zone["time_formatted"] = format_time(zone["time_seconds"])
    
    return zones


def calculate_pace_zones_from_streams(streams, athlete_name=None):
    """Calculate pace zones from streams using athlete's threshold pace"""
    if "velocity_smooth" not in streams:
        return None
    
    velocities = streams["velocity_smooth"]["data"]
    times = streams["time"]["data"]
    
    if len(velocities) < 2:
        return None
    
    time_diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    
    paces = []
    for v in velocities[:-1]:
        if v > 0:
            pace_min_km = (1 / v) * (1000 / 60)
            paces.append(pace_min_km)
        else:
            paces.append(None)
    
    # Default pace zones (you can expand to use athlete_metrics)
    zone_definitions = [
        {"zone": "Z1", "name": "Easy", "min_pace": 6.00, "max_pace": float("inf")},
        {"zone": "Z2", "name": "Endurance", "min_pace": 5.30, "max_pace": 6.00},
        {"zone": "Z3", "name": "Tempo", "min_pace": 4.50, "max_pace": 5.30},
        {"zone": "Z4", "name": "Threshold", "min_pace": 4.20, "max_pace": 4.50},
        {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": 4.20},
    ]
    
    zones = []
    for zd in zone_definitions:
        zones.append({
            "zone": zd["zone"],
            "zone_name": zd["name"],
            "min_pace": zd["min_pace"],
            "max_pace": zd["max_pace"] if zd["max_pace"] != float("inf") else None,
            "time_seconds": 0,
        })
    
    total_time = 0
    for i, pace in enumerate(paces):
        if pace is None:
            continue
        for zone in zones:
            min_pace = zone["min_pace"]
            max_pace = zone["max_pace"] if zone["max_pace"] else float("inf")
            if min_pace <= pace < max_pace:
                zone["time_seconds"] += time_diffs[i]
                total_time += time_diffs[i]
                break
    
    for zone in zones:
        zone["percentage"] = round((zone["time_seconds"] / total_time * 100), 1) if total_time > 0 else 0
        zone["time_formatted"] = format_time(zone["time_seconds"])
        if zone["min_pace"] is not None and zone["min_pace"] != float("inf"):
            zone["min_pace"] = format_pace(zone["min_pace"])
        if zone["max_pace"] is not None and zone["max_pace"] != float("inf"):
            zone["max_pace"] = format_pace(zone["max_pace"])
    
    return zones


# ============================================================
# Supabase functions (simplified for automation)
# ============================================================

def init_supabase_automation():
    """Initialize Supabase client for GitHub Actions (no Streamlit)"""
    from supabase import create_client
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials missing")
        return None
    
    return create_client(supabase_url, supabase_key)


def get_existing_zone_keys_automation():
    """Fetch existing Zone_UniqueKeys for duplicate checking"""
    supabase = init_supabase_automation()
    if not supabase:
        return set()
    
    try:
        response = supabase.table("zones").select("Zone_UniqueKey").execute()
        if response.data:
            return {row["Zone_UniqueKey"] for row in response.data}
        return set()
    except Exception as e:
        print(f"  ⚠️ Error fetching existing zone keys: {e}")
        return set()


def push_zone_data_to_supabase_automation(zones_df, parent_unique_key, activity_row_data):
    """Push zone data using the same logic as manual process"""
    supabase = init_supabase_automation()
    if not supabase:
        return 0, len(zones_df) if zones_df is not None else 0
    
    try:
        existing_keys = get_existing_zone_keys_automation()
        
        new_rows = []
        for _, row in zones_df.iterrows():
            zone_key = f"{parent_unique_key}_{row['Type']}_{row['Zone']}"
            
            if zone_key in existing_keys:
                continue
            
            new_row = {
                "Zone_UniqueKey": str(zone_key),
                "Parent_UniqueKey": str(parent_unique_key),
                "Date_of_Activity": str(activity_row_data["Date"]),
                "Member Name": str(activity_row_data["Member Name"]),
                "Activity": str(activity_row_data["Activity"]),
                "Avg_HR": int(activity_row_data["Avg_HR"]) if activity_row_data["Avg_HR"] else None,
                "Zone_Type": str(row["Type"]),
                "Zone": str(row["Zone"]),
                "Zone_Name": str(row["Zone Name"]),
                "Min_Value": str(row.get("Min", "")),
                "Max_Value": str(row.get("Max", "")),
                "Time_In_Zone": str(row.get("Time", "")),
                "Percentage": str(row.get("Percentage", ""))
            }
            new_rows.append(new_row)
        
        if not new_rows:
            return 0, 0
        
        # Use upsert like the manual function
        response = supabase.table("zones")\
            .upsert(new_rows, on_conflict="Zone_UniqueKey", ignore_duplicates=True)\
            .execute()
        
        success_count = len(response.data) if response.data else 0
        error_count = len(new_rows) - success_count
        
        return success_count, error_count
        
    except Exception as e:
        print(f"  ❌ Error pushing zones: {e}")
        return 0, len(zones_df) if zones_df is not None else 0


def fetch_activities_from_supabase(athlete_name, supabase_url, supabase_key, limit=50):
    """Fetch activities for a specific athlete from Supabase"""
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}"
    }
    
    activities_url = f"{supabase_url}/rest/v1/activities?select=id,\"Member Name\",\"Date_of_Activity\",\"HR (bpm)\",\"Activity\"&\"Member Name\"=eq.{athlete_name}&order=Date_of_Activity.desc&limit={limit}"
    
    response = requests.get(activities_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"  ❌ Failed to fetch activities: {response.status_code}")
        return []


def main():
    print("=" * 70)
    print(f"🚀 STRAVA ZONE SYNC - PRODUCTION")
    print(f"📍 Started at: {datetime.now()}")
    print("=" * 70)
    
    # Get days back (default 30)
    days_back = int(os.environ.get("DAYS_BACK", "30"))
    print(f"📅 Analyzing activities from the last {days_back} days")
    
    # Get users from environment
    users_json = os.environ.get("STRAVA_USERS", "{}")
    users = json.loads(users_json)
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    all_zones_pushed = 0
    total_activities_processed = 0
    
    for athlete_name, creds in users.items():
        print(f"\n👤 Processing {athlete_name}...")
        
        try:
            # Initialize Strava client
            strava = StravaAPI(
                client_id=creds["client_id"],
                client_secret=creds["client_secret"],
                access_token=creds["access_token"],
                refresh_token=creds["refresh_token"],
            )
            
            # Verify connection
            profile = strava.get_athlete_profile()
            if profile is None:
                print(f"  ⚠️ Could not connect for {athlete_name}, skipping")
                continue
            
            print(f"  ✅ Connected as {profile.get('firstname', athlete_name)}")
            
            # Fetch activities from Supabase
            activities = fetch_activities_from_supabase(athlete_name, supabase_url, supabase_key, limit=100)
            print(f"  📊 Found {len(activities)} activities in Supabase")
            
            for act in activities:
                strava_id = act.get('id')
                if not strava_id:
                    continue
                
                start_date = act.get('Date_of_Activity', '')
                act_type = act.get('Activity', '')
                avg_hr = act.get('HR (bpm)', 0)
                
                # Convert avg_hr to int
                try:
                    avg_hr = int(float(avg_hr))
                except (ValueError, TypeError):
                    avg_hr = 0
                
                # Only process activities that are likely to have streams
                if act_type not in ["Run", "Ride", "Walk"]:
                    continue
                
                # Build parent_unique_key
                parent_unique_key = f"{start_date}|{athlete_name}|{act_type}|{avg_hr}"
                
                activity_row_data = {
                    "Date": start_date,
                    "Member Name": athlete_name,
                    "Activity": act_type,
                    "Avg_HR": avg_hr
                }
                
                print(f"    📈 Processing {strava_id}: {start_date} | {act_type} | HR={avg_hr}")
                
                # Fetch streams
                streams = strava.get_activity_streams(strava_id)
                
                if streams and 'heartrate' in streams:
                    # Calculate HR zones
                    hr_zones = calculate_hr_zones_from_streams(streams, athlete_name)
                    
                    # Calculate Pace zones
                    pace_zones = calculate_pace_zones_from_streams(streams, athlete_name)
                    
                    # Prepare zones_df
                    zones_for_activity = []
                    
                    if hr_zones:
                        for zone in hr_zones:
                            zones_for_activity.append({
                                "Type": "Heart Rate",
                                "Zone": zone["zone"],
                                "Zone Name": zone["zone_name"],
                                "Min": zone["min_hr"],
                                "Max": zone["max_hr"],
                                "Time": zone["time_formatted"],
                                "Percentage": f"{zone['percentage']}%",
                            })
                    
                    if pace_zones:
                        for zone in pace_zones:
                            zones_for_activity.append({
                                "Type": "Pace",
                                "Zone": zone["zone"],
                                "Zone Name": zone["zone_name"],
                                "Min": zone.get("min_pace", ""),
                                "Max": zone.get("max_pace", ""),
                                "Time": zone["time_formatted"],
                                "Percentage": f"{zone['percentage']}%",
                            })
                    
                    if zones_for_activity:
                        zones_df = pd.DataFrame(zones_for_activity)
                        
                        # Push using the same function pattern as manual process
                        success, errors = push_zone_data_to_supabase_automation(
                            zones_df, parent_unique_key, activity_row_data
                        )
                        
                        all_zones_pushed += success
                        total_activities_processed += 1
                        
                        if success > 0:
                            print(f"      ✅ Pushed {success} zone records")
                    
                    time.sleep(1)  # Rate limiting
                else:
                    print(f"      ⚠️ No stream data available")
                    
        except Exception as e:
            print(f"  ❌ Error processing {athlete_name}: {e}")
    
    print("\n" + "=" * 70)
    print(f"🏁 ZONE SYNC COMPLETED at {datetime.now()}")
    print(f"📈 Summary:")
    print(f"   • Activities processed: {total_activities_processed}")
    print(f"   • Zone records pushed: {all_zones_pushed}")
    print("=" * 70)


if __name__ == "__main__":
    main()