#!/usr/bin/env python3
"""
Strava Zone Sync Script for GitHub Actions
Calculates and pushes HR and Pace zone distributions to Supabase
Runs weekly to avoid excessive API calls
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
            print(f"    ❌ Stream fetch failed: {response.status_code}")
            return None
    
    def get_athlete_profile(self):
        """Get athlete profile to verify connection"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}/athlete", headers=headers)
        
        # If token expired, refresh and retry
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


def get_athlete_metrics():
    """Get athlete metrics from environment or hardcoded values"""
    # Try to get from environment first
    metrics_json = os.environ.get("ATHLETE_METRICS", "{}")
    if metrics_json and metrics_json != "{}":
        return json.loads(metrics_json)
    
    # Fallback to hardcoded metrics (update with your athletes)
    return {
        "Scott": {
            "max_hr": 195,
            "threshold_hr": 165,
            "threshold_pace": 4.30,
        },
        "Chona": {
            "max_hr": 175,
            "threshold_hr": 155,
            "threshold_pace": 5.00,
        },
        "Lead": {
            "max_hr": 180,
            "threshold_hr": 160,
            "threshold_pace": 5.00,
        },
        "Fraulein": {
            "max_hr": 178,
            "threshold_hr": 158,
            "threshold_pace": 5.15,
        },
        "Aiza": {
            "max_hr": 176,
            "threshold_hr": 156,
            "threshold_pace": 5.30,
        },
    }


def get_athlete_max_hr(athlete_name):
    """Get athlete's max HR"""
    metrics = get_athlete_metrics()
    return metrics.get(athlete_name, {}).get("max_hr")


def get_athlete_threshold_pace(athlete_name):
    """Get athlete's threshold pace"""
    metrics = get_athlete_metrics()
    pace = metrics.get(athlete_name, {}).get("threshold_pace")
    # Convert string like "4:30" to float if needed
    if isinstance(pace, str) and ":" in pace:
        parts = pace.split(":")
        return int(parts[0]) + int(parts[1]) / 60
    return pace


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
    
    # Calculate time differences
    time_diffs = [times[i + 1] - times[i] for i in range(len(times) - 1)]
    
    # Get max HR from athlete metrics
    max_hr = get_athlete_max_hr(athlete_name)
    
    if max_hr is None:
        # Fall back to activity max HR
        max_hr = max(heartrates) if heartrates else 180
        print(f"    ⚠️ Using activity max HR ({max_hr}) for {athlete_name}")
    
    # Define 5 zones
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
    
    # Calculate time in each zone
    total_time = 0
    for i, hr in enumerate(heartrates[:-1]):
        for zone in zones:
            if zone["min_hr"] <= hr < zone["max_hr"]:
                zone["time_seconds"] += time_diffs[i]
                total_time += time_diffs[i]
                break
    
    # Calculate percentages
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
    
    # Convert velocity to pace (min/km)
    paces = []
    for v in velocities[:-1]:
        if v > 0:
            pace_min_km = (1 / v) * (1000 / 60)
            paces.append(pace_min_km)
        else:
            paces.append(None)
    
    # Get threshold pace from athlete metrics
    threshold_pace = get_athlete_threshold_pace(athlete_name)
    
    if threshold_pace and threshold_pace > 0:
        t = threshold_pace
        zone_definitions = [
            {"zone": "Z1", "name": "Easy", "min_pace": t * 1.25, "max_pace": float("inf")},
            {"zone": "Z2", "name": "Endurance", "min_pace": t * 1.15, "max_pace": t * 1.25},
            {"zone": "Z3", "name": "Tempo", "min_pace": t * 1.05, "max_pace": t * 1.15},
            {"zone": "Z4", "name": "Threshold", "min_pace": t * 0.95, "max_pace": t * 1.05},
            {"zone": "Z5", "name": "VO2 Max", "min_pace": 0, "max_pace": t * 0.95},
        ]
    else:
        # Fallback zones
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


def push_zones_to_supabase(zones_df):
    """Push zone data to Supabase"""
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials missing")
        return 0, len(zones_df)
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    # Convert DataFrame to records
    records = zones_df.to_dict(orient='records')
    
    # Use upsert to avoid duplicates
    url = f"{supabase_url}/rest/v1/zones"
    
    try:
        response = requests.post(url, headers=headers, json=records)
        
        if response.status_code in [200, 201]:
            print(f"  ✅ Pushed {len(records)} zone records")
            return len(records), 0
        else:
            print(f"  ❌ Push failed: {response.status_code} - {response.text}")
            return 0, len(records)
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return 0, len(records)


