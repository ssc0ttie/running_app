# athlete_metrics.py
import pandas as pd
import streamlit as st

# Hardcoded athlete metrics (you can move to Google Sheets later)
ATHLETE_METRICS = {
    "Scott": {
        "max_hr": 195,
        "threshold_hr": 165,
        "threshold_pace": 5.00,  # 4:30 min/km as decimal (4 + 30/60)
        "pace_5k": 4.00,
        "pace_10k": 4.90,
    },
    "Chona": {
        "max_hr": 195,
        "threshold_hr": 171,
        "threshold_pace": 6.5,  # 5:00 min/km
        "pace_5k": 6.15,
        "pace_10k": 6.8,
    },
}


def get_athlete_metrics(athlete_name):
    """Get metrics for a specific athlete"""
    return ATHLETE_METRICS.get(athlete_name, {})


def get_hr_zones(athlete_name):
    """Calculate HR zones for an athlete"""
    metrics = get_athlete_metrics(athlete_name)
    max_hr = metrics.get("max_hr")

    if not max_hr:
        return None

    zones = [
        {
            "zone": "Z1",
            "name": "Endurance",
            "min": int(max_hr * 0.50),
            "max": int(max_hr * 0.60),
        },
        {
            "zone": "Z2",
            "name": "Moderate",
            "min": int(max_hr * 0.60),
            "max": int(max_hr * 0.70),
        },
        {
            "zone": "Z3",
            "name": "Tempo",
            "min": int(max_hr * 0.70),
            "max": int(max_hr * 0.80),
        },
        {
            "zone": "Z4",
            "name": "Threshold",
            "min": int(max_hr * 0.80),
            "max": int(max_hr * 0.90),
        },
        {"zone": "Z5", "name": "Anaerobic", "min": int(max_hr * 0.90), "max": max_hr},
    ]
    return zones


def get_pace_zones(athlete_name):
    """Calculate pace zones for an athlete based on threshold pace"""
    metrics = get_athlete_metrics(athlete_name)
    threshold_pace = metrics.get("threshold_pace")

    if not threshold_pace:
        return None

    # Threshold pace in seconds per km (for easier calculation)
    threshold_seconds = int(threshold_pace * 60)

    zones = [
        {
            "zone": "Z1",
            "name": "Easy",
            "min": format_pace(threshold_seconds * 1.25),
            "max": "∞",
        },
        {
            "zone": "Z2",
            "name": "Endurance",
            "min": format_pace(threshold_seconds * 1.15),
            "max": format_pace(threshold_seconds * 1.25),
        },
        {
            "zone": "Z3",
            "name": "Tempo",
            "min": format_pace(threshold_seconds * 1.05),
            "max": format_pace(threshold_seconds * 1.15),
        },
        {
            "zone": "Z4",
            "name": "Threshold",
            "min": format_pace(threshold_seconds * 0.95),
            "max": format_pace(threshold_seconds * 1.05),
        },
        {
            "zone": "Z5",
            "name": "VO2 Max",
            "min": "0:00",
            "max": format_pace(threshold_seconds * 0.95),
        },
    ]
    return zones


def format_pace(seconds):
    """Convert seconds to mm:ss format"""
    minutes = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{minutes}:{secs:02d}"


# For backward compatibility with existing zone processor
def get_athlete_max_hr(athlete_name):
    metrics = get_athlete_metrics(athlete_name)
    return metrics.get("max_hr")


def get_athlete_threshold_pace(athlete_name):
    metrics = get_athlete_metrics(athlete_name)
    return metrics.get("threshold_pace")
