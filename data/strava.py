import requests
import pandas as pd
import json
from datetime import datetime

# In strava.py
import time
from data.token_storage import get_stored_tokens, update_stored_tokens


### ORIGINAL SCRIPT ##### ############## ############## ############## ############## ############## ##############
class StravaAPI:
    def __init__(self, client_id, client_secret, access_token=None, refresh_token=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.base_url = "https://www.strava.com/api/v3"

    ############## ############## ############## ############## ############## ##############
    # class StravaAPI:
    #     def __init__(
    #         self,
    #         athlete_name,
    #         client_id=None,
    #         client_secret=None,
    #         access_token=None,
    #         refresh_token=None,
    #     ):
    #         self.athlete_name = athlete_name
    #         self.client_id = client_id
    #         self.client_secret = client_secret
    # #         self.base_url = "https://www.strava.com/api/v3"

    #         # Try to load from Google Sheets first
    #         stored_tokens = get_stored_tokens(athlete_name)

    #         if stored_tokens:
    #             self.access_token = stored_tokens["access_token"]
    #             self.refresh_token = stored_tokens["refresh_token"]
    #             self.expires_at = stored_tokens.get("expires_at")
    #             # Use stored client credentials if not provided
    #             if not self.client_id:
    #                 self.client_id = stored_tokens.get("client_id")
    #             if not self.client_secret:
    #                 self.client_secret = stored_tokens.get("client_secret")
    #         else:
    #             self.access_token = access_token
    #             self.refresh_token = refresh_token
    #             self.expires_at = None

    def refresh_access_token_original(self):
        ### ORIGINAL SCRIPT ############## ############## ############## ############## ############## ############## ##############

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

        ############# ############## ############## ############## ############## ##############

        response = requests.post(url, data=payload)

        # if response.status_code == 200:
        #     tokens = response.json()
        #     self.access_token = tokens["access_token"]
        #     self.expires_at = tokens.get("expires_at")

        #     # Save to Google Sheets (persistent storage)
        #     update_stored_tokens(
        #         self.athlete_name,
        #         tokens["access_token"],
        #         tokens.get("refresh_token", self.refresh_token),  # Use new if provided
        #         tokens.get("expires_at"),
        #     )

        #     # Also update refresh_token if Strava issued a new one
        #     if "refresh_token" in tokens:
        #         self.refresh_token = tokens["refresh_token"]

        #     print(f"✅ Token refreshed and saved for {self.athlete_name}")
        #     return True
        # else:
        #     print(f"❌ Refresh failed for {self.athlete_name}: {response.text}")
        #     return False

    #### ORIGINAL SCRIPT ############## ############## ############## ############## ############## ############## ##############

    def refresh_access_token(self):
        """Refresh the access token using refresh token (matching Postman format)"""
        url = "https://www.strava.com/oauth/token"

        # Use URL parameters (query string) instead of form data
        params = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "refresh_token": self.refresh_token,
            "grant_type": "refresh_token",
        }

        response = requests.post(url, params=params)  # Note: params=, not data=

        if response.status_code == 200:
            tokens = response.json()
            self.access_token = tokens["access_token"]
            self.refresh_token = tokens.get("refresh_token", self.refresh_token)
            print(f"✅ Token refreshed. Scope: {tokens.get('scope')}")
            return True
        else:
            print(f"❌ Refresh failed: {response.status_code} - {response.text}")
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

    #### ############## ############## ############## ############## ############## ############## ##############

    # def make_authenticated_request(self, endpoint, params=None):
    #     """Make API request with auto-refresh and token saving"""
    #     # Check if token is expired (add 60 second buffer)
    #     if self.expires_at and time.time() + 60 >= self.expires_at:
    #         print(f"Token expired for {self.athlete_name}, refreshing...")
    #         self.refresh_access_token()

    #     headers = {"Authorization": f"Bearer {self.access_token}"}
    #     url = f"{self.base_url}{endpoint}"

    #     response = requests.get(url, headers=headers, params=params)

    #     if response.status_code == 401:
    #         print(f"Token invalid for {self.athlete_name}, refreshing...")
    #         if self.refresh_access_token():
    #             headers = {"Authorization": f"Bearer {self.access_token}"}
    #             response = requests.get(url, headers=headers, params=params)

    #     return response

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
