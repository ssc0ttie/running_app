#!/usr/bin/env python3
"""
Strava Zone Sync Script for GitHub Actions
Uses the SAME working functions as the manual Streamlit UI
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

# IMPORT YOUR WORKING MODULES (NOT REIMPLEMENTED!)
from data import strava as strav
from data.zoneprocessor import calculate_hr_zones_from_streams, calculate_pace_zones_from_streams
from data.push_supa import push_zone_data_to_supabase
from data.athlete_metrics import get_athlete_max_hr, get_athlete_threshold_pace


def init_supabase_automation():
    """Initialize Supabase client for GitHub Actions"""
    from supabase import create_client
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials missing")
        return None
    
    return create_client(supabase_url, supabase_key)


def fetch_activities_from_supabase(athlete_name, supabase_url, supabase_key, limit=100):
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
    
    days_back = int(os.environ.get("DAYS_BACK", "30"))
    print(f"📅 Analyzing activities from the last {days_back} days")
    
    # Get users from environment
    users_json = os.environ.get("STRAVA_USERS", "{}")
    users = json.loads(users_json)
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Supabase credentials missing")
        sys.exit(1)
    
    # =========================================================
    # STEP 1: Create ONE StravaAPI client per athlete (like your UI)
    # =========================================================
    athlete_clients = {}
    for name, creds in users.items():
        athlete_clients[name] = strav.StravaAPI(
            client_id=creds["client_id"],
            client_secret=creds["client_secret"],
            access_token=creds["access_token"],
            refresh_token=creds["refresh_token"],
        )
        print(f"✅ Created client for {name}")
    
    all_zones_pushed = 0
    total_activities_processed = 0
    
    for athlete_name, creds in users.items():
        print(f"\n👤 Processing {athlete_name}...")
        
        try:
            # Reuse the existing client (like your UI)
            strava = athlete_clients.get(athlete_name)
            if not strava:
                print(f"  ⚠️ No client found for {athlete_name}, skipping")
                continue
            
            # Verify connection using your working method
            profile = strava.get_athlete_profile()
            if not profile:
                print(f"  ⚠️ Could not authenticate for {athlete_name}, skipping")
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
                raw_hr = act.get('HR (bpm)', 0)
                
                # IMPORTANT: Use ROUNDING (same as your UI)
                try:
                    avg_hr = int(round(float(raw_hr)))
                except (ValueError, TypeError):
                    avg_hr = 0
                
                # Only process activities that are likely to have streams
                if act_type not in ["Run", "Ride", "Walk"]:
                    continue
                
                # Build parent_unique_key (same format as UI)
                parent_unique_key = f"{start_date}|{athlete_name}|{act_type}|{avg_hr}"
                
                activity_row_data = {
                    "Date": start_date,
                    "Member Name": athlete_name,
                    "Activity": act_type,
                    "Avg_HR": avg_hr
                }
                
                print(f"    📈 Processing {strava_id}: {start_date} | {act_type} | HR={avg_hr}")
                
                # Use your working make_authenticated_request method
                response = strava.make_authenticated_request(
                    f"/activities/{strava_id}/streams",
                    params={"keys": "time,heartrate,velocity_smooth", "key_by_type": "true"}
                )
                
                if response and response.status_code == 200:
                    streams_data = response.json()
                    
                    # Convert to expected format (same as UI)
                    class StreamWrapper:
                        def __init__(self, data):
                            self.data = data
                    
                    streams = {}
                    if "heartrate" in streams_data:
                        streams["heartrate"] = StreamWrapper(streams_data["heartrate"]["data"])
                    if "time" in streams_data:
                        streams["time"] = StreamWrapper(streams_data["time"]["data"])
                    if "velocity_smooth" in streams_data:
                        streams["velocity_smooth"] = StreamWrapper(streams_data["velocity_smooth"]["data"])
                    
                    if streams and 'heartrate' in streams:
                        # Calculate zones using your working functions
                        hr_zones = calculate_hr_zones_from_streams(streams, athlete_name=athlete_name)
                        pace_zones = calculate_pace_zones_from_streams(streams, athlete_name=athlete_name)
                        
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
                            
                            # Use YOUR WORKING push function
                            success, errors = push_zone_data_to_supabase(
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
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print(f"🏁 ZONE SYNC COMPLETED at {datetime.now()}")
    print(f"📈 Summary:")
    print(f"   • Activities processed: {total_activities_processed}")
    print(f"   • Zone records pushed: {all_zones_pushed}")
    print("=" * 70)


if __name__ == "__main__":
    main()