# data/fetch_strava_automation.py
import os
import json
import requests
from datetime import datetime
import time


class StravaAPI:
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
            return True
        return False

    def get_athlete_profile(self):
        """Get athlete profile"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}/athlete", headers=headers)
        if response.status_code == 200:
            return response.json()
        return None

    def get_activities(self, per_page=200, page=1, after=None):
        """Get activities with pagination"""
        params = {"per_page": per_page, "page": page}
        if after:
            params["after"] = after
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"{self.base_url}/athlete/activities", headers=headers, params=params)
        
        # If token expired, refresh and retry
        if response.status_code == 401:
            if self.refresh_access_token():
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(f"{self.base_url}/athlete/activities", headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        return []

    def get_all_activities(self, days_back=30):
        """Get all activities from last X days"""
        all_activities = []
        page = 1
        
        after_timestamp = int((datetime.now().timestamp() - (days_back * 86400)))
        
        while True:
            activities = self.get_activities(per_page=100, page=page, after=after_timestamp)
            if not activities:
                break
            all_activities.extend(activities)
            page += 1
            time.sleep(0.5)  # Rate limiting
        
        return all_activities


def fetch_all_activities(days_back=30):
    """Fetch activities for all users from environment variables"""
    users_json = os.environ.get("STRAVA_USERS", "{}")
    users = json.loads(users_json)
    
    all_activities = []
    
    for name, creds in users.items():
        print(f"  • Fetching for {name}...")
        try:
            strava = StravaAPI(
                client_id=creds["client_id"],
                client_secret=creds["client_secret"],
                access_token=creds["access_token"],
                refresh_token=creds["refresh_token"],
            )
            
            # Test connection
            profile = strava.get_athlete_profile()
            if not profile:
                print(f"    ⚠️ Could not authenticate for {name}, skipping")
                continue
            
            activities = strava.get_all_activities(days_back=days_back)
            
            for act in activities:
                act["athlete_name"] = name
            
            all_activities.extend(activities)
            print(f"    ✅ Fetched {len(activities)} activities for {name}")
            
        except Exception as e:
            print(f"    ❌ Error fetching for {name}: {e}")
    
    return all_activities