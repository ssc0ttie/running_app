# scripts/keep_alive.py
import os
import time
from playwright.sync_api import Playwright, sync_playwright

# The URL of your LIVE Streamlit app
STREAMLIT_URL = os.environ.get("STREAMLIT_APP_URL", "https://stillhere.streamlit.app/")


def run(playwright: Playwright):
    # 1. Launch a hidden browser (headless mode)
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    print(f"🌐 Visiting {STREAMLIT_URL}...")

    # 2. Navigate to the app
    page.goto(STREAMLIT_URL)
    page.wait_for_timeout(5000)  # Wait 5 seconds for the page to settle

    # 3. Look for the sleep button and click it if found
    wake_up_button = page.get_by_role("button", name="Yes, get this app back up!")
    if wake_up_button.count() > 0:
        print("😴 App was asleep. Clicking the wake-up button...")
        wake_up_button.click()
        # Wait for the app to fully restart
        page.wait_for_timeout(60000)
        print("✅ App should be awake now.")
    else:
        # 4. If no button, the app is already awake.
        print("✅ App is already awake. Nothing to do.")

    browser.close()


def main():
    print("🚀 Starting the keep-awake script...")
    with sync_playwright() as playwright:
        run(playwright)
    print("🏁 Script finished.")


if __name__ == "__main__":
    main()