def main():
    print("=" * 70)
    print(f"🚀 STRAVA ZONE SYNC - PRODUCTION")
    print(f"📍 Started at: {datetime.now()}")
    print("=" * 70)
    
    # Get days back (default 90 for zone calculations)
    days_back = int(os.environ.get("DAYS_BACK", "2"))
    print(f"📅 Analyzing activities from the last {days_back} days")
    
    # Get users from environment
    users_json = os.environ.get("STRAVA_USERS", "{}")
    users = json.loads(users_json)
    
    all_zones = []
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
            
            # Fetch athlete profile to verify connection
            profile = strava.get_athlete_profile()
            if profile is None:
                print(f"  ⚠️ Could not connect for {athlete_name}, skipping")
                continue
            
            print(f"  ✅ Connected as {profile.get('firstname', athlete_name)}")
            
            # Query activities from Supabase
            supabase_url = os.environ.get("url")
            supabase_key = os.environ.get("key")
            
            if supabase_url and supabase_key:
                headers = {
                    "apikey": supabase_key,
                    "Authorization": f"Bearer {supabase_key}"
                }
                
                # Get activities from Supabase - use correct column names
                # Fix: Use correct column names with proper quoting
                activities_url = f"{supabase_url}/rest/v1/activities?select=id,\"Member Name\",\"Date_of_Activity\",\"HR (bpm)\"&\"Member Name\"=eq.{athlete_name}&order=Date_of_Activity.desc&limit=50"
                response = requests.get(activities_url, headers=headers)
                
                if response.status_code == 200:
                    activities = response.json()
                    print(f"  📊 Found {len(activities)} activities in Supabase")
                    
                    for act in activities:
                        # Get Strava activity ID (try both possible column names)
                        strava_id = act.get('id')
                        if not strava_id:
                            continue
                        
                        # Get average HR for this activity
                        avg_hr = act.get('HR (bpm)', 0)
                        if avg_hr is None:
                            avg_hr = 0
                        
                        print(f"    📈 Processing activity {strava_id} (Avg HR: {avg_hr})...")
                        
                        # Fetch streams
                        streams = strava.get_activity_streams(strava_id)
                        
                        if streams and 'heartrate' in streams:
                            # Calculate HR zones
                            hr_zones = calculate_hr_zones_from_streams(streams, athlete_name)
                            
                            if hr_zones:
                                start_date = act.get('Date_of_Activity', '').split('T')[0] if act.get('Date_of_Activity') else ''
                                
                                for zone in hr_zones:
                                    all_zones.append({
                                        "Parent_UniqueKey": f"{start_date}|{athlete_name}|Run|{int(avg_hr)}",
                                        "Zone_UniqueKey": f"{start_date}|{athlete_name}|Run|{int(avg_hr)}_HeartRate_{zone['zone']}",
                                        "Date_of_Activity": start_date,
                                        "Member Name": athlete_name,
                                        "Activity": "Run",
                                        "Zone_Type": "Heart Rate",
                                        "Zone": zone["zone"],
                                        "Zone_Name": zone["zone_name"],
                                        "Min_Value": zone["min_hr"],
                                        "Max_Value": zone["max_hr"],
                                        "Time_In_Zone": zone["time_formatted"],
                                        "Percentage": f"{zone['percentage']}%",
                                    })
                            
                            # Calculate Pace zones
                            if 'velocity_smooth' in streams:
                                pace_zones = calculate_pace_zones_from_streams(streams, athlete_name)
                                
                                if pace_zones:
                                    start_date = act.get('Date_of_Activity', '').split('T')[0] if act.get('Date_of_Activity') else ''
                                    
                                    for zone in pace_zones:
                                        all_zones.append({
                                            "Parent_UniqueKey": f"{start_date}|{athlete_name}|Run|{int(avg_hr)}",
                                            "Zone_UniqueKey": f"{start_date}|{athlete_name}|Run|{int(avg_hr)}_Pace_{zone['zone']}",
                                            "Date_of_Activity": start_date,
                                            "Member Name": athlete_name,
                                            "Activity": "Run",
                                            "Zone_Type": "Pace",
                                            "Zone": zone["zone"],
                                            "Zone_Name": zone["zone_name"],
                                            "Min_Value": zone.get("min_pace", ""),
                                            "Max_Value": zone.get("max_pace", ""),
                                            "Time_In_Zone": zone["time_formatted"],
                                            "Percentage": f"{zone['percentage']}%",
                                        })
                            
                            total_activities_processed += 1
                            time.sleep(1)  # Rate limiting
                        else:
                            print(f"      ⚠️ No stream data for activity {strava_id}")
                else:
                    print(f"  ❌ Failed to fetch activities: {response.status_code}")
                    print(f"     Response: {response.text[:200]}")
            else:
                print("  ❌ Supabase credentials not available")
            
        except Exception as e:
            print(f"  ❌ Error processing {athlete_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Push zones to Supabase
    if all_zones:
        print(f"\n📤 Pushing {len(all_zones)} zone records to Supabase...")
        zones_df = pd.DataFrame(all_zones)
        success, errors = push_zones_to_supabase(zones_df)
        
        print("\n" + "=" * 70)
        print(f"🏁 ZONE SYNC COMPLETED at {datetime.now()}")
        print(f"📈 Summary:")
        print(f"   • Activities processed: {total_activities_processed}")
        print(f"   • Zone records created: {len(all_zones)}")
        print(f"   • Successfully pushed: {success}")
        print(f"   • Errors: {errors}")
        print("=" * 70)
    else:
        print("\n⚠️ No zone data generated")


if __name__ == "__main__":
    main()