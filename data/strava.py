import requests
import pandas as pd
import json
from datetime import datetime


class StravaAPI:
    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://www.strava.com/api/v3"

    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
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
            self.refresh_token = tokens["refresh_token"]  # Update refresh token
            print("Token refreshed successfully")
            return True
        else:
            print("Error refreshing token:", response.text)
            return False

    def make_authenticated_request(self, endpoint, params=None):
        """Make API request with automatic token refresh"""
        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"{self.base_url}{endpoint}"

        response = requests.get(url, headers=headers, params=params)

        # If token expired, refresh and try again
        if response.status_code == 401:
            print("Token expired, refreshing...")
            if self.refresh_access_token():
                headers = {"Authorization": f"Bearer {self.access_token}"}
                response = requests.get(url, headers=headers, params=params)
            else:
                return None

        return response

    def get_athlete_profile(self):
        """Get your athlete profile"""
        response = self.make_authenticated_request("/athlete")
        return response.json() if response else None

    def get_activities(self, per_page=200, page=1, before=None, after=None):
        """Get your activities with pagination"""
        params = {"per_page": per_page, "page": page}

        if before:
            params["before"] = before
        if after:
            params["after"] = after

        response = self.make_authenticated_request("/athlete/activities", params)
        return response.json() if response else None

    def get_activity_detail(self, activity_id):
        """Get detailed information for a specific activity"""
        response = self.make_authenticated_request(f"/activities/{activity_id}")
        return response.json() if response else None

    def get_all_activities(self, days_back=365):
        """Get all activities from the last X days"""
        all_activities = []
        page = 1

        # FIX: Convert to Unix timestamp properly
        after_date = datetime.now() - pd.Timedelta(days=days_back)
        after_timestamp = int(after_date.timestamp())  # This is correct

        while True:
            activities = self.get_activities(
                per_page=100, page=page, after=after_timestamp
            )
            if not activities:
                print("No activities returned or API error")
                break

            if len(activities) == 0:
                print(f"Page {page}: Empty activities list received")
                break

            all_activities.extend(activities)
            print(f"Fetched page {page}: {len(activities)} activities")
            page += 1

            # Rate limiting
            import time

            time.sleep(1)

        return all_activities
